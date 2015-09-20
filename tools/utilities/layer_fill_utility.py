#!/usr/bin/env python

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

import sys
if __name__ == '__main__':
    base_string = """<i o="<object>" r="0" x="<X>.0" y="<Y>.0" z="0.0" />\n"""
    try:
        object = raw_input("Object Name: ")
    except KeyboardInterrupt:
        sys.exit(0)
    xmin = None
    while xmin == None:
        try:
            xmin = int(raw_input("xmin: "))
        except ValueError:
            pass
        except KeyboardInterrupt:
            sys.exit(0)
    xmax = None
    while xmax == None:
        try:
            xmax = int(raw_input("xmax: "))
        except ValueError:
            pass
        except KeyboardInterrupt:
            sys.exit(0)
    ymin = None
    while ymin == None:
        try:
            ymin = int(raw_input("ymin: "))
        except ValueError:
            pass
        except KeyboardInterrupt:
            sys.exit(0)
    ymax = None
    while ymax == None:
        try:
            ymax = int(raw_input("ymax: "))
        except ValueError:
            pass
        except KeyboardInterrupt:
            sys.exit(0)

    try:
        filename = raw_input("FileName - File will be overwritten without asking: ")
    except KeyboardInterrupt:
        sys.exit(0)

    file = open(filename, "w")    
    for i in range(xmin, xmax + 1):
        for j in range(ymin, ymax + 1):
            curlinestring = base_string.replace(
                "<object>", object).replace(
                    "<X>", str(i)).replace(
                        "<Y>", str(j))
            file.write(curlinestring)
    file.close()
