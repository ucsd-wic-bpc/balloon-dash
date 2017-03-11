import sys
sys.path.append('gen-py')

import click
import threading
import time
import logging

from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from hackerrank_leaderboard import HackerrankLeaderboardServer
from hackerrank_leaderboard.ttypes import (
    HackerrankProxyStatus, Status, LeaderboardDiff, LeaderboardDiffList, 
    InvalidVersionException, HackerrankProxyNotReadyException
)
from balloonlib.hackerrank_selenium_stat_proxy import HackerrankSeleniumStatProxy

logging.basicConfig(level=getattr(logging, 'INFO'))
logger = logging.getLogger('leaderboard_server')

class HackerrankLeaderboardProxyMachine(object):

    def __init__(self, hackerrank_proxy, retry_limit=5):
        self.retry_limit = retry_limit
        self.hackerrank_proxy = hackerrank_proxy

        # Should be STARTING until a full complete iteration
        self.status = HackerrankProxyStatus(
            status=Status.STARTING, statusMessage="Starting up"
        )

    def iterate_data(self, retries=0, e=None):
        if self.status.status == Status.DEAD:
            return

        if retries >= self.retry_limit:
            self.status = HackerrankProxyStatus(
                status=Status.DEAD, statusMessage=str(e)
            )
            return

        try:
            for username, pos, completed in self.hackerrank_proxy.iterate_updated_contestant_data():
                yield username, int(completed)
        except Exception as e:
            for username, completed in self.iterate_data(retries = retries+1, e=e):
                yield username, int(completed)

        self.status = HackerrankProxyStatus(
            status=Status.OK, statusMessage="Succesfully fetched data with {} retries".format(retries))


class HackerrankLeaderboardServerHandler(object):

    def __init__(self, hackerrank_proxy, update_frequency=30):
        self.update_frequency = update_frequency
        self.leaderboard_diffs = [{}]
        self.proxy_machine = HackerrankLeaderboardProxyMachine(hackerrank_proxy)
        self.proxy_machine_thread = threading.Thread(target=self.loopProxyMachine)
        self.proxy_machine_thread.start()

    def loopProxyMachine(self):
        while True:
            new_diffs = {}
            for username, completed in self.proxy_machine.iterate_data():
                latest_user_completed = self.leaderboard_diffs[-1].setdefault(username, 0)
                if completed > latest_user_completed:
                    new_diffs[username] = completed - latest_user_completed

            if len(new_diffs) > 0:
                logger.info(new_diffs)
                self.leaderboard_diffs.append(new_diffs)

            time.sleep(self.update_frequency)

    def coagulate_diffs(self, start_version):
        # Combine the latest diffs
        diffs = {}
        newest_version = len(self.leaderboard_diffs) - 1
        for i in range(start_version + 1, newest_version + 1):
            version_entry = self.leaderboard_diffs[i]
            for username in version_entry:
                problems = version_entry[username]
                current_diff = diffs.setdefault(username, LeaderboardDiff(username=username, additional_problems_completed=0))
                new_diff = LeaderboardDiff(username=username, additional_problems_completed=current_diff.additional_problems_completed + problems)
                diffs[username] = new_diff

        return diffs.values(), newest_version

    def getLeaderboardDiff(self, current_version):
        if self.proxy_machine.status.status != Status.OK:
            raise HackerrankProxyNotReadyException(proxy_status=self.proxy_machine.status)

        latest_version = len(self.leaderboard_diffs) - 1
        if latest_version < current_version:
            raise InvalidVersionException(server_latest=latest_version)

        diff_list, version = self.coagulate_diffs(current_version)
        return LeaderboardDiffList(difflist=diff_list, version=version)


@click.command()
@click.option('--port', type=int, default=9876)
@click.option('--leaderboardurl', type=str, required=True)
@click.option('--username', type=str, required=True)
@click.option('--password', type=str, required=True)
@click.option('--updateinterval', type=int, default=30)
def main(port, leaderboardurl, username, password, updateinterval):
    proxy = HackerrankSeleniumStatProxy(leaderboardurl, username, password)
    handler = HackerrankLeaderboardServerHandler(proxy, updateinterval)

    processor = HackerrankLeaderboardServer.Processor(handler)
    transport = TSocket.TServerSocket(port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
    server.serve()

if __name__ == '__main__':
    main()
