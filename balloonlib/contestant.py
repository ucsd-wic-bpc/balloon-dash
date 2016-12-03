###############################################################################
# contestant.py
# ucsd-wic-bpc
# 20 November 2016
#
# Class definition and helper methods for a contestant in UCSD's WiC BPC
###############################################################################


class Contestant(object):
    KEY_ROOM_NUMBER = 'Room #'
    KEY_TEAM_NUMBER = 'Team #'
    KEY_CHECKED_IN = 'Check-In'
    KEY_USERNAME = 'HackerRank'
    KEY_PARTNER_ONE = 'Partner 1 Name'
    KEY_PARTNER_TWO = 'Partner 2 Name'
    KEY_COMPLETED_PROBLEMS = 'Problems Completed'
    KEY_CURRENT_BALLOONS = 'Current Balloons'

    @classmethod
    def from_dict(cls, contestant_data):
        return cls(contestant_data[KEY_ROOM_NUMBER],
                   contestant_data[KEY_TEAM_NUMBER],
                   contestant_data[KEY_CHECKED_IN],
                   contestant_data[KEY_USERNAME],
                   contestant_data[KEY_PARTNER_ONE],
                   contestant_data[KEY_PARTNER_TWO],
                   contestant_data.get(KEY_COMPLETED_PROBLEMS, 0),
                   contestant_data.get(KEY_CURRENT_BALLOONS, 0))
    
    def __init__(self, room, team, checked_in, username, partner_one, 
                 partner_two, completed_problems=0, current_ballons=0):
       self.room = room
       self.checked_in = checked_in
       self.username = username
       self.partner_one = partner_one
       self.partner_two = partner_two
       self.completed_problems = completed_problems
       self.current_balloons = current_ballons 
       self._team = team

   def __iter__(self):
       yield self.KEY_ROOM_NUMBER, self.room
       yield self.KEY_TEAM_NUMBER, self._team
       yield self.KEY_CHECKED_IN, self.checked_in
       yield self.KEY_USERNAME, self.username
       yield self.KEY_PARTNER_ONE, self.partner_one
       yield self.KEY_PARTNER_TWO, self.partner_two
       yield self.KEY_COMPLETED_PROBLEMS, self.completed_problems
       yield self.KEY_CURRENT_BALLOONS, self.current_balloons

   def __str__(self):
       return ("Team {} ({}) in room {}. Completed {} problems "
               "and has {} balloons").format(self._team, self.username,
               self.room, self.completed_problems, self.current_balloons)


class ContestantCollection(dict):

    def __init__(self, contestants):
        contestants = {}
        self.contestants_by_team = {}
        for contestant in contestants:
            contestants[contestant.username] = contestant
            self.contestants_by_team[contestant.team] = contestant

        super(ContestantCollection, self).__init__(contestants)

    def move_contestant(contestant, new_team_number):
       if new_team_number in self.contestants_by_team:
           raise ValueEror('Cannot move contestant {} to {} - Not available'
                           .format(str(contestant), new_team_number))

       del self.contestants_by_team[contestant._team]
       contestant._team = new_team_number
       self.contestants_by_team[new_team_number] = contestant
