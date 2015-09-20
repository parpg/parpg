#   This file is part of PARPG.

#   PARPG is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   PARPG is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with PARPG.  If not, see <http://www.gnu.org/licenses/>.

import yaml

from parpg.common.utils import locateFiles
from parpg import vfs

class Quest(object):
    """Class that holds the information for a quest"""
    def __init__(self, quest_id, quest_giver_id, quest_name, description,
                 variables):
        self.quest_id = quest_id
        self.quest_giver_id = quest_giver_id
        self.quest_name = quest_name
        self.description = description
        self.quest_variables = variables
    
    def setValue(self, variable_name, value):
        """Set the value of a quest variable
           @param variable_name: the name of the variable to set
           @param value: the value you want to assign to the variable
           @return: True on success
           @return: False when it failes"""

        if self.quest_variables.has_key(variable_name):
            self.quest_variables[variable_name]["value"] = value
            return True
        else:
            return False

    def getValue(self, variable_name):
        """Get the value of a quest_variable
           @param variable_name: the name of the variable to set
           @return: the value of the quest_variable"""
        if self.quest_variables.has_key(variable_name):
            return self.quest_variables[variable_name]["value"]
        else:
            return False

    def getGoalValue(self, variable_name):
        """Get the goal value of a quest_variable
           @param variable_name: the name of the variable to set
           @return: the goal value of the quest variable"""
        if self.quest_variables.has_key(variable_name):
            return self.quest_variables[variable_name]["goal_value"]
        else:
            return False

    def increaseValue(self, variable_name, value):
        """Increase a variable by a specified value
           @param variable_name: the name of the variable to set
           @param value: the value you want to increase the variable with
           @return: True on success
           @return: False when it fails"""
        if self.quest_variables.has_key(variable_name):
            self.quest_variables[variable_name]["value"] += value
            return True
        else:
            return False

    def decreaseValue(self, variable_name, value):
        """Decrease a variable by a specified value
           @param variable_name: the name of the variable to set
           @param value: the value you want to decrease the variable with
           @return: True on success
           @return: False when it failes"""
        if self.quest_variables.has_key(variable_name):
            self.quest_variables[variable_name]["value"] -= value
            return True
        else:
            return False

    def isGoalValue(self, variable_name):
        """Check if the variable has reached it's goal value
           @param variable_name: the name of the variable to check
           @return: True when the variable has reached the goal value
           @return: False when it has not reached the goal value"""
        if self.quest_variables.has_key(variable_name):
            return self.quest_variables[variable_name]["value"] == \
                    self.quest_variables[variable_name]["goal_value"]
        else:
            return False

    def isEqualOrBiggerThanGoalValue(self, variable_name):
        """Check if the variable is equil or bigger then it's goal value
           @param variable_name: the name of the variable to set
           @return: True when it has reached or exceeded the goal value
           @return: False when it has not reached or exceeded the goal value """
        if variable_name in self.quest_variables:
            return self.quest_variables[variable_name]["value"] >= \
                             self.quest_variables[variable_name]["goal_value"]
        else:
            return False
    
    def restartQuest(self):
        """Restarts the quest. This sets all values to the reset values,
        if there is a reset value present """
        for variable in self.quest_variables.itervalues():
            if variable.has_key("reset_value"):
                variable["value"] = variable["reset_value"]

class QuestEngine(dict):
    def __init__(self, quest_dir):
        """Create a quest engine object"""
        dict.__init__(self)
        self.empty_quest = Quest(None, None, None, None, {})
        self.quests = {}
        self.active_quests = []
        self.finished_quests = []
        self.failed_quests = []
        self.quest_dir = quest_dir

    def __str__(self):
        return self.quests.__str__()

    def __getitem__(self, key):
        try:
            return self.quests.__getitem__(key)
        except KeyError:
            return self.empty_quest

    def items(self):
        return self.quests.items()

    def values(self):
        return self.quests.values()

    def keys(self):
        return self.quests.keys()
    
    def readQuests(self):
        """Reads in the quests in the quest directory"""
        filepaths = locateFiles("*.yaml", self.quest_dir)
        self.quests = {}
        self.active_quests = []
        self.finished_quests = []
        self.failed_quests = []
        for filepath in filepaths:
            quest_file = vfs.VFS.open(filepath)
            tree = yaml.load(quest_file)
            quest_properties = tree["QUEST_PROPERTIES"]
            variable_defines = tree["DEFINES"]
    
            self.quests[quest_properties["quest_id"]] = \
                                  Quest(quest_properties["quest_id"],
                                        quest_properties["quest_giver_id"],
                                        quest_properties["quest_name"],
                                        quest_properties["description"],
                                        variable_defines)

    def activateQuest(self, quest_id):
        """Add a quest to the quest log
           @param quest: the quest id of the quest to add to the quest log
           @return: True if succesfully added
           @return: False if failed to add"""

        if quest_id in self.quests \
            and not (quest_id in self.active_quests \
                        or quest_id in self.finished_quests):
            self.active_quests.append(quest_id)
            return True
        return False

    def finishQuest(self, quest_id):
        """Move a quest to the finished quests log
           @param quest_id: The id of the quest you want to move
           @return: True on success
           @return: False when it failes"""
        if quest_id in self.active_quests:
            self.finished_quests.append(quest_id)
            self.active_quests.remove(quest_id)
            return True
        return False
    
    def restartQuest(self, quest_id):
        """Restart a quest
           @param quest_id: ID of the quest you want to restart
           @return: True on success
           @return: False when it failes"""
        if quest_id in self.active_quests:
            self.quests[quest_id].restartQuest()
    
    def failQuest(self, quest_id):
        """Set a quest to failed
           @param quest_id: ID of the quest you want to fail
           @return: True on success
           @return: False when it failes"""
        if quest_id in self.active_quests:
            self.failed_quests.append(quest_id)
            self.active_quests.remove(quest_id)
            return True
        return False
            
    def hasQuest(self, quest_id):
        """Check whether a quest is present in the quest_list.
        It doesn't matter which state the quest is, or even if its
        started.
        @param quest_id: ID of the quest you want to check
        @return: True on when the quest is in the quest log
        @return: False when it's not in the quest log"""
        return quest_id in self.quests

    def hasActiveQuest(self, quest_id):
        """Check whether a quest is in the quest log
        @param quest_id: ID of the quest you want to check
        @return: True on when the quest is in the quest log
        @return: False when it's not in the quest log"""
        return quest_id in self.active_quests

    def hasFinishedQuest(self, quest_id):
        """Check whether a quest is in the finished quests log
        @param quest_id: ID of the quest you want to check
        @return: True on when the quest is in the finished quests log
        @return: False when it's not in the finished quests log"""
        return quest_id in self.finished_quests
    
    def hasFailedQuest(self, quest_id):
        """Check whether a quest is in the failed quests log
        @param quest_id: ID of the quest you want to check
        @return: True on when the quest is in the failed quests log
        @return: False when it's not in the failed quests log"""
        return quest_id in self.failed_quests
    
    def getStateForSaving(self):
        """Prepares state for saving
        @type state: dictionary
        @param state: State of the object"""
        ret_dict = {}
        variables_dict = ret_dict["Variables"] = {}
        for quest in self.quests.itervalues():
            quest_dict = variables_dict[quest.quest_id] = {}
            for variable, data in quest.quest_variables.iteritems():
                quest_dict[variable] = data["value"]
        ret_dict["ActiveQuests"] = self.active_quests
        ret_dict["FinishedQuests"] = self.finished_quests
        ret_dict["FailedQuests"] = self.failed_quests
        return ret_dict

    def restoreFromState(self, state):
        """Restores the state"""
        variables_dict = state["Variables"]
        for quest_id, variables in variables_dict.iteritems():
            for variable, value in variables.iteritems():
                self.quests[quest_id].setValue(variable, value)
        self.active_quests = state["ActiveQuests"]
        self.finished_quests = state["FinishedQuests"]
        self.failed_quests = state["FailedQuests"]
