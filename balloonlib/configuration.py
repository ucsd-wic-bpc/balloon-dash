################################################################################
# configuration.py
# ucsd-wic-bpc
# 03 December 2016
#
# A class used to hold the configuration values for a specific programming
# competition.
################################################################################

class Configuration(object):

    def __init__(self, balloon_problem_counts):
        """
        Arguments:
            balloon_problem_counts: list - The numbers of problem completions
                which correspond to getting a balloon
        """
        self.balloon_problem_counts = balloon_problem_counts
