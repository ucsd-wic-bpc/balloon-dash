################################################################################
# hackerrank_selenium_stat_proxy.py
# ucsd-wic-bpc
# 22 November 2016
#
# Classes and utilities to scrape competitor problem data from Hackerrank using
# selenium. Conforms to the stat_proxy interface and uses hackerrank-scraper
# to accomplish its goal
################################################################################
from hackerrank_scraper.scraper import Scraper

class HackerrankSeleniumStatProxy(object):
    """
    Uses hackerrank-scraper to get the leaderboard information
    """

    def __init__(self, leaderboard_url, hackerrank_username, 
                 hackerrank_password):

        self.scraper = Scraper(hackerrank_username, hackerrank_password,
                               leaderboard_url)

    def iterate_updated_contestant_data(self):
        for competitor in self.scraper.scrape(auto_login=True):
            yield (competitor.username, competitor.position, 
                   competitor.completedCount)
