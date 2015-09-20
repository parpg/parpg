#   This file is part of PARPG.
#
#   PARPG is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   PARPG is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with PARPG.  If not, see <http://www.gnu.org/licenses/>.
"""Provides the controller that defines the behaviour of the character creation
   screen."""

from parpg import vfs
from controllerbase import ControllerBase
from gamescenecontroller import GameSceneController
from gamesceneview import GameSceneView
from parpg.world import PARPGWorld
from parpg.entities import General
from parpg.components import character_statistics

def getStatCost(offset):
    """Gets and returns the cost to increase stat based on the offset"""

    if offset < 0:
        offset *= -1

    if offset < 22:
        return 1
    elif offset < 29:
        return 2
    elif offset < 32:
        return 3
    elif offset < 35:
        return 4
    elif offset < 36:
        return 5
    elif offset < 38:
        return 6
    elif offset < 39:
        return 7
    elif offset < 40:
        return 8
    elif offset < 41:
        return 9
    else:
        return 10    
            
class CharacterCreationController(ControllerBase, PARPGWorld):
    """Controller defining the behaviour of the character creation screen."""
    
    #TODO: Change to actual values
    MAX_TRAITS = 3
    MIN_AGE = 16
    MAX_AGE = 40
    ORIGINS = {"None": None,}
    GENDERS = ["Male", "Female",]
    PICTURES = {"Male": ["None",], "Female": ["None",],}
    TRAITS = {}
    MAX_BULK = 100
    INV_SLOTS = 20
    
    def __init__(self, engine, view, model, application):
        """Construct a new L{CharacterCreationController} instance.
           @param engine: Rendering engine used to display the associated view.
           @type engine: L{fife.Engine}
           @param view: View used to display the character creation screen.
           @type view: L{ViewBase}
           @param model: Model of the game state.
           @type model: L{GameModel}
           @param application: Application used to glue the various MVC
               components together.
           @type application: 
               L{fife.extensions.basicapplication.ApplicationBase}"""
        ControllerBase.__init__(self, engine, view, model, application)
        PARPGWorld.__init__(self, engine)
        self.settings = self.model.settings
        self.view.start_new_game_callback = self.startNewGame
        self.view.cancel_new_game_callback = self.cancelNewGame

    def reset_character(self):
        inventory = []
        for x in xrange(self.INV_SLOTS):
            inventory.append(None)
        self.char_data = General(self, "PlayerCharacter")
        self.char_data.description.view_name = "Player"
        self.char_data.description.real_name = "Enter name here"
        self.char_data.characterstats.gender = self.GENDERS[0]
        self.char_data.characterstats.origin = self.ORIGINS.keys()[0]
        self.char_data.characterstats.age = 20
        self.char_data.characterstats.picture = (
            self.PICTURES[self.GENDERS[0]][0]
        )
        self.model.create_stats(self.char_data)
        self.char_data.container.max_bulk = self.MAX_BULK
        self.char_data.container.children = inventory
        self._stat_points = 200 
    
    def update_agent(self):
        """Updates the player agent data in the model"""
        agent_data = (
            self.model.agents[self.model.ALL_AGENTS_KEY]["PlayerCharacter"]
        )
        agent_data["Statistics"] = (
            character_statistics.get_stat_values(
                self.char_data.characterstats
            )["primary"]
        )
        
    def startNewGame(self):
        """Create the new character and start a new game.
           @return: None"""
        self.update_agent()
        view = GameSceneView(self.engine, self.model)
        controller = GameSceneController(self.engine, view, self.model,
                                         self.application)
        self.application.view = view
        self.application.manager.swap_modes(controller)
        start_map = self.settings.get("parpg", "Map")
        self.model.changeMap(start_map)
    
    def cancelNewGame(self):
        """Exit the character creation view and return the to main menu.
           @return: None"""
        # KLUDGE Technomage 2010-12-24: This is to prevent a circular import
        #     but a better fix needs to be thought up.
        from mainmenucontroller import MainMenuController
        from mainmenuview import MainMenuView
        view = MainMenuView(self.engine, self.model)
        controller = MainMenuController(self.engine, view, self.model,
                                        self.application)
        self.application.view = view
        self.application.manager.activate_mode(controller)
    
    def on_activate(self):
        self.reset_character()
        self.view.show()
    
    def on_deactivate(self):
        """Called when the controller is removed from the list.
           @return: None"""
        self.view.hide()
        
    @property
    def name(self):
        """Returns the name of the character.
        @return: Name of the character"""
        return self.char_data.description.real_name
    
    @property
    def age(self):
        """Returns the age of the character.
        @return: Age of the character"""
        return self.char_data.characterstats.age
    
    @property
    def gender(self):
        """Returns the gender of the character.
        @return: Gender of the character"""
        return self.char_data.characterstats.gender
    
    @property
    def origin(self):
        """Returns the origin of the character.
        @return: Origin of the character"""
        return self.char_data.characterstats.origin
    
    @property
    def picture(self):
        """Returns the ID of the current picture of the character."""
        return self.char_data.characterstats.picture
    
    def getStatPoints(self):
        """Returns the remaining statistic points that can be distributed"""
        return self._stat_points
    
    def increaseStatistic(self, statistic):
        """Increases the given statistic by one.
        @param statistic: Name of the statistic to increase
        @type statistic: string""" 
        if self.canIncreaseStatistic(statistic):
            cost = self.getStatisticIncreaseCost(statistic)
            if  cost <= self._stat_points:
                (self.char_data.characterstats.
                 primary_stats[statistic].value) += 1
                self._stat_points -= cost  

    def getStatisticIncreaseCost(self, statistic):
        """Calculate and return the cost to increase the statistic
        @param statistic: Name of the statistic to increase
        @type statistic: string
        @return cost to increase the statistic"""
        cur_value = (self.char_data.characterstats.
                     primary_stats[statistic].value)
        new_value = cur_value + 1
        offset =  new_value - DEFAULT_STAT_VALUE
        return getStatCost(offset)
    
    def canIncreaseStatistic(self, statistic):
        """Checks whether the given statistic can be increased or not.
        @param statistic: Name of the statistic to check
        @type statistic: string
        @return: True if the statistic can be increased, False if not."""
        stat = self.char_data.characterstats.primary_stats[statistic].value
        return stat < stat.statistic_type.maximum
    
    def decreaseStatistic(self, statistic):
        """Decreases the given statistic by one.
        @param statistic: Name of the statistic to decrease
        @type statistic: string""" 
        if self.canDecreaseStatistic(statistic):
            gain = self.getStatisticDecreaseGain(statistic)
            self.char_data.characterstats.primary_stats[statistic].value -= 1
            self._stat_points += gain  

    def getStatisticDecreaseGain(self, statistic):
        """Calculate and return the gain of decreasing the statistic
        @param statistic: Name of the statistic to decrease
        @type statistic: string
        @return cost to decrease the statistic"""
        cur_value = (self.char_data.characterstats.
                     primary_stats[statistic].value)
        new_value = cur_value - 1
        offset =  new_value - DEFAULT_STAT_VALUE
        return getStatCost(offset)
    
    def canDecreaseStatistic(self, statistic):
        """Checks whether the given statistic can be decreased or not.
        @param statistic: Name of the statistic to check
        @type statistic: string
        @return: True if the statistic can be decreased, False if not."""
        stat = self.char_data.characterstats.primary_stats[statistic].value
        return stat > stat.statistic_type.minimum
    
    def getStatisticValue(self, statistic):
        """Returns the value of the given statistic.
        @param statistic: Name of the primary or secondary statistic
        @type statistic: string
        @return: Value of the given statistic"""
        if self.char_data.characterstats.primary_stats.has_key:
            return self.char_data.characterstats.primary_stats[statistic]
        else:
            return self.char_data.characterstats.secondary_stats[statistic]
    
    def areAllStatisticsValid(self):
        """Checks if all statistics are inside the minimum/maximum values
        @return True if all statistics are valid False if not"""
        all_stats = self.char_data.characterstats.primary_stats.items()
        all_stats.extend(self.char_data.characterstats.secondary_stats.items())
        for stat in all_stats:
            if not (stat.value > stat.statistic_type.minumum and\
                stat.value < stat.statistic_type.maximum):
                return False
        return True
    
    def setName(self, name):
        """Sets the name of the character to the given value.
        @param name: New name
        @type name: string"""
        self.char_data.description.real_name = name
    
    def isNameValid(self, name):
        """Checks whether the name is valid.
        @param name: Name to check
        @type name: string
        @return: True if the name is valid, False if not"""
        if name:
            return True
        return False
    
    def changeOrigin(self, origin):
        """Changes the origin of the character to the given value.
        @param origin: New origin
        @type origin: string"""
        if self.isOriginValid(origin):
            self.char_data.characterstats.origin = origin
            #TODO: Make changes according to origin
   
    def isOriginValid(self, origin):
        """Checks whether the origin is valid.
        @param origin: Origin to check
        @type origin: string
        @return: True if the origin is valid, False if not"""
        return origin in self.ORIGINS
    
    def changeGender(self, gender):
        """Changes the gender of the character to the given value.
        @param gender: New gender
        @param gender: string"""
        if self.isGenderValid(gender):
            self.char_data.characterstats.gender = gender
    
    def isGenderValid(self, gender):
        """Checks whether the gender is valid.
        @param gender: Gender to check
        @type gender: string?
        @return: True if the origin is valid, False if not"""        
        return gender in self.GENDERS
    
    def changeAge(self, age):
        """Sets the age of the character to the given value.
        @param age: New age
        @type age: integer
        """
        if self.isAgeValid(age):
            self.char_data.characterstats.age = age
    
    def isAgeValid(self, age):
        """Checks whether the age is valid.
        @param age: Age to check
        @type age: integer
        @return: True if the origin is valid, False if not"""
        return age >= self.MIN_AGE and age <= self.MAX_AGE 
    
    def setPicture(self, picture):
        """Set picture of the character.
        @param picture: ID of the new picture
        @type picture: string"""
        if self.isPictureValid(picture):
            self.char_data.characterstats.picture = picture
    
    def isPictureValid(self, picture):
        """Checks whether the picture is valid.
        @param picture: ID of the picture to check
        @type picture: string
        @return: True if the picture is valid, False if not"""
        return picture in self.PICTURES[self.gender]
    
    def addTrait(self, trait):
        """Adds a trait to the character.
        @param trait: ID of the trait to add
        @type trait: string"""
        if self.canAddAnotherTrait() and self.isTraitValid(trait)\
                and not self.hasTrait(trait):
            self.char_data.characterstats.traits.append(trait)                
    
    def canAddAnotherTrait(self):
        """Checks whether another trait can be added.
        @return: True if another trait can be added, False if not"""
        return len(self.char_data.characterstats.traits) < self.MAX_TRAITS
    
    def removeTrait(self, trait):
        """Remove trait from character.
        @param trait: ID of the trait to remove
        @type trait: string"""
        if self.hasTrait(trait):
            self.char_data.characterstats.traits.remove(trait)
    
    def hasTrait(self, trait):
        """Checks whether the character has the trait.
        @param trait: ID of the trait to check
        @type trait: string
        @return: True if the character has the trait, False if not"""
        return trait in self.char_data.characterstats.traits
    
    def isTraitValid(self, trait):
        """Checks whether the trait is valid.
        @param trait: ID of the trait to check
        @type trait: string
        @return: True if the trait is valid, False if not"""
        return trait in self.TRAITS
    
    def areCurrentTraitsValid(self):
        """Checks whether the characters traits are valid.
        @return: True if the traits are valid, False if not"""
        if len(self.char_data.characterstats.traits) > self.MAX_TRAITS:
            return False 
        for trait in self.char_data.characterstats.traits:
            if not self.isTraitValid(trait):
                return False
        return True
    
    def isCharacterValid(self):
        """Checks whether the character as a whole is valid.
        @return: True if the character is valid, False if not"""
        #Single checks can be disabled by putting a "#" in front of them
        if True\
        and self._stat_points >= 0\
        and self.areAllStatisticsValid() \
        and self.areCurrentTraitsValid() \
        and self.isNameValid(self.name)\
        and self.isPictureValid(self.picture)\
        and self.isAgeValid(self.age)\
        and self.isGenderValid(self.gender)\
        and self.isOriginValid(self.origin)\
        :
            return True
        return False
