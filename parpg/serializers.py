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
"""
Provides classes used to serialize and deserialize Python classes.
"""

from abc import ABCMeta, abstractmethod
try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree
try:
    from collections import OrderedDict
except ImportError:
    from .common.ordereddict import OrderedDict

from .common.utils import dedent_chomp

import logging

logger = logging.getLogger('serializers')

class Serializable(object):
    def __init__(self, class_, init_args=None, attributes=None):
        self.class_ = class_
        if init_args is not None:
            self.init_args = OrderedDict(init_args)
        else:
            self.init_args = OrderedDict()
        if attributes is not None:
            self.attributes = OrderedDict(attributes)
        else:
            self.attributes = OrderedDict()


class SerializableRegistry(object):
    """
    Class holding the data used to serialize and deserialize a particular
    Python object.
    """
    registered_classes = {}
    
    @classmethod
    def registerClass(cls, name, class_, init_args=None, attributes=None):
        serializable = Serializable(class_, init_args, attributes)
        cls.registered_classes[name] = serializable


class AbstractSerializer(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def serialize(self, object_, stream):
        pass
    
    @abstractmethod
    def deserialize(self, stream):
        pass


class XmlSerializer(AbstractSerializer):
    def serialize(self, statistic, stream):
        pass
    
    @classmethod
    def deserialize(cls, stream):
        element_tree = ElementTree.parse(stream)
        root_element = element_tree.getroot()
        object_ = cls.construct_object(root_element)
        return object_
    
    @classmethod
    def construct_object(cls, element):
        element_name = element.tag
        if element_name in SerializableRegistry.registered_classes.keys():
            object_ = cls.construct_registered_class(element)
        elif len(element) > 0:
            # Element contains subelements, so we'll treat it as an
            # OrderedDict.
            if element_name == 'list':
                object_ = cls.construct_list(element)
            else:
                object_ = cls.construct_ordered_dict(element)
        else:
            object_ = cls.construct_primitive(element)
        return object_
    
    @classmethod
    def construct_registered_class(cls, element):
        element_name = element.tag
        serializable = SerializableRegistry.registered_classes[element_name]
        class_ = serializable.class_
        init_args = OrderedDict()
        for subelement in element:
            arg = cls.construct_object(subelement)
            subelement_name = subelement.tag
            init_args[subelement_name] = arg
        try:
            object_ = class_(**init_args)
        except (TypeError, ValueError) as exception:
            logger.error(init_args)
            error_message = \
                'unable to deserialize tag {0}: {1}'.format(element_name,
                                                            exception)
            raise ValueError(error_message)
        return object_
    
    @classmethod
    def construct_ordered_dict(cls, element):
        object_ = OrderedDict()
        for subelement in element:
            child = cls.construct_object(subelement)
            name = subelement.tag
            object_[name] = child
        return object_
    
    @classmethod
    def construct_list(cls, element):
        object_ = []
        for subelement in element:
            child = cls.construct_object(subelement)
            object_.append(child)
        return object_
    
    @classmethod
    def construct_primitive(cls, element):
        text = element.text
        # Interpret the element's text as unicode by default.
        element_type = element.attrib.get('type', 'unicode')
        if element_type == 'unicode':
            formatted_text = dedent_chomp(text)
            object_ = unicode(formatted_text)
        elif element_type == 'str':
            formatted_text = dedent_chomp(text)
            object_ = str(formatted_text)
        elif element_type == 'int':
            object_ = int(text)
        elif element_type == 'float':
            object_ = float(text)
        else:
            error_message = '{0!r} is not a recognized primitive type'
            error_message.format(element_type)
            raise ValueError(error_message)
        return object_
