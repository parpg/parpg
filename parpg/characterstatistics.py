#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Provides classes that define character stats and traits.
"""

from abc import ABCMeta, abstractmethod
from weakref import ref as weakref

from .serializers import SerializableRegistry

from components import character_statistics

class AbstractCharacterStatistic(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def __init__(self, description, minimum, maximum):
        self.description = description
        self.minimum = minimum
        self.maximum = maximum


class PrimaryCharacterStatistic(AbstractCharacterStatistic):
    def __init__(self, long_name, short_name, description, minimum=0,
                 maximum=100):
        AbstractCharacterStatistic.__init__(self, description=description,
                                            minimum=minimum, maximum=maximum)
        self.long_name = long_name
        self.short_name = short_name

SerializableRegistry.registerClass(
    'PrimaryCharacterStatistic',
    PrimaryCharacterStatistic,
    init_args=[
        ('long_name', unicode),
        ('short_name', unicode),
        ('description', unicode),
        ('minimum', int),
        ('maximum', int),
    ],
)


class SecondaryCharacterStatistic(AbstractCharacterStatistic):
    def __init__(self, name, description, unit, mean, sd, stat_modifiers,
                 minimum=None, maximum=None):
        AbstractCharacterStatistic.__init__(self, description=description,
                                            minimum=minimum, maximum=maximum)
        self.name = name
        self.unit = unit
        self.mean = mean
        self.sd = sd
        self.stat_modifiers = stat_modifiers

SerializableRegistry.registerClass(
    'SecondaryCharacterStatistic',
    SecondaryCharacterStatistic,
    init_args=[
        ('name', unicode),
        ('description', unicode),
        ('unit', unicode),
        ('mean', float),
        ('sd', float),
        ('stat_modifiers', dict),
        ('minimum', float),
        ('maximum', float),
    ],
)


class AbstractStatisticValue(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def __init__(self, statistic_type, character):
        self.statistic_type = statistic_type
        self.character = weakref(character)


class PrimaryStatisticValue(AbstractStatisticValue):
    def value():
        def fget(self):
            return self._value
        def fset(self, new_value):
            assert 0 <= new_value <= 100
            self._value = new_value
    
    def __init__(self, statistic_type, character, value):
        AbstractStatisticValue.__init__(self, statistic_type=statistic_type,
                                        character=character)
        self._value = None
        self.value = value


class SecondaryStatisticValue(AbstractStatisticValue):
    def normalized_value():
        def fget(self):
            return self._normalized_value
        def fset(self, new_value):
            self._normalized_value = new_value
            statistic_type = self.statistic_type
            mean = statistic_type.mean
            sd = statistic_type.sd
            self._value = self.calculate_value(mean, sd, new_value)
        return locals()
    normalized_value = property(**normalized_value())
    
    def value():
        def fget(self):
            return self._value
        def fset(self, new_value):
            self._value = new_value
            statistic_type = self.statistic_type
            mean = statistic_type.mean
            sd = statistic_type.sd
            self._normalized_value = self.calculate_value(mean, sd, new_value)
        return locals()
    value = property(**value())
    
    def __init__(self, statistic_type, character):
        AbstractStatisticValue.__init__(self, statistic_type=statistic_type,
                                        character=character)
        mean = statistic_type.mean
        sd = statistic_type.sd
        normalized_value = self.derive_value(normalized=True)
        self._normalized_value = normalized_value
        self._value = self.calculate_value(mean, sd, normalized_value)
    
    def derive_value(self, normalized=True):
        """
        Derive the current value 
        """
        statistic_type = self.statistic_type
        stat_modifiers = statistic_type.stat_modifiers
        character = self.character()
        
        value = sum(
            character_statistics.get_statistic(character, name).value * 
            modifier for name, modifier in
                stat_modifiers.items()
        )
        assert 0 <= value <= 100
        if not normalized:
            mean = statistic_type.mean
            sd = statistic_type.sd
            value = self.calculate_value(mean, sd, value)
        return value
    
    @staticmethod
    def calculate_value(mean, sd, normalized_value):
        value = sd * (normalized_value - 50) + mean
        return value
    
    @staticmethod
    def calculate_normalized_value(mean, sd, value):
        normalized_value = ((value - mean) / sd) + 50
        return normalized_value
