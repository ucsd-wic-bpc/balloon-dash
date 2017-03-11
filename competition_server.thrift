namespace py competition_server_service

struct CompetitionSettings {
  1: list<i32> alert_thresholds;
  2: string stub;
  3: string username;
  4: string password;

  // Optionally, map usernames to categories and tags. Useful for displaying
  // the data in categorical columns
  5: map<string, string> categories;
  6: map<string, list<string>> tags;
}

struct User {
  1: string username;
  2: i32 completed_problems;
  3: i32 acked_alerts;
  4: i32 pending_alerts;
  5: string category;
  6: list<string> tags;
}

exception NotWatchingCompetitionException {
  1: string stub;
}

exception LeaderboardServerNotReadyException {
  1: string message;
}

service CompetitionServer {
  void watchCompetition(1: CompetitionSettings settings);
  list<User> getUpdatedUserList(1: string stub) throws (1: NotWatchingCompetitionException notwatching,
                                                        2: LeaderboardServerNotReadyException nre);
  void ackAlerts(1: string stub, 2: map<string, i32> acked_alerts);
  void updateCategories(1: string stub, 2: map<string, string> categories) throws (1: NotWatchingCompetitionException notwatching);
  void updateTags(1: string stub, 2: map<string, list<string>> tags) throws (1: NotWatchingCompetitionException notwatching);
  bool isWatching(1: string stub);
}
