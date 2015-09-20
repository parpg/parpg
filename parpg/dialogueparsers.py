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
Contains classes for parsing and validating L{Dialogues<Dialogue>} and other
dialogue-related data.

@TODO Technomage 2010-11-13: Exception handling + validation needs work.
    Currently YAML files are only crudely validated - the code assumes that
    the file contains valid dialogue data, and if that assumption is
    violated and causes the code to raise any TypeErrors, AttributeErrors or
    ValueErrors the code then raises a DialogueFormatError with the
    original (and mostly unhelpful) error message.
@TODO Technomage 2010-11-13: Support reading and writing unicode.
"""
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from collections import Sequence
try:
    from collections import OrderedDict
except ImportError:
    # Python version 2.4-2.6 doesn't have the OrderedDict
    from parpg.common.ordereddict import OrderedDict
import re
import textwrap

import yaml

from parpg import COPYRIGHT_HEADER
from parpg.dialogue import (Dialogue, DialogueSection, DialogueResponse,
    DialogueGreeting)
from parpg.dialogueactions import DialogueAction

import logging
logger = logging.getLogger('dialogueparser')

class DialogueFormatError(Exception):
    """Exception thrown when the DialogueParser has encountered an error."""


class AbstractDialogueParser(object):
    """
    Abstract base class defining the interface for parsers responsible for
    constructing a L{Dialogue} from its serialized representation.
    """
    def load(self, stream):
        """
        Parse a stream and attempt to construct a new L{Dialogue} instance from
        its serialized representation.
        
        @param stream: open stream containing the serialized representation of
            a Dialogue.
        @type stream: BufferType
        """
        raise NotImplementedError('AbstractDialogueParser subclasses must '
                                  'override the load method.')
    
    def dump(self, dialogue, stream):
        """
        Serialize a L{Dialogue} instance and dump it to an open stream.
        
        @param dialogue: dialogue to serialize.
        @type dialogue: L{Dialogue}
        @param stream: open stream into which the serialized L{Dialogue} should
            be dumped.
        @type stream: BufferType
        """
        raise NotImplementedError('AbstractDialogueParser subclasses must '
                                  'override the dump method.')
    
    def validate(self, stream):
        """
        Parse a stream and verify that it contains a valid serialization of a
        L{Dialogue instance}.
        
        @param stream: stream containing the serialized representation of a
            L{Dialogue}
        @type stream: BufferType
        """
        raise NotImplementedError('AbstractDialogueParser subclasses must '
                                  'override the validate method.')


class YamlDialogueParser(AbstractDialogueParser):
    """
    L{AbstractDialogueParser} subclass responsible for parsing dialogues
    serialized in YAML.
    """
    logger = logging.getLogger('dialogueparser.OldYamlDialogueParser')
    
    def load(self, stream, loader_class=yaml.Loader):
        """
        Parse a YAML stream and attempt to construct a new L{Dialogue}
        instance.
        
        @param stream: stream containing the serialized YAML representation of
            a L{Dialogue}.
        @type stream: BufferType
        @param loader_class: PyYAML loader class to use for reading the
            serialization.
        @type loader_class: yaml.BaseLoader subclass
        """
        loader = loader_class(stream)
        dialogue = self._constructDialogue(loader, loader.get_single_node())
        return dialogue
    
    def dump(self, dialogue, output_stream, dumper_class=yaml.Dumper):
        """
        Serialize a L{Dialogue} instance as YAML and dump it to an open stream.
        
        @param dialogue: dialogue to serialize.
        @type dialogue: L{Dialogue}
        @param stream: open stream into which the serialized L{Dialogue} should
            be dumped.
        @type stream: BufferType
        @param dumper_class: PyYAML dumper class to use for formatting the
            serialization.
        @type dumper_class: yaml.BaseDumper subclass
        """
        intermediate_stream = StringIO()
        # KLUDE Technomage 2010-11-16: The "width" argument seems to be broken,
        #     as it doesn't take into about current line indentation and fails
        #     to correctly wrap at word boundaries.
        dumper = dumper_class(intermediate_stream, default_flow_style=False,
                              indent=4, width=99999, line_break='\n',
                              allow_unicode=True, explicit_start=True,
                              explicit_end=True, tags=False)
        dialogue_node = self._representDialogue(dumper, dialogue)
        dumper.open()
        dumper.serialize(dialogue_node)
        dumper.close()
        file_contents = intermediate_stream.getvalue()
        
        file_contents = re.sub(r'(\n|\r|\r\n)(\s*)(GOTO: .*)', r'\1\2\3\1\2',
                               file_contents)
        lines = file_contents.splitlines()
        max_line_length = 76 # 79 - 3 chars for escaping newlines
        for i in range(len(lines)):
            line = lines[i]
            match = re.match(
                r'^(\s*(?:-\s+)?)(SAY|REPLY|CONDITION):\s+"(.*)"$',
                line
            )
            if (match and len(line) > max_line_length):
                # Wrap long lines for readability.
                initial_indent = len(match.group(1))
                subsequent_indent = initial_indent + 4
                text_wrapper = textwrap.TextWrapper(
                    max_line_length,
                    subsequent_indent=' ' * subsequent_indent,
                    break_long_words=False,
                    break_on_hyphens=False
                )
                new_lines = text_wrapper.wrap(line)
                new_lines = (
                    new_lines[:1] + [re.sub(r'^(\s*) (.*)$', r'\1\ \2', l)
                                     for l in new_lines[1:]]
                )
                lines[i] = '\\\n'.join(new_lines)
        
        output_stream.write(COPYRIGHT_HEADER)
        output_stream.write('\n'.join(lines))
        
    
    def _representDialogue(self, dumper, dialogue):
        dialogue_node = dumper.represent_dict({})
        dialogue_dict = OrderedDict()
        dialogue_dict['NPC_NAME'] = dialogue.npc_name
        dialogue_dict['AVATAR_PATH'] = dialogue.avatar_path
        dialogue_dict['DEFAULT_GREETING'] = \
            self._representDialogueSection(dumper,
                                           dialogue.default_greeting)
        # NOTE Technomage 2010-11-16: Dialogue stores its sections in an
        #     OrderedDict, so a round-trip load, dump, and load will preserve
        #     the order of DialogueSections.
        if (len(dialogue.greetings) > 0):
            greetings_list_node = dumper.represent_list([])
            greetings_list = greetings_list_node.value
            for greeting in dialogue.greetings:
                greeting_node = \
                    self._representRootDialogueSection(dumper, greeting)
                greetings_list.append(greeting_node)
            dialogue_dict['GREETINGS'] = greetings_list_node
        if (len(dialogue.setions) > 0):
            sections_list_node = dumper.represent_list([])
            sections_list = sections_list_node.value
            for section in dialogue.sections.values():
                section_node = self._representDialogueSection(dumper, section)
                sections_list.append(section_node)
            dialogue_dict['SECTIONS'] = sections_list_node
        
        for key, value in dialogue_dict.items():
            if (isinstance(key, yaml.Node)):
                key_node = key
            else:
                key_node = dumper.represent_data(key)
            if (isinstance(value, yaml.Node)):
                value_node = value
            else:
                value_node = dumper.represent_data(value)
            dialogue_node.value.append((key_node, value_node))
        return dialogue_node
    
    def _representRootDialogueSection(self, dumper, greeting):
        greeting_node = dumper.represent_dict({})
        greeting_dict = OrderedDict()
        greeting_dict['ID'] = greeting.id
        greeting_dict['CONDITION'] = dumper.represent_scalar(
            'tag:yaml.org,2002:str',
            greeting.condition,
            style='"'
        )
        for key, value in greeting_dict.items():
            if (isinstance(key, yaml.Node)):
                key_node = key
            else:
                key_node = dumper.represent_data(key)
            if (isinstance(value, yaml.Node)):
                value_node = value
            else:
                value_node = dumper.represent_data(value)
            greeting_node.value.append((key_node, value_node))
        return greeting_node
    
    def _representDialogueSection(self, dumper, dialogue_section):
        section_node = dumper.represent_dict({})
        section_dict = OrderedDict() # OrderedDict is required to preserve
                                     # the order of attributes.
        section_dict['ID'] = dialogue_section.id
        # KLUDGE Technomage 2010-11-16: Hard-coding the tag like this could be
        #     a problem when writing unicode.
        section_dict['SAY'] = dumper.represent_scalar('tag:yaml.org,2002:str',
                                                      dialogue_section.text,
                                                      style='"')
        actions_list_node = dumper.represent_list([])
        actions_list = actions_list_node.value
        for action in dialogue_section.actions:
            action_node = self._representDialogueAction(dumper, action)
            actions_list.append(action_node)
        if (actions_list):
            section_dict['ACTIONS'] = actions_list_node
        responses_list_node = dumper.represent_list([])
        responses_list = responses_list_node.value
        for response in dialogue_section.responses:
            response_node = self._representDialogueResponse(dumper, response)
            responses_list.append(response_node)
        section_dict['RESPONSES'] = responses_list_node
        
        for key, value in section_dict.items():
            if (isinstance(key, yaml.Node)):
                key_node = key
            else:
                key_node = dumper.represent_data(key)
            if (isinstance(value, yaml.Node)):
                value_node = value
            else:
                value_node = dumper.represent_data(value)
            section_node.value.append((key_node, value_node))
        return section_node
    
    def _representDialogueResponse(self, dumper, dialogue_response):
        response_node = dumper.represent_dict({})
        response_dict = OrderedDict()
        # KLUDGE Technomage 2010-11-16: Hard-coding the tag like this could be
        #     a problem when writing unicode.
        response_dict['REPLY'] = dumper.represent_scalar(
            'tag:yaml.org,2002:str',
            dialogue_response.text,
            style='"')
        if (dialogue_response.condition is not None):
            response_dict['CONDITION']  = dumper.represent_scalar(
                'tag:yaml.org,2002:str',
                dialogue_response.condition,
                style='"'
            )
        actions_list_node = dumper.represent_list([])
        actions_list = actions_list_node.value
        for action in dialogue_response.actions:
            action_node = self._representDialogueAction(dumper, action)
            actions_list.append(action_node)
        if (actions_list):
            response_dict['ACTIONS'] = actions_list_node
        response_dict['GOTO'] = dialogue_response.next_section_id
        
        for key, value in response_dict.items():
            if (isinstance(key, yaml.Node)):
                key_node = key
            else:
                key_node = dumper.represent_data(key)
            if (isinstance(value, yaml.Node)):
                value_node = value
            else:
                value_node = dumper.represent_data(value)
            response_node.value.append((key_node, value_node))
        return response_node
    
    def _representDialogueAction(self, dumper, dialogue_action):
        action_node = dumper.represent_dict({})
        action_dict = OrderedDict()
        args, kwargs = dialogue_action.arguments
        if (args and not kwargs):
            arguments = list(args)
        elif (kwargs and not args):
            arguments = kwargs
        else:
            arguments = [list(args), kwargs]
        action_dict[dialogue_action.keyword] = arguments
        
        for key, value in action_dict.items():
            if (isinstance(key, yaml.Node)):
                key_node = key
            else:
                key_node = dumper.represent_data(key)
            if (isinstance(value, yaml.Node)):
                value_node = value
            else:
                value_node = dumper.represent_data(value)
            action_node.value.append((key_node, value_node))
        return action_node
    
    def _constructDialogue(self, loader, yaml_node):
        npc_name = None
        avatar_path = None
        default_greeting = None
        greetings = []
        sections = []
        
        try:
            for key_node, value_node in yaml_node.value:
                key = key_node.value
                if (key == u'NPC_NAME'):
                    npc_name = loader.construct_object(value_node)
                elif (key == u'AVATAR_PATH'):
                    avatar_path = loader.construct_object(value_node)
                elif (key == u'DEFAULT_GREETING'):
                    default_greeting = \
                        self._constructDialogueSection(loader, value_node)
                elif (key == u'GREETINGS'):
                    for greeting_node in value_node.value:
                        greeting = self._constructRootDialogueSection(
                                loader,
                                greeting_node
                        )
                        greetings.append(
                            greeting
                        )
                elif (key == u'SECTIONS'):
                    for section_node in value_node.value:
                        dialogue_section = self._constructDialogueSection(
                            loader,
                            section_node
                        )
                        sections.append(dialogue_section)
        except (AttributeError, TypeError, ValueError,
                yaml.scanner.ScannerError) as error:
            raise DialogueFormatError(error)
        
        dialogue = Dialogue(npc_name=npc_name, avatar_path=avatar_path,
                            default_greeting=default_greeting,
                            greetings=greetings,
                            sections=sections)
        return dialogue
    
    def _constructRootDialogueSection(self, loader, greeting_node):
        id = None
        text = None
        condition = None
        responses = []
        actions = []
        greeting = None
        
        try:
            for key_node, value_node in greeting_node.value:
                key = key_node.value
                if (key == u'ID'):
                    id = loader.construct_object(value_node)
                elif (key == u'SAY'):
                    text = loader.construct_object(value_node)
                elif (key == u'CONDITION'):
                    condition = loader.construct_object(value_node)
                elif (key == u'RESPONSES'):
                    for response_node in value_node.value:
                        dialogue_response = self._constructDialogueResponse(
                            loader,
                            response_node
                        )
                        responses.append(dialogue_response)
                elif (key == u'ACTIONS'):
                    for action_node in value_node.value:
                        action = self._constructDialogueAction(loader,
                                                             action_node)
                        actions.append(action)
        except (AttributeError, TypeError, ValueError) as e:
            raise DialogueFormatError(e)
        else:
            greeting = DialogueSection(id=id, text=text,
                                           condition=condition,
                                           responses=responses,
                                           actions=actions)
        
        return greeting
    
    def _constructDialogueSection(self, loader, section_node):
        id_ = None
        text = None
        responses = []
        actions = []
        dialogue_section = None
        
        try:
            for key_node, value_node in section_node.value:
                key = key_node.value
                if (key == u'ID'):
                    id_ = loader.construct_object(value_node)
                elif (key == u'SAY'):
                    text = loader.construct_object(value_node)
                elif (key == u'RESPONSES'):
                    for response_node in value_node.value:
                        dialogue_response = self._constructDialogueResponse(
                            loader,
                            response_node
                        )
                        responses.append(dialogue_response)
                elif (key == u'ACTIONS'):
                    for action_node in value_node.value:
                        action = self._constructDialogueAction(loader,
                                                             action_node)
                        actions.append(action)
        except (AttributeError, TypeError, ValueError) as e:
            raise DialogueFormatError(e)
        else:
            dialogue_section = DialogueSection(id_=id_, text=text,
                                               responses=responses,
                                               actions=actions)
        
        return dialogue_section
    
    def _constructDialogueResponse(self, loader, response_node):
        text = None
        next_section_id = None
        actions = []
        condition = None
        
        try:
            for key_node, value_node in response_node.value:
                key = key_node.value
                if (key == u'REPLY'):
                    text = loader.construct_object(value_node)
                elif (key == u'ACTIONS'):
                    for action_node in value_node.value:
                        action = self._constructDialogueAction(loader,
                                                             action_node)
                        actions.append(action)
                elif (key == u'CONDITION'):
                    condition = loader.construct_object(value_node)
                elif (key == u'GOTO'):
                    next_section_id = loader.construct_object(value_node)
        except (AttributeError, TypeError, ValueError) as e:
            raise DialogueFormatError(e)
        
        dialogue_response = DialogueResponse(text=text,
                                             next_section_id=next_section_id,
                                             actions=actions,
                                             condition=condition)
        return dialogue_response
    
    def _constructDialogueAction(self, loader, action_node):
        mapping = loader.construct_mapping(action_node, deep=True)
        keyword, arguments = mapping.items()[0]
        if (isinstance(arguments, dict)):
            # Got a dictionary of keyword arguments.
            args = ()
            kwargs = arguments
        elif (not isinstance(arguments, Sequence) or
              isinstance(arguments, basestring)):
            # Got a single positional argument.
            args = (arguments,)
            kwargs = {}
        elif (not len(arguments) == 2 or not isinstance(arguments[1], dict)):
            # Got a list of positional arguments.
            args = arguments
            kwargs = {}
        else:
            self.logger.error(
                '{0} is an invalid DialogueAction argument'.format(arguments)
            )
            return None
        
        action_type = DialogueAction.registered_actions.get(keyword)
        if (action_type is None):
            self.logger.error(
                'no DialogueAction with keyword "{0}"'.format(keyword)
            )
            dialogue_action = None
        else:
            dialogue_action = action_type(*args, **kwargs)
        return dialogue_action


class OldYamlDialogueParser(YamlDialogueParser):
    """
    L{YAMLDialogueParser} that can read and write dialogues in the old
    Techdemo1 dialogue file format.
    
    @warning: This class is deprecated and likely to be removed in a future
        version.
    """
    logger = logging.getLogger('dialogueparser.OldYamlDialogueParser')
    
    def __init__(self):
        self.response_actions = {}
    
    def load(self, stream):
        dialogue = YamlDialogueParser.load(self, stream)
        # Place all DialogueActions that were in DialogueSections into the
        # DialogueResponse that led to the action's original section.
        for section in dialogue.sections.values():
            for response in section.responses:
                actions = self.response_actions.get(response.next_section_id)
                if (actions is not None):
                    response.actions = actions
        return dialogue
    
    def _constructDialogue(self, loader, yaml_node):
        npc_name = None
        avatar_path = None
        start_section_id = None
        sections = []
        
        try:
            for key_node, value_node in yaml_node.value:
                key = key_node.value
                if (key == u'NPC'):
                    npc_name = loader.construct_object(value_node)
                elif (key == u'AVATAR'):
                    avatar_path = loader.construct_object(value_node)
                elif (key == u'START'):
                    start_section_id = loader.construct_object(value_node)
                elif (key == u'SECTIONS'):
                    for id_node, section_node in value_node.value:
                        dialogue_section = self._constructDialogueSection(
                            loader,
                            id_node,
                            section_node
                        )
                        sections.append(dialogue_section)
        except (AttributeError, TypeError, ValueError) as e:
            raise DialogueFormatError(e)
        
        dialogue = Dialogue(npc_name=npc_name, avatar_path=avatar_path,
                            start_section_id=start_section_id,
                            sections=sections)
        return dialogue
    
    def _constructDialogueSection(self, loader, id_node, section_node):
        id = loader.construct_object(id_node)
        text = None
        responses = []
        actions = []
        dialogue_section = None
        
        try:
            for node in section_node.value:
                key_node, value_node = node.value[0]
                key = key_node.value
                if (key == u'say'):
                    text = loader.construct_object(value_node)
                elif (key == u'meet'):
                    action = self._constructDialogueAction(loader, node)
                    actions.append(action)
                elif (key in [u'start_quest', u'complete_quest', u'fail_quest',
                              u'restart_quest', u'set_value',
                              u'decrease_value', u'increase_value',
                              u'give_stuff', u'get_stuff']):
                    action = self._constructDialogueAction(loader, node)
                    if (id not in self.response_actions.keys()):
                        self.response_actions[id] = []
                    self.response_actions[id].append(action)
                elif (key == u'responses'):
                    for response_node in value_node.value:
                        dialogue_response = self._constructDialogueResponse(
                            loader,
                            response_node
                        )
                        responses.append(dialogue_response)
        except (AttributeError, TypeError, ValueError) as e:
            raise DialogueFormatError(e)
        else:
            dialogue_section = DialogueSection(id=id, text=text,
                                               responses=responses,
                                               actions=actions)
        
        return dialogue_section
    
    def _constructDialogueResponse(self, loader, response_node):
        text = None
        next_section_id = None
        actions = []
        condition = None
        
        try:
            text = loader.construct_object(response_node.value[0])
            next_section_id = loader.construct_object(response_node.value[1])
            if (len(response_node.value) == 3):
                condition = loader.construct_object(response_node.value[2])
        except (AttributeError, TypeError, ValueError) as e:
            raise DialogueFormatError(e)
        
        dialogue_response = DialogueResponse(text=text,
                                             next_section_id=next_section_id,
                                             actions=actions,
                                             condition=condition)
        return dialogue_response
    
    def _constructDialogueAction(self, loader, action_node):
        mapping = loader.construct_mapping(action_node, deep=True)
        keyword, arguments = mapping.items()[0]
        if (keyword == 'get_stuff'):
            # Renamed keyword in new syntax.
            keyword = 'take_stuff'
        elif (keyword == 'set_value'):
            keyword = 'set_quest_value'
        elif (keyword == 'increase_value'):
            keyword = 'increase_quest_value'
        elif (keyword == 'decrease_value'):
            keyword = 'decrease_quest_value'
        if (isinstance(arguments, dict)):
            # Got a dictionary of keyword arguments.
            args = ()
            kwargs = arguments
        elif (not isinstance(arguments, Sequence) or
              isinstance(arguments, basestring)):
            # Got a single positional argument.
            args = (arguments,)
            kwargs = {}
        elif (not len(arguments) == 2 or not isinstance(arguments[1], dict)):
            # Got a list of positional arguments.
            args = arguments
            kwargs = {}
        else:
            self.logger.error(
                '{0} is an invalid DialogueAction argument'.format(arguments)
            )
            return None
        action_type = DialogueAction.registered_actions.get(keyword)
        if (action_type is None):
            self.logger.error(
                'no DialogueAction with keyword "{0}"'.format(keyword)
            )
            dialogue_action = None
        else:
            dialogue_action = action_type(*args, **kwargs)
        return dialogue_action
