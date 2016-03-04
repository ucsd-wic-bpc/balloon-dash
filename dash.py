from scraper import Scraper
import csv, fileinput, cmd,sys

class Contestant(object):
    contestantCache = {}

    class MoveException(Exception):
        def __init__(self, collisionUsername):
            self.collidesWith = collisionUsername

    def __init__(self, room, team, checkin, hackerrank, name1, name2):
        self.room = room
        self.team = team
        self.checkin = checkin
        self.hackerRank = hackerrank
        self.partnerOne = name1
        self.partnerTwo = name2
        self.completedProblems = 0
        self.lastBalloon = 0

    def __str__(self):
        return "{}: Room {}, team {}".format(self.hackerRank,
                self.room, self.team)

    @classmethod
    def add_to_cache(cls, c):
        if c.hackerRank == "":
            raise ValueError('HackerRank Username cannot be blank')
        cls.contestantCache[c.hackerRank] = c

    @classmethod
    def get_from_cache(cls, hackerrank):
        return cls.contestantCache[hackerrank]

    @classmethod
    def get_all_contestants_iter(cls):
        for hackerrankUsername in cls.contestantCache:
            yield cls.contestantCache[hackerrankUsername]

    @classmethod
    def get_by_team_number(cls, team):
        for hackerrankUsername in cls.contestantCache:
            if cls.contestantCache[hackerrankUsername].team == team:
                return cls.contestantCache[hackerrankUsername]

        raise ValueError('Invalid team')

    @classmethod
    def move_team(cls, username, newTeam):
        try:
            currentResident = cls.get_by_team_number(newTeam)
            raise cls.MoveException(currentResident.hackerRank)
        except ValueError:
            contestant = cls.get_from_cache(username)
            contestant.team = newTeam
            cls.add_to_cache(contestant)

class Dashboard(cmd.Cmd):
    def __init__(self, rosterfile):
        cmd.Cmd.__init__(self)
        self.prompt = "dash> "
        self.rosterFilePath = rosterfile

    def do_load(self, line):
        """ Loads the provided roster file into memory. """
        with open(self.rosterFilePath, 'r') as csvFile:
            rosterReader = csv.DictReader(csvFile)
            for row in rosterReader:
                contestant = Contestant(row['Room #'], row['Team #'],
                        row['Check-In'], row['HackerRank'], 
                        row['Partner 1 Name'], row['Partner 2 Name'])
                try: 
                    Contestant.add_to_cache(contestant)
                except Exception as e:
                    continue

    def do_list(self, line):
        """ Lists all contestants if none specified. Contestants to explicitly
        list can be passed via "list [contestantHackerrank] [contestantHackerrank] """
        if line == "":
            for contestant in Contestant.get_all_contestants_iter():
                print(contestant)
        else:
            for hrUser in line.split(' '):
                try:
                    print(Contestant.get_from_cache(hrUser))
                except Exception:
                    print('Invalid Username: {}'.format(hrUser))

    def do_move(self, line):
        """ Moves the team number for the specified username to the specified number.
        Example: "move <username> 20" """
        try:
            contestant = Contestant.get_from_cache(line.split(' ')[0])
        except Exception:
            print('Invalid Username: {}'.format(line.split(' ')[0]))

        try:
            Contestant.move_team(line.split(' ')[0], line.split(' ')[1])
        except Contestant.MoveException as e:
            print("Cannot move contestant - {} already sitting there".format(
                e.collidesWith))

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
