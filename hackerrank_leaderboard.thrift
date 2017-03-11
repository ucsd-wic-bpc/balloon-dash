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

service HackerrankLeaderboardServer {
  LeaderboardDiffList getLeaderboardDiff(1: i32 current_version) throws (1: HackerrankProxyNotReadyException notready);
  HackerrankProxyStatus getProxyStatus();
}
