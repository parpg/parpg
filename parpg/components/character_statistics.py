#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from base import Base

class CharacterStatistics(Base):
    """Component that defines character statistics."""

    def __init__(self):
        """Constructor"""
        Base.__init__(self, gender=str, picture=str, age=int, origin=str, 
                      primary_stats=dict, secondary_stats=dict, traits=list, 
                      )
    @property
    def saveable_fields(self):
        fields = self.fields.keys()
        fields.remove("primary_stats")
        fields.remove("secondary_stats")
        return fields
    
def get_statistic(stats, name):
    """Gets the statistic by its name"""
    if name in stats.primary_stats:
        return stats.primary_stats[name]
    elif name in stats.secondary_stats:
        return stats.secondary_stats[name]
    else:
        for stat in stats.primary_stats:
            if stat.statistic_type.short_name == name:
                return stat
    return None

def get_stat_values(char_stats):
    stats = {"primary":{}, "secondary":{}}
    for name, stat in char_stats.primary_stats.iteritems():
        stats["primary"][name] = stat.value
    for name, stat in char_stats.secondary_stats.iteritems():
        stats["secondary"][name] = stat.value
    return stats