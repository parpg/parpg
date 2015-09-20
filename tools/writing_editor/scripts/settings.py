#!/usr/bin/env python

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

class Settings():
    """
    The class that contains all of the settings
    """
    def __init__(self):
        """
        Initialize the instance
        """
        self.res_width = None
        self.res_height = None

    def readSettingsFromFile(self, filename):
        """
        Read the settings from a file
        @type filename: string
        @param filename: the file to read from
        @return: None
        """
        file_open = open(filename, 'r')
        contents = file_open.read().strip()
        file_open.close()

        s_contents = contents.split('\n')

        self.res_width = s_contents[0]
        self.res_height = s_contents[1]

    def writeSettingsToFile(self, filename):
        """
        Write the current settings to a file
        @type filename: string
        @param filename: the file to write to
        @return: None
        """
        text_to_write = self.res_width + '\n' + self.res_height
        file_open = open(filename, 'w')
        file_open.write(text_to_write)
        file_open.close()
        
