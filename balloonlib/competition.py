###############################################################################
# competition.py
# ucsd-wic-bpc
# 20 November 2016
#
# Classes and utilities to manage a competition, which is a collection of 
# contestants solving problems which are scraped.
###############################################################################

class Competition(object):

    def __init__(self, contestant_collection, stat_proxy, competition_config):

        # The collection of contestants is the only state-ful thing
        self.contestants = contestant_collection
        self.stat_proxy = stat_proxy
        self.configuration = competition_config
        self.balloon_generator = None

    def refresh_contestants_completed(self):
        bad_usernames = []
        for updated_stats in self.stat_proxy.iterate_updated_contestant_data():
            username, position, completed_problems = updated_stats
            username = username.lower()

            if not username in self.contestants:
                bad_usernames.append(username)
                continue

            contestant = self.contestants[username]
            contestant.completed_problems = completed_problems

        return bad_usernames

    def get_needed_balloon_count_for_contestant(self, contestant):
        balloon_problem_counts = self.configuration.balloon_problem_counts
        needed_balloons = len([count for count in balloon_problem_counts
                               if count <= contestant.completed_problems])

        if contestant.current_balloons < needed_balloons:
            return needed_balloons - contestant.current_balloons
        else:
            return 0

    def iterate_needed_ballons(self):
        for _, contestant in self.contestants.items():
           yield (contestant, 
                  self.get_needed_balloon_count_for_contestant(contestant))

    def get_next_needed_balloon(self):
        if self.balloon_generator is None:
            self.balloon_generator = self.iterate_needed_ballons()

        try:
            return self.balloon_generator.next()
        except StopIteration:
            self.balloon_generator = None
            return None, None
