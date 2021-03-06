from scraper import Scraper
import csv, fileinput, cmd, sys, json, os
import threading, time
import urllib.request

backgroundUpdate = True
loaded_config = {}

class Contestant(object):
    contestantCache = {}

    class MoveException(Exception):
        def __init__(self, collisionUsername):
            self.collidesWith = collisionUsername

    def __init__(self, room, team, checkin, hackerrank, name1, name2,
            completedProblems, currentBalloons):
        self.room = room
        self.team = team
        self.checkin = checkin
        self.hackerRank = hackerrank
        self.partnerOne = name1
        self.partnerTwo = name2
        self.completedProblems = completedProblems
        self.currentBalloons = currentBalloons

    def get_dict(self):
        return {
                'Room #'  : self.room,
                'Team #'  : self.team,
                'Check-In':self.checkin,
                'HackerRank': self.hackerRank,
                'Partner 1 Name':self.partnerOne,
                'Partner 2 Name':self.partnerTwo,
                'completedProblems': self.completedProblems,
                'currentBalloons': self.currentBalloons,
                }

    def __str__(self):
        return "{}: Room {}, team {}. Completed {} problems".format(self.hackerRank,
                self.room, self.team, self.completedProblems)

    @classmethod
    def get_contestant_count(cls):
        return len(cls.contestantCache)

    @classmethod
    def get_fieldnames(cls):
        return ['Room #', 'Team #', 'Check-In', 'HackerRank', 'Partner 1 Name',
                'Partner 2 Name', 'completedProblems', 'currentBalloons']

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
    def rename_team(cls, username, newUsername):
        try:
            currentResident = cls.get_from_cache(newUsername)
            raise cls.MoveException(newUsername)
        except KeyError:
            try:
                contestant = cls.get_from_cache(username)
                contestant.hackerRank = newUsername
                cls.add_to_cache(contestant)
                del cls.contestantCache[username]
            except KeyError:
                raise KeyError from None

    @classmethod
    def update_completed_count(cls, username, completedCount):
        contestant = cls.get_from_cache(username)
        contestant.completedProblems = completedCount
        cls.add_to_cache(contestant)


def performUpdate():
    scr = Scraper()
    try: 
        for competitorListChunk in scr.scrape():
            for competitor in competitorListChunk:
                try:
                    Contestant.update_completed_count(competitor.username.lower(),
                        competitor.completedCount)
                except Exception as e:
                    print("ERR: Username most likely not found in spreadsheet {}. {}".format(
                        competitor.username, str(e)))
    except Exception:
        return

def save_all():
    with open('dash.save', 'w+') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=Contestant.get_fieldnames())
        writer.writeheader()
        for contestant in Contestant.get_all_contestants_iter():
            writer.writerow(contestant.get_dict())


def send_balloon_update(contestant, missing_balloons):
    global loaded_config
    api_url = loaded_config['api_url']
    push_url = os.path.join(api_url, 'balloonpush.php')
    push_url = '{}?year=fa16&team={}&room={}&balloons={}'.format(
        push_url, contestant.team, contestant.room, missing_balloons)
    urllib.request.urlopen(push_url).read()

    
def update(parallel):
    if parallel:
        global backgroundUpdate
        while backgroundUpdate:
            performUpdate()
            for competitor, missing_balloons in get_needed_balloons_and_ack():
                send_balloon_update(competitor, missing_balloons)
                save_all()
            time.sleep(10)
    else: performUpdate()

def update_last_cmd(f):
    """ A decorator that makes a Cmd command write its name to the Cmd command
    history """
    def decorated(self,line):
        rv = f(self,line)
        self.lastCommand = f.__name__
        return rv
    decorated.__doc__ = f.__doc__
    return decorated

def get_missing_balloons(contestant):
    global loaded_config
    balloon_list = loaded_config['balloon_on']
    needed_balloons = len([req for req in balloon_list if req <= contestant.completedProblems])
    if contestant.currentBalloons < needed_balloons:
        return needed_balloons - contestant.currentBalloons
    else:
        return 0

def get_needed_balloons_and_ack(contestantList=None):
    global loaded_config
    contestantList = contestantList or Contestant.get_all_contestants_iter()
    balloon_list = loaded_config['balloon_on']
    for contestant in contestantList:
        missing_balloons = get_missing_balloons(contestant)
        if missing_balloons > 0:
            yield (contestant, missing_balloons)
            contestant.currentBalloons += missing_balloons

def query_contestants(numContestants, printQuery=True, contestantList=None, check=True):
    iters = 0
    iteratingItem = contestantList if not contestantList is None else Contestant.get_all_contestants_iter()
    lastContestant = None
    for contestant in iteratingItem:
        if iters >= numContestants:
            return lastContestant
        missing_balloons = get_missing_balloons(contestant)
        if (check and missing_balloons != 0) or not check:
            if printQuery:
                print("{} (Room {} Team {}) has completed {} problems. Missing {} balloons".format(
                    contestant.hackerRank, contestant.room, contestant.team, contestant.completedProblems,
                    missing_balloons))
            lastContestant = contestant
            iters += 1
    return None

class Dashboard(cmd.Cmd):
    def __init__(self, rosterfile):
        cmd.Cmd.__init__(self)
        self.prompt = "dash> "
        self.rosterFilePath = rosterfile
        self.lastCommand = ""
        self.lastResult = ""

    @update_last_cmd
    def do_qb(self, line):
        """Balloon the competitor printed in the previous "queryone" result"""
        if self.lastCommand == "do_queryone":
            if not self.lastResult is None:
                self.do_balloon(self.lastResult.hackerRank)
        else:
            print("Cannot perform qb when last command not queryone")

    @update_last_cmd
    def do_load(self, line):
        """ Loads the provided roster file into memory. """
        with open(self.rosterFilePath, 'r') as csvFile:
            rosterReader = csv.DictReader(csvFile)
            for row in rosterReader:
                completedProblems = row['completedProblems'] if 'completedProblems' in row else 0
                currentBalloons = row['currentBalloons'] if 'currentBalloons' in row else 0
                contestant = Contestant(row['Room #'], row['Team #'],
                        row['Check-In'], row['HackerRank'].lower(), 
                        row['Partner 1 Name'], row['Partner 2 Name'], 
                        completedProblems, currentBalloons)
                try: 
                    Contestant.add_to_cache(contestant)
                except Exception as e:
                    continue

    @update_last_cmd
    def do_list(self, line):
        """ Lists all contestants if none specified. Contestants to explicitly
        list can be passed via "list [contestantHackerrank] [contestantHackerrank] """
        if line.split(' ')[0] == "":
            for contestant in Contestant.get_all_contestants_iter():
                print(contestant)
        elif line.split(' ')[0] == '*' and len(line.split(' ')) > 1:
            for contestant in Contestant.get_all_contestants_iter():
                if contestant.completedProblems == line.split(' ')[1]:
                    print(contestant)
        else:
            for hrUser in line.split(' ')[0]:
                try:
                    print(Contestant.get_from_cache(hrUser))
                except Exception:
                    print('Invalid Username: {}'.format(hrUser))

    @update_last_cmd
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

    @update_last_cmd
    def do_rename(self, line):
        """ Renames the team from the first username to the second """
        try:
            contestant = Contestant.get_from_cache(line.split(' ')[0])
        except Exception:
            print('Invalid Username: {}'.format(line.split(' ')[0]))
            return

        try:
            Contestant.rename_team(line.split(' ')[0], line.split(' ')[1])
        except Contestant.MoveException as e:
            print("Cannot rename contestant - {} already named this".format(
                e.collidesWith))
        except ValueError:
            print("Invalid User: {}".format(line.split(' ')[0]))
        except KeyError: 
            print("Invalid User: {}".format(line.split(' ')[0]))

    @update_last_cmd
    def do_update(self, line):
        """ Spawns a hackerrank scraper to update all contestants """
        update(False)

    @update_last_cmd
    def do_updateback(self,line):
        """ Issues updating in the background. WARNING: Opens a new web browser
        instance for every iteration """
        global backgroundUpdate
        backgroundUpdate = True
        def update_parallel(): update(True)
        s = threading.Thread(target=update_parallel)
        s.start()

    @update_last_cmd
    def do_stopupdateback(self,line):
        """ Stop any background udpating """
        global backgroundUpdate
        backgroundUpdate = False

    @update_last_cmd
    def do_query(self, line):
        """ Lists the competitors who have not received a balloon for their 
        completed problems. Contestants to explicitly list can be passed via
        "query [contestantHackerrank] [contestantHackerrank]" """
        if line == "":
            query_contestants(Contestant.get_contestant_count())
        else:
            contestantList = []
            for hrUser in line.split(' '):
                try: 
                    contestant = Contestant.get_from_cache(hrUser)
                    contestantList.append(contestant)
                except Exception:
                    print('Invalid Username: {}'.format(hrUser))

            query_contestants(len(contestantList), contestantList = contestantList, check=False)

    @update_last_cmd
    def do_queryone(self, line):
        """ Lists a single competitor who has not received a balloon for their
        completed problems """
        queried = query_contestants(1)
        self.lastResult = queried

    @update_last_cmd
    def do_balloon(self, line):
        """ Declares that the provided contestant has had their balloon status
        updated """
        try:
            contestant = Contestant.get_from_cache(line)
            contestant.currentBalloons += 1
            Contestant.add_to_cache(contestant)
        except Exception:
            print("Invalid Username: {}".format(line))

    @update_last_cmd
    def do_save(self, line):
        """ Saves the current information into a local file. The dash session
        can then be reopened by using the local file as a commandline arg """
        save_all()

    @update_last_cmd
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
# 03 March 2016
############################################################################

██╗    ██╗██╗ ██████╗              ██████╗ ██████╗  ██████╗
██║    ██║██║██╔════╝              ██╔══██╗██╔══██╗██╔════╝
██║ █╗ ██║██║██║         █████╗    ██████╔╝██████╔╝██║     
██║███╗██║██║██║         ╚════╝    ██╔══██╗██╔═══╝ ██║     
╚███╔███╔╝██║╚██████╗              ██████╔╝██║     ╚██████╗
 ╚══╝╚══╝ ╚═╝ ╚═════╝              ╚═════╝ ╚═╝      ╚═════╝
                                              

Please remember to frequently save your data. Type "help" or "?" for info
	    """
    with open('config.json', 'r') as configFile:
        loaded_config = json.loads(configFile.read())

    if len(sys.argv) < 2: sys.argv.append("")
    Dashboard(sys.argv[1]).cmdloop(intro)
