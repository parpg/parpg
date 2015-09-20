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

import Image
import getopt
import logging
import os
import sys

log = logging.getLogger("scaler")
log.setLevel(logging.DEBUG)

def scaleImage(filename, scale=100):
    """ Opens an image, and scales it to a width of slice_width pixes, keeping aspect
        ratio
        @type filename: String
        @param filename: Pathname of the image to open
        @type scale: Integer 
        @param scale: Width of the final image
        @rtype: Bool
        @return True on success, false on failure. """
    
    if not os.path.isfile(filename):
        log.info("File does not exist: %s", filename)
        return False
    
    img = Image.open(filename)
    log.debug("Loaded file: %s", filename)

    # Create the slice
    copy_image = img.copy()

    # Crop and trim it
    (width,height) = copy_image.size
    
    log.debug("original image: %d x %d" % (width, height))
    new_height = int((float(scale)/float(width)) * float(height))
    log.debug("scaling to %d %d" % (scale, new_height))
    # PIL wants (left, upper, right, lower)
    new_image = copy_image.resize((scale, new_height))

    #new_image.trim() - hard to reimplement in PIL

    # Obtain the filename 
    (name,ext) = os.path.splitext(filename)
    new_filename = name + "_scaled" + ext 
    log.debug("Going to write scaled image %s" %(new_filename))
    new_image.save(new_filename)
    log.info("Wrote %s",new_filename)
    return True 
        
    
def usage():
    """ Prints the help message. """
    print "Usage: %s [options] file1 file2..." % sys.argv[0]
    print "Options:"
    print "   --verbose, -v      Verbose"
    print "   --help, -h         This help message"
    print "   --size -s SIZE     Width size in pixels (default 100)"
    
def main(argv):
    """ Main function, parses the command line arguments 
    and launches the image scaling logic. """

    try:
        opts, args = getopt.getopt(argv, "hvs:", 
        ["help","verbose","size"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    scale = 100 
    # default scale in pixels
    for opt, arg in opts:        
       if opt in ("-v","--verbose"):
            ch.setLevel(logging.DEBUG)
       elif opt in ("-s","--size"):
            try:
                check = str(int(arg))
            except:
                print "%s not an int for size parameter" % arg
                sys.exit(2)           
            scale = int(arg)
       elif opt in ("-h","--help"):
            usage()
            sys.exit()
    
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    
    for file in args:
        if scaleImage(file, scale):
            log.info("Done scaling %s" % file)
        else:
            log.info("Aborted %s" % file)
    
if __name__ == '__main__':
    main(sys.argv[1:])
