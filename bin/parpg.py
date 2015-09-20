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

#TODO: Modularize this script
import sys
from optparse import OptionParser
from os import path

usage = ('usage: %prog [options] '
         'Example: python %prog .')

parser = OptionParser(description='PARPG Launcher Script', usage=usage)
parser.add_option('-f', '--logfile',
                  help='Name of log file to save to')
parser.add_option('-l', '--loglevel', default='critical',
                  help='desired output level for log file')
parser.add_option('-p', '--fife-path',
                  help='Path to the fife module')
parser.add_option('-m', '--parpg-path',
                  help='Path to the parpg module')

opts, args = parser.parse_args()

try:
    old_path = sys.path
    if opts.parpg_path:
        sys.path = [opts.parpg_path]
    import parpg
except ImportError:
    print("Could not import parpg module. Please install parpg or set the --parpg-path command line value")
    parser.print_help()
    sys.exit(1)
finally:
    sys.path = old_path


from parpg.main import main
main(parser)
