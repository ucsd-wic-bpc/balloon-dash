from scraper import Scraper
import csv, fileinput, cmd,sys

class Contestant(object):
    contestantCache = {}

    class MoveException(Exception):
        def __init__(self, collisionUsername):
            self.collidesWith = collisionUsername

    def __init__(self, room, team, checkin, hackerrank, name1, name2,
            completedProblems, lastBalloon, disregardedAt):
        self.room = room
        self.team = team
        self.checkin = checkin
        self.hackerRank = hackerrank
        self.partnerOne = name1
        self.partnerTwo = name2
        self.completedProblems = completedProblems
        self.lastBalloon = lastBalloon
        self.disregardedAt = disregardedAt

    def get_dict(self):
        return {
                'Room #'  : self.room,
                'Team #'  : self.team,
                'Check-In':self.checkin,
                'HackerRank': self.hackerRank,
                'Partner 1 Name':self.partnerOne,
                'Partner 2 Name':self.partnerTwo,
                'completedProblems': self.completedProblems,
                'lastBalloon': self.lastBalloon,
                'disregardedAt':self.disregardedAt 
                }

    def __str__(self):
        return "{}: Room {}, team {}. Completed {} problems".format(self.hackerRank,
                self.room, self.team, self.completedProblems)

    @classmethod
    def get_fieldnames(cls):
        return ['Room #', 'Team #', 'Check-In', 'HackerRank', 'Partner 1 Name',
                'Partner 2 Name', 'completedProblems', 'lastBalloon',
                'disregardedAt']

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

    @classmethod
    def update_completed_count(cls, username, completedCount):
        contestant = cls.get_from_cache(username)
        contestant.completedProblems = completedCount
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
                disregardedAt = row['disregardedAt'] if 'disregardedAt' in row else 0
                completedProblems = row['completedProblems'] if 'completedProblems' in row else 0
                lastBalloon = row['lastBalloon'] if 'lastBalloon' in row else 0
                contestant = Contestant(row['Room #'], row['Team #'],
                        row['Check-In'], row['HackerRank'], 
                        row['Partner 1 Name'], row['Partner 2 Name'], 
                        completedProblems, lastBalloon, disregardedAt)
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

    def do_update(self, line):
        """ Spawns a hackerrank scraper to update all contestants """
        scr = Scraper()
        for competitorListChunk in scr.scrape():
            for competitor in competitorListChunk:
                try:
                    Contestant.update_completed_count(competitor.username,
                        competitor.completedCount)
                except Exception as e:
                    print("ERR: Username most likely not found in spreadsheet {}. {}".format(
                        competitor.username, str(e)))

    def do_query(self, line):
        """ Lists the competitors who have not received a balloon for their 
        completed problems. Contestants to explicitly list can be passed via
        "query [contestantHackerrank] [contestantHackerrank]" """
        if line == "":
            for contestant in Contestant.get_all_contestants_iter():
                if not contestant.lastBalloon == contestant.completedProblems:
                    if not contestant.disregardedAt == contestant.completedProblems:
                        print("{} (Team {}) has completed {} problems. Last balloon given at {} problems.".format(
                            contestant.hackerRank, contestant.team, contestant.completedProblems,
                            contestant.lastBalloon))
        else:
            for hrUser in line.split(' '):
                try: 
                    contestant = Contestant.get_from_cache(hrUser)
                    print("{} (Team {}) has completed {} problems. Last balloon given at {} problems.".format(
                    contestant.hackerRank, contestant.team, contestant.completedProblems,
                    contestant.lastBalloon))
                except Exception:
                    print('Invalid Username: {}'.format(hrUser))

    def do_queryone(self, line):
        """ Lists a single competitor who has not received a balloon for their
        completed problems """
        for contestant in Contestant.get_all_contestants_iter():
            if not contestant.lastBalloon == contestant.completedProblems:
                if not contestant.disregardedAt == contestant.completedProblems:
                    print("{} (Team {}) has completed {} problems. Last balloon given at {} problems.".format(
                        contestant.hackerRank, contestant.team, contestant.completedProblems,
                        contestant.lastBalloon))
                    return

    def do_disregard(self, line):
        """ Disregards the current contestant until they've completed an
        additional problem """
        try:
            contestant = Contestant.get_from_cache(line)
            contestant.disregardedAt = contestant.completedProblems
            Contestant.add_to_cache(contestant)
        except Exception:
            print("Invalid Username: {}".format(line))

    def do_balloon(self, line):
        """ Declares that the provided contestant has had their balloon status
        updated """
        try:
            contestant = Contestant.get_from_cache(line)
            contestant.lastBalloon = contestant.completedProblems
            Contestant.add_to_cache(contestant)
        except Exception:
            print("Invalid Username: {}".format(line))

    def do_save(self, line):
        """ Saves the current information into a local file. The dash session
        can then be reopened by using the local file as a commandline arg """
        with open('dash.save', 'w+') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=Contestant.get_fieldnames())
            writer.writeheader()
            for contestant in Contestant.get_all_contestants_iter():
                writer.writerow(contestant.get_dict())

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