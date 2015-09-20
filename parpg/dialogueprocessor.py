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
Provides the core interface to the dialogue subsystem used to process player
L{Dialogues<Dialogue>} with NPCs.
"""
import logging

from parpg.common.utils import dedent_chomp

if (__debug__):
    from collections import Sequence, MutableMapping
    from parpg.dialogue import Dialogue

logger = logging.getLogger('dialogueprocessor')

class DialogueProcessor(object):
    """
    Primary interface to the dialogue subsystem used to initiate and process a
    L{Dialogue} with an NPC.
    
    To begin a dialogue with an NPC a L{DialogueProcessor} must first be
    instantiated with the dialogue data to process and a dictionary of Python
    objects defining the game state for testing of response conditionals. The
    L{initiateDialogue} must be called to initialized the L{DialogueProcessor},
    and once it is initialized processing of
    L{DialogueSections<DialogueSection>} and
    L{DialogueResponses<DialogueResponse>} can be initiated via the
    L{continueDialogue} and L{reply} class methods.
    
    The state of dialogue processing is stored via the
    L{dialogue_section_stack} class attribute, which stores a list of
    L{DialogueSections<DialogueSection>} that have been or are currently being
    processed. Each time L{reply} is called with a L{DialogueResponse} its
    next_section_id attribute is used to select a new L{DialogueSection} from
    the L{dialogue}. The selected L{DialogueSection} is then pushed
    onto the end of the L{dialogue_section_stack}, ready to be processed via
    L{continueDialogue}. The exception to this rule occurs when L{reply} is
    called with a L{DialogueResponse} whose next_section_id attribute is "end"
    or "back". "end" terminates the dialogue as described below, while "back"
    removes the last L{DialogueSection} on the L{dialogue_section_stack}
    effectively going back to the previous section of dialogue.
    
    The L{DialogueProcessor} terminates dialogue processing once L{reply} is
    called with a L{DialogueResponse} whose next_section_id == 'end'.
    Processing can also be manually terminated by calling the L{endDialogue}
    class method.
    
    @note: See the dialogue_demo.py script for a complete example of how the
        L{DialogueProcessor} can be used.
    
    @ivar dialogue: dialogue data currently being processed.
    @type dialogue: L{Dialogue}
    @ivar dialogue_section_stack: sections of dialogue that have been or are
        currently being processed.
    @type dialogue_section_stack: list of L{DialogueSections<DialogueSection>}
    @ivar game_state: objects defining the game state that should be made
        available for testing L{DialogueResponse} conditionals.
    @type game_state: dict of Python objects
    @ivar in_dialogue: whether a dialogue has been initiated.
    @type in_dialogue: Bool
    
    Usage:
    >>> game_state = {'pc': player_character, 'quest': quest_engine}
    >>> dialogue_processor = DialogueProcessor(dialogue, game_state)
    >>> dialogue_processor.initiateDialogue()
    >>> while dialogue_processor.in_dialogue:
    ...     valid_responses = dialogue_processor.continueDialogue()
    ...     response = choose_response(valid_responses)
    ...     dialogue_processor.reply(response)
    """
    _logger = logging.getLogger('dialogueengine.DialogueProcessor')
    
    def dialogue():
        def fget(self):
            return self._dialogue
        
        def fset(self, dialogue):
            assert isinstance(dialogue, Dialogue), \
                '{0} does not implement Dialogue interface'.format(dialogue)
            self._dialogue = dialogue
        
        return locals()
    dialogue = property(**dialogue())
    
    def dialogue_section_stack():
        def fget(self):
            return self._dialogue_section_stack
        
        def fset(self, new_value):
            assert isinstance(new_value, Sequence) and not \
                   isinstance(new_value, basestring), \
                   'dialogue_section_stack must be a Sequence, not {0}'\
                   .format(new_value)
            self._dialogue_section_stack = new_value
        
        return locals()
    dialogue_section_stack = property(**dialogue_section_stack())
    
    def game_state():
        def fget(self):
            return self._game_state
        
        def fset(self, new_value):
            assert isinstance(new_value, MutableMapping),\
                   'game_state must be a MutableMapping, not {0}'\
                   .format(new_value)
            self._game_state = new_value
        
        return locals()
    game_state = property(**game_state())
    
    def in_dialogue():
        def fget(self):
            return self._in_dialogue
        
        def fset(self, value):
            assert isinstance(value, bool), '{0} is not a bool'.format(value)
            self._in_dialogue = value
        
        return locals()
    in_dialogue = property(**in_dialogue())
    
    def __init__(self, dialogue, game_state):
        """
        Initialize a new L{DialogueProcessor} instance.
        
        @param dialogue: dialogue data to process.
        @type dialogue: L{Dialogue}
        @param game_state: objects defining the game state that should be made
            available for testing L{DialogueResponse} conditions.
        @type game_state: dict of objects
        """
        self._dialogue_section_stack = []
        self._dialogue = dialogue
        self._game_state = game_state
        self._in_dialogue = False
    
    def getDialogueGreeting(self):
        """
        Evaluate the L{RootDialogueSections<RootDialogueSection>} conditions
        and return the valid L{DialogueSection} which should be displayed
        first.
        
        @return: Valid root dialogue section.
        @rtype: L{DialogueSection}
        
        @raise: RuntimeError - evaluation of a DialogueGreeting condition fails
            by raising an exception (e.g. due to a syntax error).
        """
        dialogue = self.dialogue
        dialogue_greeting = None
        for greeting in dialogue.greetings:
            try:
                condition_met = eval(greeting.condition, self.game_state)
            except Exception as exception:
                error_message = dedent_chomp('''
                    exception raised in DialogueGreeting {id} condition:
                    {exception}
                ''').format(id=greeting.id, exception=exception)
                self._logger.error(error_message)
            if (condition_met):
                dialogue_greeting = greeting
        if (dialogue_greeting is None):
            dialogue_greeting = dialogue.default_greeting
        
        return dialogue_greeting
    
    def initiateDialogue(self):
        """
        Prepare the L{DialogueProcessor} to process the L{Dialogue} by pushing
        the starting L{DialogueSection} onto the L{dialogue_section_stack}.
        
        @raise RuntimeError: Unable to determine the root L{DialogueSection}
            defined by the L{Dialogue}.
        """
        if (self.in_dialogue):
            self.endDialogue()
        dialogue_greeting = self.getDialogueGreeting()
        self.dialogue_section_stack.append(dialogue_greeting)
        self.in_dialogue = True
        self._logger.info('initiated dialogue {0}'.format(self.dialogue))
    
    def continueDialogue(self):
        """
        Process the L{DialogueSection} at the top of the
        L{dialogue_section_stack}, run any L{DialogueActions<DialogueActions>}
        it contains and return a list of valid
        L{DialogueResponses<DialogueResponses> after evaluating any response
        conditionals.
        
        @returns: valid responses.
        @rtype: list of L{DialogueResponses<DialogueResponse>}
        
        @raise RuntimeError: Any preconditions are not met.
        
        @precondition: dialogue has been initiated via L{initiateDialogue}.
        """
        if (not self.in_dialogue):
            error_message = dedent_chomp('''
                dialogue has not be initiated via initiateDialogue yet
            ''')
            raise RuntimeError(error_message)
        current_dialogue_section = self.getCurrentDialogueSection()
        self.runDialogueActions(current_dialogue_section)
        valid_responses = self.getValidResponses(current_dialogue_section)
        
        return valid_responses
    
    def getCurrentDialogueSection(self):
        """
        Return the L{DialogueSection} at the top of the
        L{dialogue_section_stack}.
        
        @returns: section of dialogue currently being processed.
        @rtype: L{DialogueSection}
        
        @raise RuntimeError: Any preconditions are not met.
        
        @precondition: dialogue has been initiated via L{initiateDialogue} and
            L{dialogue_section_stack} contains at least one L{DialogueSection}.
        """
        if (not self.in_dialogue):
            error_message = dedent_chomp('''
                getCurrentDialogueSection called but the dialogue has not been
                initiated yet
            ''')
            raise RuntimeError(error_message)
        try:
            current_dialogue_section = self.dialogue_section_stack[-1]
        except IndexError:
            error_message = dedent_chomp('''
                getCurrentDialogueSection called but no DialogueSections are in
                the stack
            ''')
            raise RuntimeError(error_message)
        
        return current_dialogue_section
    
    def runDialogueActions(self, dialogue_node):
        """
        Execute all L{DialogueActions<DialogueActions>} contained by a
        L{DialogueSection} or L{DialogueResponse}.
        
        @param dialogue_node: section of dialogue or response containing the
            L{DialogueActions<DialogueAction>} to execute.
        @type dialogue_node: L{DialogueNode}
        """
        self._logger.info('processing commands for {0}'.format(dialogue_node))
        for command in dialogue_node.actions:
            try:
                command(self.game_state)
            except (Exception,) as error:
                self._logger.error('failed to execute DialogueAction {0}: {1}'
                                   .format(command.keyword, error))
                # TODO Technomage 2010-11-18: Undo previous actions when an
                #     action fails to execute.
            else:
                self._logger.debug('ran {0} with arguments {1}'
                                   .format(getattr(type(command), '__name__'),
                                           command.arguments))
    
    def getValidResponses(self, dialogue_section):
        """
        Evaluate all L{DialogueResponse} conditions for a L{DialogueSection}
        and return a list of valid responses.
        
        @param dialogue_section: section of dialogue containing the
            L{DialogueResponses<DialogueResponse>} to process.
        @type dialogue_section: L{DialogueSection}
        
        @return: responses whose conditions were met.
        @rtype: list of L{DialogueResponses<DialogueResponse>}
        """
        valid_responses = []
        for dialogue_response in dialogue_section.responses:
            condition = dialogue_response.condition
            try:
                condition_met = condition is None or \
                                eval(condition, self.game_state)
            except (Exception,) as exception:
                error_message = dedent_chomp('''
                    evaluation of condition {condition} for {response} failed
                    with error: {exception}
                ''').format(condition=dialogue_response.condition,
                            response=dialogue_response, exception=exception)
                self._logger.error(error_message)
            else:
                self._logger.debug(
                    'condition "{0}" for {1} evaluated to {2}'
                    .format(dialogue_response.condition, dialogue_response,
                            condition_met)
                )
                if (condition_met):
                    valid_responses.append(dialogue_response)
        
        return valid_responses
    
    def reply(self, dialogue_response):
        """
        Reply with a L{DialogueResponse}, execute the
        L{DialogueActions<DialogueAction>} it contains and push the next
        L{DialogueSection} onto the L{dialogue_section_stack}.
        
        @param dialogue_response: response to reply with.
        @type dialogue_response: L{DialogueReponse}
        
        @raise RuntimeError: Any precondition is not met.
        
        @precondition: L{initiateDialogue} must be called before this method
            is used.
        """
        if (not self.in_dialogue):
            error_message = dedent_chomp('''
                reply cannot be called until the dialogue has been initiated
                via initiateDialogue
            ''')
            raise RuntimeError(error_message)
        self._logger.info('replied with {0}'.format(dialogue_response))
        # FIXME: Technomage 2010-12-11: What happens if runDialogueActions
        #     raises an error?
        self.runDialogueActions(dialogue_response)
        next_section_id = dialogue_response.next_section_id
        if (next_section_id == 'back'):
            if (len(self.dialogue_section_stack) == 1):
                error_message = dedent_chomp('''
                    attempted to run goto: back action but stack does not
                    contain a previous DialogueSection
                ''')
                raise RuntimeError(error_message)
            else:
                try:
                    self.dialogue_section_stack.pop()
                except (IndexError,):
                    error_message = dedent_chomp('''
                        attempted to run goto: back action but the stack was
                        empty
                    ''')
                    raise RuntimeError(error_message)
                else:
                    self._logger.debug(
                        'ran goto: back action, restored last DialogueSection'
                    )
        elif (next_section_id == 'end'):
            self.endDialogue()
            self._logger.debug('ran goto: end action, ended dialogue')
        else:
            try:
                next_dialogue_section = \
                    self.dialogue.sections[next_section_id]
            except KeyError:
                error_message = dedent_chomp('''
                    {0} is not a recognized goto: action or DialogueSection
                    identifier
                ''').format(next_section_id)
                raise RuntimeError(error_message)
            else:
                self.dialogue_section_stack.append(next_dialogue_section)
    
    def endDialogue(self):
        """
        End the current dialogue and clean up any resources in use by the
        L{DialogueProcessor}.
        """
        self.dialogue_section_stack = []
        self.in_dialogue = False
