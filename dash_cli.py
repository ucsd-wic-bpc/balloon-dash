################################################################################
# dash.py
# ucsd-wic-bpc
# 3 December 2016
#
# A CLI to managing a programming competition using balloonlib
################################################################################
import json
import click
import cmd
import getpass
import csv
import logging
from balloonlib.contestant import Contestant, ContestantCollection
from balloonlib.competition import Competition
from balloonlib.configuration import Configuration
from balloonlib.hackerrank_selenium_stat_proxy import (
    HackerrankSeleniumStatProxy
)

logging.basicConfig(level=getattr(logging, 'DEBUG'))

class BalloonDashboard(cmd.Cmd):

    def __init__(self, leaderboard_url, hackerrank_username, 
                 hackerrank_password, competition_config, roster_path,
                 autosave):
        cmd.Cmd.__init__(self)
        self.prompt = "dash_cli> "
        self.roster_path = roster_path
        self.autosave = autosave

        # Initialize the stat proxy and contestants for the competition
        stat_proxy = HackerrankSeleniumStatProxy(
            leaderboard_url, hackerrank_username, hackerrank_password)
        self.contestants = self.get_contestant_collection_from_roster()

        # Initialize the competition object
        self.competition = Competition(self.contestants, stat_proxy,
                                       competition_config)

    def get_contestant_collection_from_roster(self):
        contestants = []
        with open(self.roster_path, 'r') as csvRoster:
            roster_reader = csv.DictReader(csvRoster)
            for row in roster_reader:
                contestants.append(Contestant.from_dict(row))

        return ContestantCollection(contestants)

    def write_roster(self):
        with open(self.roster_path, 'w+') as csv_file:
            roster_writer = csv.DictWriter(csv_file, 
                                           fieldnames=Contestant.FIELDNAMES)
            roster_writer.writeheader()
            for contestant in self.contestants.values():
                roster_writer.writerow(dict(contestant))

    def do_print(self, line):
        """
        Prints a one-liner about all teams or a single team if hackerrank
        username is provided. 

        Example:
            print

            print username
        """
        if line:
            if line in self.contestants:
                print(self.contestants[line])
            else:
                print("Invalid username {}".format(line))
        else:
            for contestant in self.contestants.values():
                print(contestant)

    def do_save(self, line):
        """
        Saves the current competition settings into the roster CSV file. Note
        that this also overwrites all currently saved information.
        """
        self.write_roster()

    def do_refresh(self, line):
        """
        Refreshes the details of the competition using the stat proxy
        """
        try:
            bad_usernames = self.competition.refresh_contestants_completed()
            for bad_username in bad_usernames:
                print("WARNING: {} found in competition, not in roster".format(bad_username))

            if self.autosave:
                self.do_save(line)

        except Exception as e:
            print("Something went wrong with refreshing. Details: {}".format(str(e)))

    def do_next(self, line):
        """
        Returns the details about the next competitors balloon needs
        """
        next_competitor, needed_balloons = self.competition.get_next_needed_balloon()
        while next_competitor and needed_balloons <= 0:
            next_competitor, needed_balloons = self.competition.get_next_needed_balloon()

        if not next_competitor:
            print("Nobody needs balloons at the moment!")
        else:
            print("{} balloons for {}".format(needed_balloons, next_competitor))
            next_competitor.current_balloons = needed_balloons

            if self.autosave:
                self.do_save(line)

    def do_EOF(self, line):
        """ Quit """
        return True

@click.command()
@click.option('--config', default='config.json', type=click.File('rb'),
              help='The JSON file to load the config from')
@click.option('--csv', default='roster.csv', type=click.Path(),
              help='The CSV File holding roster information')
@click.option('--autosave/--no-autosave', default=True,
              help='Save everytime an important action is performed')
def cli(config, csv, autosave):
    intro = """
    ############################################################################
    # University of California, San Diego
    # Women in Computing, Beginners' Programming Competition
    # Balloon Dash CLI
    # https://github.com/ucsd-wic-bpc/balloon-dash
    # 03 December 2016
    ############################################################################
    """

    config = json.loads(config.read())

    competition_config = Configuration(config['balloon_problem_counts'])
    leaderboard_url = config['leaderboard_url']
    hackerrank_username = config['hackerrank_username']
    hackerrank_password = getpass.getpass('Hackerrank Password: ')

    dashboard = BalloonDashboard(leaderboard_url, hackerrank_username,
                                 hackerrank_password, competition_config,
                                 csv, autosave)
    dashboard.cmdloop(intro)

if __name__ == '__main__':
    cli()
