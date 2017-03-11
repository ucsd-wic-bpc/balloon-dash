namespace py hackerrank_leaderboard

struct LeaderboardDiff {
  1: string username;
  2: i32 additional_problems_completed;
}


struct LeaderboardDiffList {
  1: list<LeaderboardDiff> difflist;
  2: i32 version;
}

enum Status {
  STARTING,
  OK,
  DEAD
}

struct HackerrankProxyStatus {
  1: Status status;
  2: string statusMessage;
}

exception HackerrankProxyNotReadyException {
  1: HackerrankProxyStatus proxy_status;
}

exception InvalidVersionException {
  1: i32 server_latest;
}

exception StubNotRegisteredException {
  1: string stub_name;
}

service HackerrankLeaderboardServer {
  void registerLeaderboard(1: string stub, 2: string username, 3: string password);
  LeaderboardDiffList getLeaderboardDiff(1: string stub, 2: i32 version) throws (1: HackerrankProxyNotReadyException notready,
                                                                                 2: StubNotRegisteredException snre);
  void unregisterLeaderboard(1: string stub) throws (1: StubNotRegisteredException snre);
}
