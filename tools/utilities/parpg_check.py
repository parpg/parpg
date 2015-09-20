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
#   along with this program.  If not, see <http://www.gnu.org/licenses/>

helpstring = """
Runs pylint on all python files found in a directory and
its subdirectories. Prints messages that match
the type of checks we wish to see.

Usage:
        parpg-check.py [--check check_type] [/path/to/parpg]

check_types:
        errors
        warnings
        conventions
        refactors
        all

If no check_type is given it defaults to showing only possible 'errors'.
If not path is given it defaults to the current parent directory.
"""

import os
import sys
import re
import imp
from optparse import OptionParser


def check(module, regx):
    """ Applies pylint to the file specified and displays only the
        messages that match our type of code check.
    """
    pout = os.popen('pylint --reports=no %s 2> %s' % (module, os.devnull), 'r')
    errs = [line for line in pout if re.match(regx, line)]
    if errs:
        print_matches(module, errs)


def print_matches(mod, matches):
    """ Prints the matching messages for our type of
        code check.
    """
    print "Found %s errors in %s :" % (len(matches), mod)
    for match in matches:
        print "\t %s" % match.rstrip('\n')
    print

def main():
    # Check if pylint is installed
    try:
        imp.find_module('pylint')
    except:
        sys.exit("This script requires pylint! Exiting...")

    version = 'Version: %prog 0.1'
    parser = OptionParser(usage=helpstring, version=version)
    parser.add_option('-c', '--check', action='store', \
            type='string', dest='check_type',
            help='types of code checks to show',
            default='errors')
    opts, args = parser.parse_args()

    # Setup the base directory where our script will start
    try:
        base_directory = args[0]
    except IndexError:
        print "No directory specified, defaulting to parent"
        base_directory = os.path.abspath("..")

    # Setup the type of checks we want
    rgx_map = {"warnings": "^W:",
                "errors":   "^E:",
                "pep8": "^C:",
                "refactors": "^R:",
                "all": "^[WECRF]:"}
    chk_type = opts.check_type

    print "***** Checking %s for %s.\n" % (os.path.abspath(base_directory), chk_type)

    # Start crawling for 'py' files
    for root, dirs, files in os.walk(base_directory):
        for name in files:
            if os.path.splitext(name)[1] == '.py':
                filepath = os.path.join(root, name)
                check(filepath, rgx_map[chk_type])

if __name__ == "__main__":
    main()
