#!/usr/bin/env python2
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
A very simple demonstration of the dialogue engine used for testing dialogue
files.
"""
import logging
import os
import sys
from optparse import OptionParser

from parpg.dialogueparsers import YamlDialogueParser
from parpg.dialogueprocessor import DialogueProcessor
from parpg.quest_engine import QuestEngine
from parpg.settings import Settings

class MockPlayerCharacter(object):
    """
    Mock object representing the player character.
    """
    def __init__(self):
        """
        Initialize a new L{MockPlayerCharacter} instance.
        
        @ivar inventory: set of items carried by the L{MockPlayerCharacter}.
        @ivar known_npcs: set of IDs for the NPCs the player has met.
        """
        self.inventory = set(['beer'])
        self.known_npcs = set()
    
    def meet(self, npc_id):
        """
        Add an NPC to the list of NPCs known by the player.
        
        @param npc: ID of the NPC to add.
        @type npc: str
        """
        if npc_id in self.known_npcs:
            raise RuntimeError("I already know {0}".format(npc_id))
        self.known_npcs.add(npc_id)
    
    def met(self, npc):
        return npc in self.known_npcs


class MockBeer(object):
    """Mock object representing a 'beer' item."""
    quality = 3


class MockBox(object):
    """Mock box object than can be opened or closed."""
    def __init__(self):
        """
        Initialize a new {MockBox} instance.
        
        @ivar opened: whether the L{MockBox} has been "opened".
        """
        self.opened = False
    
    def open(self):
        """Set the opened state of the L{MockBox} to True."""
        self.opened = True
    
    def close(self):
        """Set the opened state of the L{MockBox} to False."""
        self.opened = False


def selectDialogueFile(settings):
    """
    List all YAML dialogue files in the dialogue directory and prompt the user
    to select one for testing.
    """
    dialogue_dir = os.path.join(settings.system_path, 
                                settings.parpg.DialoguesPath)
    dialogue_files = [file_name for file_name in os.listdir(dialogue_dir) 
                      if file_name.endswith('.yaml')]
    for index, file_name in enumerate(dialogue_files):
        print('{0} - {1}'.format(index, file_name))
    while True:
        str_input = raw_input("> ")
        try:
            choice_n = int(str_input)
            selected_file_name = dialogue_files[choice_n]
        except (ValueError, IndexError):
            print(('"{0}" is an invalid selection, please choose a number '
                   'between 0 and {1}').format(str_input,
                                               len(dialogue_files) - 1))
            continue
        else:
            break
    
    selected_file_path = os.path.join(dialogue_dir, selected_file_name)
    return selected_file_path

def chooseReply(dialogue_responses):
    """
    Prompt the user to choose a L{DialogueResponse} from a list of valid
    responses.
    
    @param dialogue_responses: valid responses to choose from
    @type dialogue_responses: list of L{DialogueResponses}
    """
    while (True):
        print('Available responses:')
        for index, response in enumerate(dialogue_responses):
            print('{0} - {1}'.format(index, response.text))
        try:
            chosen_response_n = int(raw_input('Choose a response number> '))
            chosen_response = dialogue_responses[chosen_response_n]
        except (ValueError, IndexError):
            print(('\ninvalid response, please enter an integer between 0 '
                   'and {0}').format(len(dialogue_responses) - 1))
        else:
            break
    
    return chosen_response

def processDialogue(dialogue, game_state):
    """
    Process a L{Dialogue} until the user selects a response that ends it.
    
    @param dialogue: dialogue data to process.
    @type dialogue: L{Dialogue}
    @param game_state: objects that should be made available for response
        conditional testing.
    @type game_state: dict of objects
    """
    npc_name = dialogue.npc_name
    dialogue_processor = DialogueProcessor(dialogue, game_state)
    dialogue_processor.initiateDialogue()
    while dialogue_processor.in_dialogue:
        responses = dialogue_processor.continueDialogue()
        current_dialogue_section = \
            dialogue_processor.getCurrentDialogueSection()
        dialogue_text = current_dialogue_section.text
        # Indent dialogue text after the first line.
        dialogue_text = dialogue_text.replace('\n', '\n    ')
        print('\n{0}: {1}'.format(npc_name, dialogue_text))
        chosen_reply = chooseReply(responses)
        dialogue_processor.reply(chosen_reply)

def main():
    parser = OptionParser(description='Script for testing dialogue files')
    parser.add_option('-s', '--settings', nargs=2,
                      dest='paths', default=['.'],
                      help='One or more paths to load settings from')
    parser.add_option('-f', '--logfile',
                        help='Name of log file to save to')
    parser.add_option('-l', '--loglevel', default='critical',
                    help='desired output level for log file')
    
    opts, args = parser.parse_args()

    settings = Settings(*opts.paths)

    levels = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}

    #TODO: setup formating
    logging.basicConfig(filename=opts.logfile, level=levels[opts.loglevel])
    logger = logging.getLogger('dialogue_demo')

    try:
        dialogue_file_path = args[0]
    except IndexError:
        logger.info('No dialogue file provided, generating a list..')
        dialogue_file_path = selectDialogueFile(settings)

    game_state = {
        'quest': QuestEngine('quests'),
        'pc': MockPlayerCharacter(),
        'box': MockBox(),
        'beer': MockBeer()
    }
    dialogue_parser = YamlDialogueParser()
    with file(dialogue_file_path, 'r') as dialogue_file:
        dialogue = dialogue_parser.load(dialogue_file)
    processDialogue(dialogue, game_state)

if __name__ == "__main__":
    main()
