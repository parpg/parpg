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
import re

log = logging.getLogger("agentxml")
log.setLevel(logging.DEBUG)

def generateAgent(path, delay, x_off, y_off):
    """ Generates the agent XML file and creates animation
    XML files for found children. 
    @type path: string 
    @param path: Agent path 
    @type delay: string
    @param delay: Animation delay (used in animation.xml)
    @type x_off: string
    @param x_off: X offset (used in animation.xml)
    @type y_off: string
    @param y_off: Y offset (used in animation.xml)
    @return True on success, False on failure
    """
    # Name is the last subdirectory 
    name=os.path.split(os.path.abspath(path))[1]
    log.debug("Doing animation for agent: %s", name)

    f = open(os.path.join(path,name + ".xml"), 'w')            
    log.debug("Opened " + os.path.join(path,name + ".xml"))
    f.write('<?fife type="object"?>\n')
    f.write('<object id="%s" namespace="PARPG" blocking="1" static="0">\n' % \
            (name,))

    # Iterate the animations 
    anims = os.listdir(path)
    anims.sort()
    for anim in anims:
        anim_path=os.path.join(path,anim)
        if os.path.isdir(anim_path) and anim.find("svn")==-1:
            log.debug("Found animation: %s", anim)
            f.write('\t<action id="' + anim +'">\n')
            angles = os.listdir(anim_path)
            angles.sort()
            for angle in angles:
                angle_path=os.path.join(anim_path,angle)
                if os.path.isdir(angle_path) and angle.find("svn")==-1:
                    log.debug("Found angle: %s", angle)
                    f.write('\t\t<animation source="' + anim + '/' + angle 
                            + '/animation.xml" direction="' 
                            + str(int(angle)) + '" />\n')
                    if not generateAnimation(angle_path,delay,x_off,y_off):
                        log.error("Failed to create animation for " + anum\
                                   + " (angle: " + angle + ")")
            f.write('\t</action>\n')
    f.write('</object>\n')
    f.close()
    log.info("Wrote " + os.path.join(path,name + ".xml"))
    return True

def imageCompare(x,y):
    """ Compares two filenames containing a number 
    @type x: string
    @param x: First filename
    @type y: string
    @param y: second filename
    @return 1 of x>y, 0 when x==y,  -1 when y<x.
    """
    regex="[^0-9]*([0-9]*).*"
    try:
        int_x = int(re.sub(regex,"\\1",x))
    except:
        int_x = -1

    try:
        int_y = int(re.sub(regex,"\\1",y))
    except:
        int_y = -1
    
    if int_x > int_y:
        return 1
    elif int_x < int_y:
        return -1;
    
    return 0

def generateAnimation(path, delay, x_off, y_off):
    """ Generate animation.xml for a given path.
    @type path: string 
    @param path: Agent path 
    @type delay: string
    @param delay: Animation delay 
    @type x_off: string
    @param x_off: X offset 
    @type y_off: string
    @param y_off: Y offset 
    @return True on success, False on failure """

    (tmp, angle) = os.path.split(os.path.abspath(path))
    (tmp, anim) = os.path.split(tmp)
    (tmp, agent) = os.path.split(tmp)
    id = "%s:%s:%s"%(agent, anim, angle)
    log.debug("Doing animation with id: %s" % (id))

    images = os.listdir(path)
    # Get those with the correct extension
    images_filtered = []
    for image in images:
        if image.endswith(".png"):
            images_filtered.append(image)


    f = open(os.path.join(path,"animation.xml"), 'w')    
    log.debug("Opened: " + os.path.join("animation.xml"))
    f.write('<animation delay="' + delay + '" namespace="PAPRG" id="' + id 
            + '" x_offset="' + x_off 
            + '" y_offset="' + y_off + '">\n')

    # Sort them
    images_filtered.sort(cmp=imageCompare)
    for image in images_filtered:
        log.debug("Found image: %s" % image)
        f.write('\t<frame source="' + image + '" />\n')

    f.write('</animation>\n')
    f.close()
    log.info("Wrote: " + os.path.join(path,"animation.xml"))
    return True 

def usage():
    """ Prints the help message. """
    print "Usage: %s [options]" % sys.argv[0]
    print "Options:"
    print "   --verbose, -v      Verbose"
    print "   --help, -h         This help message"
    print "   --path DIR, -p     Root path of the agent (default .)"
    print "   --delay DLY, -d    Delay value (default 100)"
    print "   --x_offset OFF, -x X Offset (default 0)"
    print "   --y_offset OFF, -y Y Offset (default 0)"

def main(argv):
    """ Main function, parses the command line arguments 
    and launches the xml file creation logic. """

    try:
        opts, args = getopt.getopt(argv, "hp:d:x:y:v", 
        ["help","path","delay", "x_offset", "y_offset", "verbose"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    agent_path = "."
    delay = "100"
    x_offset = "0"
    y_offset = "0"
    verbose = False

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    for opt, arg in opts:        
        if opt in ("-p","--path"):
            agent_path = path
        elif opt in ("-d","--delay"):
            delay = arg
        elif opt in ("-x","--x_offset"):
            x_offset = arg
        elif opt in ("-y","--y_offset"):
            y_offset = arg
        elif opt in ("-v","--verbose"):
            ch.setLevel(logging.DEBUG)
        else:
            usage()
            sys.exit()

    formatter = logging.Formatter("%(levelname)s: %(message)s")
    ch.setFormatter(formatter)
    log.addHandler(ch)

    log.debug("Going to generate animation for %s" % (agent_path))
    generateAgent(agent_path, delay, x_offset, y_offset)
    log.info("Done");

if __name__ == '__main__':
    main(sys.argv[1:])
