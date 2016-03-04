from scraper import Scraper
import csv, fileinput, cmd,sys

class Contastant(object):
    contestantCache = {}

    def __init__(self, room, team, checkin, hackerrank, name1, name2):
        self.room = room
        self.team = team
        self.checkin = checkin
        self.hackerrank = hackerrank
        self.partnerOne = name1
        self.partnerTwo = name2

    @classmethod
    def add_to_cache(cls, c):
        cls.contestantCache[c.hackerRank] = c

    @classmethod
    def get_from_cache(cls, hackerrank):
        return cls.contestantCache[hackerrank]

class Dashboard(cmd.Cmd):
    def __init__(self, rosterfile):
        cmd.Cmd.__init__(self)
        self.prompt = "dash> "
        self.rosterFilePath = rosterfile

    def do_load(self, line):
        """ Loads the provided roster file into memory. """
        print(self.rosterFilePath)
        with open(self.rosterFilePath, 'r') as csvFile:
            rosterReader = csv.DictReader(csvFile)
            for row in rosterReader:
                print(row['HackerRank'])



    def do_EOF(self, line):
        """ Quit """
        return True

if __name__ == '__main__':

    intro =  """
    ############################################################################
    # University of California, San Diego
    # Women in Computing, Beginners' Programming Competition
    # Balloon Dash
    # https://github.com/ucsd-wic-bpc/balloon-dash
    ############################################################################
    """
    Dashboard(sys.argv[1]).cmdloop(intro)
