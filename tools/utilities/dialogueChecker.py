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

import os
import sys
import getopt
import logging

import sys
sys.path = ['../parpg'] + sys.path


from dialoguevalidator import DialogueValidator, DialogueFormatException

log = logging.getLogger("dialoguevalidator")
log.setLevel(logging.DEBUG)

def usage():
    """ Prints the help message. """
    print "Usage: %s [options]" % sys.argv[0]
    print "Options:"
    print "   --help, -h         This help message"
    print "   --file FILE, -f    Yaml file to validate (default dialogue.yaml)"
    print "   --root ROOT, -r    Root path to which all files are checked"

def main(argv):
    """ Main function, parses the command line arguments 
    and launches the dialogue validator. """

    try:
        opts, args = getopt.getopt(argv, "hf:r:", 
        ["help","file", "root"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    yaml_file = "dialogue.yaml"
    topdir = "."

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    for opt, arg in opts:        
        if opt in ("-f","--file"):
            yaml_file = arg
        elif opt in ("-r","--root"):
            topdir = arg
        else:
            usage()
            sys.exit()

    formatter = logging.Formatter("%(levelname)s: %(message)s")
    ch.setFormatter(formatter)
    log.addHandler(ch)

    log.info("Going to validate file %s" % (yaml_file))
    log.info("Searching for files relative to %s" % (topdir))
    val = DialogueValidator()
    try:
        val.validateDialogueFromFile(yaml_file, topdir)
        log.info("Done");
    except DialogueFormatException as dfe:
        log.info("Error found in file !")
        log.info("Error was: %s" % (dfe))


if __name__ == '__main__':
    main(sys.argv[1:])
