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
"""
Provides classes used to implement dialogue logic and allow dialogues to have
external effects on the game state.
"""
import logging

from parpg.components import container

logger = logging.getLogger('dialogueaction')

class DialogueAction(object):
    """
    Abstract base class for subclasses that represent dialogue actions embedded
    within a DialogueSection or DialogueResponse.
    
    Subclasses must define the keyword class variable and implement both the
    __init__ and __call__ methods.
    
    @cvar keyword: keyword used by the L{DialogueParser} to recognize the
        L{DialogueAction} in serialized L{Dialogues<Dialogues>}.
    @type keyword: basestring
    """
    logger = logging.getLogger('dialogueaction.DialogueAction')
    registered_actions = {}
    
    @classmethod
    def registerAction(cls, dialogue_action_type):
        """
        Register a L{DialogueAction} subclass for easy reference.
        
        @param dialogue_action_type: dialogue action to register.
        @type dialogue_action_type: L{DialogueAction} subclass
        """
        cls.registered_actions[dialogue_action_type.keyword] = \
            dialogue_action_type
    
    def __init__(self, *args, **kwargs):
        """
        Initialize a new L{DialogueAction} instance.
        
        @param args: positional arguments passed by the L{DialogueParser} after
            reading a serialized L{Dialogue}.
        @type args: list of objects
        @param kwargs: keyword arguments passed by the L{DialogueParser} after
            reading a serialized L{Dialogue}.
        @type kwargs: dict of objects
        """
        if (not hasattr(type(self), 'keyword')):
            raise AttributeError('DialogueAction subclasses must define the '
                                 'keyword class variable.')
        self.arguments = (args, kwargs)
    
    def __call__(self, game_state):
        """
        Execute the L{DialogueAction}.
        
        @param game_state: variables and functions that make up the current
            game state.
        @type game_state: dict of objects
        """
        raise NotImplementedError('subclasses of DialogueAction must '
                                  'override __call__')


class MeetAction(DialogueAction):
    """
    L{DialogueAction} that adds an NPC to the list of NPCs known by the player.
    """
    keyword = 'meet'
    
    def __init__(self, *args, **kwargs):
        """
        Initialize a new L{MeetAction} instance.
        
        @param args: positional arguments.
        @type args: list of objects
        @param npc_id: identifier of the NPC that the player has met.
        @type npc_id: basestring
        @param kwargs: keyword arguments (not used).
        @type kwargs: dict of objects
        """
        DialogueAction.__init__(self, *args, **kwargs)
    
    def __call__(self, game_state):
        """
        Add an NPC to the list of NPCs known by the player.
        
        @param game_state: variables and functions that make up the current
            game state.
        @type game_state: dict of objects
        """
        npc_id = game_state["npc"].general.identifier
        # NOTE Technomage 2010-11-13: This print statement seems overly
        #     verbose, so I'm logging it as an INFO message instead.
#        print("You've met {0}!".format(npc_id))
        self.logger.info("You've met {0}!".format(npc_id))
        game_state['meet'](npc_id)
DialogueAction.registerAction(MeetAction)


class InventoryAction(DialogueAction):
    """
    Abstract base class for L{DialogueActions<DialogueAction>} used to
    manipulate the NPC's and the player's inventory.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize a new L{InventoryAction} instance.
        
        @param args: positional arguments.
        @type args: list of objects
        @param item_types: item types that should be manipulated.
        @type item_types: list of basestrings
        @param kwargs: keyword arguments.
        @type kwargs: dict of objects
        """
        DialogueAction.__init__(self, *args, **kwargs)
        self.item_types = args


class TakeStuffAction(InventoryAction):
    """
    L{InventoryAction} used to move items from the NPC's inventory to the
    player's inventory.
    """
    keyword = 'take_stuff'
    
    def __call__(self, game_state):
        """
        Move items from the NPC's inventory to the player's inventory.
        
        @param game_state: variables and functions that make up the current
            game state.
        @type game_state: dict of objects
        """
        item_types = self.item_types
        for item_type in item_types:            
            item = container.take_item(game_state['npc'].container, item_type)
            if (item):
                container.put_item(game_state['pc'].container, item)
                print("{0} gave you the {1}".format(game_state['npc'].
                                                    description.view_name,
                                                    item_type))
            else:
                print("{0} doesn't have the {1}".format(game_state['npc'].
                                                        description.view_name,
                                                        item_type))
DialogueAction.registerAction(TakeStuffAction)


class GiveStuffAction(InventoryAction):
    """
    L{InventoryAction} used to move items from the player's inventory to the
    NPC's inventory.
    """
    keyword = 'give_stuff'
    
    def __call__(self, game_state):
        """
        Move items from the player's inventory to the NPC's inventory.
        
        @param game_state: variables and functions that make up the current
            game state.
        @type game_state: dict of objects
        """
        item_types = self.item_types
        for item_type in item_types:
            item = container.take_item(game_state['pc'].container, item_type)
            if (item):
                container.put_item(game_state['npc'].container, item)
                print("You give the {0} to {1}".format(item_type,
                                                       game_state['npc'].
                                                       description.view_name))
            else:
                print("You don't have the {0}".format(item_type))
DialogueAction.registerAction(GiveStuffAction)


class ReplaceItemAction(InventoryAction):
    """
    L{InventoryAction} used to replace an item with another in the player's
    inventory.
    """
    
    keyword = 'replace_item'
    
    def __call__(self, game_state):
        """
        Take an item from the player and place another at its place.
        
        @param game_state: variables and functions that make up the current
            game state.
        @type game_state: dict of objects
        """
        old_type = self.item_types[0]
        new_type = self.item_types[1]
        item = container.take_item(game_state['pc'].container, old_type)
        if item:
            model = game_state['model']
            new_item = model.createItemByType(new_type, new_type, 
                                              item.entity.world)
            container.put_item(game_state['pc'].container, 
                               new_item.containable, item.slot)
            model.deleteObject(item.entity.general.identifier)
            item.delete()
            print("{0} took the {1} and gave you the {2}".format(
                game_state['npc'].description.view_name, old_type, item_type))
        else:
            print("You don't have the {0}".format(old_type))
DialogueAction.registerAction(ReplaceItemAction)
        
class QuestAction(DialogueAction):
    """
    Abstract base class for quest-related L{DialogueActions<DialogueAction>}.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize a new L{QuestAction} instance.
        
        @param args: positional arguments.
        @type args: list of objects
        @param quest_id: ID of the quest to manipulate.
        @type quest_id: basestring
        @param kwargs: keyword arguments (not used).
        @type kwargs: dict of objects
        """
        DialogueAction.__init__(self, *args, **kwargs)
        self.quest_id = kwargs['quest'] if 'quest' in kwargs else args[0]


class StartQuestAction(QuestAction):
    """L{QuestAction} used to activate a quest."""
    keyword = 'start_quest'
    
    def __call__(self, game_state):
        """
        Activate a quest.
        
        @param game_state: variables and functions that make up the current
            game state.
        @type game_state: dict of objects
        """
        quest_id = self.quest_id
        print("You've picked up the \"{0}\" quest!".format(quest_id))
        game_state['quest'].activateQuest(quest_id)
DialogueAction.registerAction(StartQuestAction)


class CompleteQuestAction(QuestAction):
    """
    L{QuestAction} used to mark a quest as successfully finished/completed.
    """
    keyword = 'complete_quest'
    
    def __call__(self, game_state):
        """
        Successfully complete a quest.
        
        @param game_state: variables and functions that make up the current
            game state.
        @type game_state: dict of objects
        """
        quest_id = self.quest_id
        print("You've finished the \"{0}\" quest".format(quest_id))
        game_state['quest'].finishQuest(quest_id)
DialogueAction.registerAction(CompleteQuestAction)


class FailQuestAction(QuestAction):
    """L{QuestAction} used to fail an active quest."""
    keyword = 'fail_quest'
    
    def __call__(self, game_state):
        """
        Fail an active quest.
        
        @param game_state: variables and functions that make up the current
            game state.
        @type game_state: dict of objects
        """
        quest_id = self.quest_id
        print("You've failed the \"{0}\" quest".format(quest_id))
        game_state['quest'].failQuest(quest_id)
DialogueAction.registerAction(FailQuestAction)


class RestartQuestAction(QuestAction):
    """L{QuestAction} used to restart an active quest."""
    keyword = 'restart_quest'
    
    def __call__(self, game_state):
        """
        Restart an active quest.
        
        @param game_state: variables and functions that make up the current
            game state.
        @type game_state: dict of objects
        """
        quest_id = self.quest_id
        print("You've restarted the \"{0}\" quest".format(quest_id))
        game_state['quest'].restartQuest(quest_id)
DialogueAction.registerAction(RestartQuestAction)


class QuestVariableAction(QuestAction):
    """
    Base class for L{QuestActions<QuestAction>} that modify quest
    variables.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize a new L{QuestVariableAction} instance.
        
        @param args: positional arguments (not used).
        @type args: list of objects
        @param kwargs: keyword arguments.
        @type kwargs: dict of objects
        @keyword quest: ID of the quest whose variable should be modified.
        @type quest: basestring
        @keyword variable: name of the quest variable to modify.
        @type variable: basestring
        @keyword value: new value that should be used to modify the quest
            variable.
        @type value: object
        """
        QuestAction.__init__(self, *args, **kwargs)
        self.variable_name = kwargs['variable']
        self.value = kwargs['value']


class IncreaseQuestVariableAction(QuestVariableAction):
    """
    L{QuestVariableAction} used to increase the value of a quest variable by a
    set amount.
    """
    keyword = 'increase_quest_variable'
    
    def __call__(self, game_state):
        """
        Increase a quest variable by a set amount.
        
        @param game_state: variables and functions that make up the current
            game state.
        @type game_state: dict of objects
        """
        quest_id = self.quest_id
        variable_name = self.variable_name
        value = self.value
        print('Increased {0} by {1}'.format(variable_name, value))
        game_state['quest'][quest_id].increaseValue(variable_name, value)
DialogueAction.registerAction(IncreaseQuestVariableAction)


class DecreaseQuestVariableAction(QuestVariableAction):
    """
    L{QuestVariableAction} used to decrease the value of a quest variable by a
    set amount.
    """
    keyword = 'decrease_quest_variable'
    
    def __call__(self, game_state):
        """
        Decrease a quest variable by a set amount.
        
        @param game_state: variables and functions that make up the current
            game state.
        @type game_state: dict of objects
        """
        quest_id = self.quest_id
        variable_name = self.variable_name
        value = self.value
        print('Decreased {0} by {1}'.format(variable_name, value))
        game_state['quest'][quest_id].decreaseValue(variable_name, value)
DialogueAction.registerAction(DecreaseQuestVariableAction)


class SetQuestVariableAction(QuestVariableAction):
    """
    L{QuestVariableAction} used to set the value of a quest variable.
    """
    keyword = 'set_quest_variable'
    
    def __call__(self, game_state):
        """
        Set the value of a quest variable.
        
        @param game_state: variables and functions that make up the current
            game state.
        @type game_state: dict of objects
        """
        quest_id = self.quest_id
        variable_name = self.variable_name
        value = self.value
        print('Set {0} to {1}'.format(variable_name, value))
        game_state['quest'][quest_id].setValue(variable_name, value)
DialogueAction.registerAction(SetQuestVariableAction)
