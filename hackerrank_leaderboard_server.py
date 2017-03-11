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
    InvalidVersionException, HackerrankProxyNotReadyException,
    StubNotRegisteredException
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
            for username, completed in self.iterate_data(retries=retries+1, e=e):
                yield username, int(completed)

        self.status = HackerrankProxyStatus(
            status=Status.OK, statusMessage="Succesfully fetched data with {} retries".format(retries))


class HackerrankLeaderboardServerHandler(object):

    def __init__(self, proxy_factory, update_frequency=30):
        self.update_frequency = update_frequency
        self.proxy_factory = proxy_factory
        self.leaderboard_diffs = {}
        self.machines = {}
        self.proxy_machine_thread = threading.Thread(target=self.loopProxyMachine)
        self.proxy_machine_thread.start()

    def registerLeaderboard(self, stub, username, password):
        if stub in self.machines:
            return

        url = "https://www.hackerrank.com/contests/{}/leaderboard".format(stub)
        proxy = self.proxy_factory(url, username, password)
        proxy_machine = HackerrankLeaderboardProxyMachine(proxy)

        self.leaderboard_diffs[stub] = [{}]
        self.machines[stub] = proxy_machine

    def unregisterLeaderboard(self, stub):
        self.assertStubValid(stub)

        del self.machines[stub]
        del self.leaderboard_diffs[stub]

    def loopProxyMachine(self):
        while True:
            for stub, proxy_machine in self.machines.items():
                new_diffs = {}
                for username, completed in self.machines[stub].iterate_data():
                    latest_user_completed = self.leaderboard_diffs[stub][-1].setdefault(username, 0)
                    if completed > latest_user_completed:
                        new_diffs[username] = completed - latest_user_completed

                if len(new_diffs) > 0:
                    logger.info(new_diffs)
                    self.leaderboard_diffs[stub].append(new_diffs)

            time.sleep(self.update_frequency)

    def coagulate_diffs(self, stub, start_version):
        # Combine the latest diffs
        diffs = {}
        newest_version = len(self.leaderboard_diffs[stub]) - 1
        for i in range(start_version + 1, newest_version + 1):
            version_entry = self.leaderboard_diffs[stub][i]
            for username in version_entry:
                problems = version_entry[username]
                current_diff = diffs.setdefault(username, LeaderboardDiff(username=username, additional_problems_completed=0))
                new_diff = LeaderboardDiff(username=username, additional_problems_completed=current_diff.additional_problems_completed + problems)
                diffs[username] = new_diff

        return diffs.values(), newest_version

    def getLeaderboardDiff(self, stub, current_version):
        self.assertStubValid(stub)

        if self.machines[stub].status.status != Status.OK:
            raise HackerrankProxyNotReadyException(proxy_status=self.machines[stub].status)

        latest_version = len(self.leaderboard_diffs[stub]) - 1
        if latest_version < current_version:
            raise InvalidVersionException(server_latest=latest_version)

        diff_list, version = self.coagulate_diffs(stub, current_version)
        return LeaderboardDiffList(difflist=diff_list, version=version)

    def assertStubValid(self, stub):
        if stub not in self.machines or stub not in self.leaderboard_diffs:
            raise StubNotRegisteredException(stub)


@click.command()
@click.option('--port', type=int, default=9876)
@click.option('--updateinterval', type=int, default=30)
def main(port, updateinterval):
    handler = HackerrankLeaderboardServerHandler(HackerrankSeleniumStatProxy, updateinterval)

    processor = HackerrankLeaderboardServer.Processor(handler)
    transport = TSocket.TServerSocket(port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
    server.serve()

if __name__ == '__main__':
    main()
