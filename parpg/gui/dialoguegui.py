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
import logging

from fife import fife
from fife.extensions import pychan
from fife.extensions.pychan import widgets

from parpg import vfs
from parpg.dialogueprocessor import DialogueProcessor

logger = logging.getLogger('dialoguegui')

class DialogueGUI(object):
    """Window that handles the dialogues."""
    _logger = logging.getLogger('dialoguegui.DialogueGUI')
    
    def __init__(self, controller, npc, quest_engine, met_fnc, meet_fnc, 
                 has_fnc, player_character):
        self.active = False
        self.controller = controller
        xml_file = vfs.VFS.open('gui/dialogue.xml')
        self.dialogue_gui = pychan.loadXML(xml_file)
        self.npc = npc
        # TODO Technomage 2010-11-10: the QuestEngine should probably be
        #     a singleton-like object, which would avoid all of this instance
        #     handling.
        self.quest_engine = quest_engine
        self.player_character = player_character
        self.met_fnc = met_fnc
        self.meet_fnc = meet_fnc
        self.pc_has_fnc = lambda slot_or_type:\
            has_fnc(player_character.container, slot_or_type)
        self.npc_has_fnc = lambda slot_or_type:\
            has_fnc(npc.container, slot_or_type)
    
    def initiateDialogue(self):
        """Callback for starting a quest"""
        self.active = True
        stats_label = self.dialogue_gui.findChild(name='stats_label')
        stats_label.text = u'Name: John Doe\nAn unnamed one'
        events = {
            'end_button': self.handleEnd
        }
        self.dialogue_gui.mapEvents(events)
        self.dialogue_gui.show()
        self.setNpcName(self.npc.description.view_name)
        self.setAvatarImage(self.npc.dialogue.dialogue.avatar_path)
        
        game_state = {'npc': self.npc, 'pc': self.player_character,
                      'quest': self.quest_engine, 
                      'met': self.met_fnc, 'meet': self.meet_fnc, 
                      'pc_has': self.pc_has_fnc, 'npc_has': self.npc_has_fnc,
                      'model': self.controller.model,
                      }
        try:
            self.dialogue_processor = DialogueProcessor(self.npc.dialogue.dialogue,
                                                        game_state)
            self.dialogue_processor.initiateDialogue()
        except (TypeError) as error:
            self._logger.error(str(error))
        else:
            self.continueDialogue()
    
    def setDialogueText(self, text):
        """Set the displayed dialogue text.
           @param text: text to display."""
        text = unicode(text)
        speech = self.dialogue_gui.findChild(name='speech')
        # to append text to npc speech box, uncomment the following line
        #speech.text = speech.text + "\n-----\n" + unicode(say)
        speech.text = text
        self._logger.debug('set dialogue text to "{0}"'.format(text))
    
    def continueDialogue(self):
        """Display the dialogue text and responses for the current
           L{DialogueSection}."""
        dialogue_processor = self.dialogue_processor
        dialogue_text = dialogue_processor.getCurrentDialogueSection().text
        self.setDialogueText(dialogue_text)
        self.responses = dialogue_processor.continueDialogue()
        self.setResponses(self.responses)
    
    def handleEntered(self, *args):
        """Callback for when user hovers over response label."""
        pass
    
    def handleExited(self, *args):
        """Callback for when user hovers out of response label."""
        pass
    
    def handleClicked(self, *args):
        """Handle a response being clicked."""
        response_n = int(args[0].name.replace('response', ''))
        response = self.responses[response_n]
        dialogue_processor = self.dialogue_processor
        dialogue_processor.reply(response)
        if (not dialogue_processor.in_dialogue):
            self.handleEnd()
        else:
            self.continueDialogue()
    
    def handleEnd(self):
        """Handle the end of the conversation being reached, either from the
           GUI or from within the conversation itself."""
        self.dialogue_gui.hide()
        self.responses = []
        self.npc.fifeagent.behaviour.state = 1
        self.npc.fifeagent.behaviour.idle()
        self.active = False
    
    def setNpcName(self, name):
        """Set the NPC name to display on the dialogue GUI.
           @param name: name of the NPC to set
           @type name: basestring"""
        name = unicode(name)
        stats_label = self.dialogue_gui.findChild(name='stats_label')
        try:
            (first_name, desc) = name.split(" ", 1)
            stats_label.text = u'Name: ' + first_name + "\n" + desc
        except ValueError:
            stats_label.text = u'Name: ' + name
        
        self.dialogue_gui.title = name
        self._logger.debug('set NPC name to "{0}"'.format(name))
    
    def setAvatarImage(self, image_path):
        """Set the NPC avatar image to display on the dialogue GUI
           @param image_path: filepath to the avatar image
           @type image_path: basestring"""
        avatar_image = self.dialogue_gui.findChild(name='npc_avatar')
        avatar_image.image = image_path
    
    def setResponses(self, dialogue_responses):
        """Creates the list of clickable response labels and sets their
           respective on-click callbacks.
           @param responses: list of L{DialogueResponses} from the
               L{DialogueProcessor}
           @type responses: list of L{DialogueResponses}"""
        choices_list = self.dialogue_gui.findChild(name='choices_list')
        choices_list.removeAllChildren()
        for index, response in enumerate(dialogue_responses):
            button = widgets.Label(
                name="response{0}".format(index),
                text=unicode(response.text),
                hexpand="1",
                min_size=(100,16),
                max_size=(490,48),
                position_technique='center:center'
            )
            button.margins = (5, 5)
            button.background_color = fife.Color(0, 0, 0)
            button.color = fife.Color(0, 255, 0)
            button.border_size = 0
            button.wrap_text = 1
            button.capture(lambda button=button: self.handleEntered(button),
                           event_name='mouseEntered')
            button.capture(lambda button=button: self.handleExited(button),
                           event_name='mouseExited')
            button.capture(lambda button=button: self.handleClicked(button),
                           event_name='mouseClicked')
            choices_list.addChild(button)
            self.dialogue_gui.adaptLayout(True)
            self._logger.debug(
                'added {0} to response choice list'.format(response)
            )
