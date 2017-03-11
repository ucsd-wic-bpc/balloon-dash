import sys
sys.path.append('gen-py')

import click

from thrift import Thrift
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from competition_server_service.ttypes import (
    NotWatchingCompetitionException, LeaderboardServerNotReadyException, User
)
from hackerrank_leaderboard.ttypes import (
    HackerrankProxyNotReadyException
)

from hackerrank_leaderboard import HackerrankLeaderboardServer
from competition_server_service import CompetitionServer


class AlertCollection(object):
    def __init__(self):
        self.version = 0
        self.users = {}


class CompetitionServerHandler(object):

    def __init__(self, leaderboard_server_url, leaderboard_server_port):
        self.competitions = {}  # stub: competition
        self.alerts = {}

        self.leaderboard_transport = TSocket.TSocket(leaderboard_server_url,
                                                     leaderboard_server_port)
        protocol = TBinaryProtocol.TBinaryProtocol(self.leaderboard_transport)
        self.leaderboard_client = HackerrankLeaderboardServer.Client(protocol)

    def isWatching(self, stub):
        return stub in self.competitions

    def watchCompetition(self, competition):
        if competition.stub in self.competitions:
            return

        try:
            self.leaderboard_transport.open()
            self.leaderboard_client.registerLeaderboard(
                competition.stub, competition.username, competition.password
            )
            self.competitions[competition.stub] = competition
            self.alerts[competition.stub] = AlertCollection()
        except HackerrankProxyNotReadyException as e:
            raise LeaderboardServerNotReadyException(message=e.proxy_status.statusMessage)
        finally:
            self.leaderboard_transport.close()

    def getDefaultUser(self, stub, username):
        return User(
            username=username,
            completed_problems=0,
            acked_alerts=0,
            pending_alerts=0,
            category=self.competitions[stub].categories.get(username, "Uncategorized") or "Uncategorized",
            tags=self.competitions[stub].tags.get(username, [])
        )

    def getUpdatedUserList(self, stub):
        if stub not in self.competitions:
            raise NotWatchingCompetitionException(stub=stub)

        # Now connect to leaderboard server, get completed problems for all usernames
        competition_settings = self.competitions[stub]
        current_alerts = self.alerts[stub]

        try:
            self.leaderboard_transport.open()
            difflist = self.leaderboard_client.getLeaderboardDiff(stub, current_alerts.version)
        except HackerrankProxyNotReadyException as e:
            raise LeaderboardServerNotReadyException(message=e.proxy_status.statusMessage)
        finally:
            self.leaderboard_transport.close()

        for diff in difflist.difflist:
            current_user = current_alerts.users.setdefault(diff.username, self.getDefaultUser(stub, diff.username))
            current_user.completed_problems += diff.additional_problems_completed

        current_alerts.version = difflist.version

        all_users = []
        for username, user in current_alerts.users.items():
            all_alerts = len([alert for alert in competition_settings.alert_thresholds
                              if alert <= user.completed_problems])
            user.pending_alerts = all_alerts - user.acked_alerts
            all_users.append(user)

        return all_users

    def ackAlerts(self, stub, acks):
        if stub not in self.competitions:
            raise NotWatchingCompetitionException(stub=stub)

        for username, ack_count in acks.items():
            self.alerts[stub].users[username].acked_alerts += ack_count

    def updateCategories(self, stub, categories):
        if stub not in self.competitions:
            raise NotWatchingCompetitionException(stub=stub)

        for username, category in categories.items():
            self.alerts[stub].users[username].category = category

    def updateTags(self, stub, tags):
        if stub not in self.competitions:
            raise NotWatchingCompetitionException(stub=stub)

        for username, tags in tags.items():
            self.alerts[stub].users[username].tags = tags

@click.command()
@click.option('--port', type=int, required=True)
@click.option('--leaderboardaddr', type=str, required=True)
@click.option('--leaderboardport', type=int, required=True)
def main(port, leaderboardaddr, leaderboardport):
    handler = CompetitionServerHandler(leaderboardaddr, leaderboardport)
    processor = CompetitionServer.Processor(handler)
    transport = TSocket.TServerSocket(port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
    server.serve()


if __name__ == '__main__':
    main()
