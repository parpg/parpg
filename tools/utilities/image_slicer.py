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

log = logging.getLogger("splicer")
log.setLevel(logging.DEBUG)

def saveSlice(img, filename, num, left, right, slice_width):
    """ Takes a slice out of the image passed. This slice is defined by
        left and righ and will be saved as filename extended with num before 
        the prefix.
        @type img: Image.new
        @param img: Source image to take the slice from
        @type filename: String
        @param filename: Base filename
        @type num: Integer 
        @param nun: Suffix for the filename
        @type left: Integer 
        @param left: Left boundary of the slice 
        @type right: Integer 
        @param right: Right boundary of the slice
        @type slice_width: Integer
        @param slice_width: The desired width of a slice, trimmed images will be
        extended to this width.
        @rtype: Boolean
        @return True on success, False on failure """         

    # Create the slice
    copy_image = img.copy()

    # Crop and trim it
    (width,height) = copy_image.size
    if (right > width):
        right = width
    log.debug("size: %d %d %d %d" % (0,left,right,height))
    # PIL wants (left, upper, right, lower)
    new_image = copy_image.crop((left,\
                                 0,\
                                 right,\
                                 height))

    #new_image.trim() - hard to reimplement in PIL

    # Obtain the filename 
    (name,ext) = os.path.splitext(filename)
    new_filename = name + str(num) + ext 
    log.debug("Going to write slide %d to %s" %(num,new_filename))
    new_image.save(new_filename)
    log.info("Wrote %s",new_filename)
    return True 
        
def sliceImage(filename, slice_width=72, tail_width=108):
    """ Opens an image, and produces slice_width pixel wide slices of it
        @type filename: String
        @param filename: Pathname of the image to open
        @type slice_width: Integer 
        @param slice_width: Width of the slices that should be made
        @rtype: Bool
        @return True on success, false on failure. """
    
    if not os.path.isfile(filename):
        log.info("File does not exist: %s", filename)
        return False
    
    img = Image.open(filename)
    log.debug("Loaded file: %s", filename)
    (img_width,img_height) = img.size
    log.debug("Image geometry before trim %dx%d", img_width, img_height)
    
    #img.trim()  No trim support in PIL
    #img_width = img.size.width
    #img_height = img.size.height
    #log.debug("Image geometry after trim %dx%d", img_width, img_height)
    
    current_pos = 0
    num = 0
    while current_pos + slice_width < img_width:
        remainder = img_width - current_pos
        log.info("Remainder: %d" % remainder)
        if remainder < tail_width + slice_width:
            break
        # Save the slice 
        if not saveSlice(img, filename, num, current_pos, \
                         current_pos + slice_width, slice_width):
            log.info("Failed to save slice: %d", num)
            return False 
        num = num + 1
        current_pos += slice_width 
    
    # Handle the tail tail is now bigger
    if(current_pos < img_width):
        if not saveSlice(img, filename, num, current_pos, \
                         img_width-1, slice_width):
            log.info("Failed to save tail slice: %d", num)
            return False 
    return True
    
def usage():
    """ Prints the help message. """
    print "Usage: %s [options]" % sys.argv[0]
    print "Options:"
    print "   --verbose, -v      Verbose"
    print "   --help, -h         This help message"
    print "   --file FILE, -f    File to splice"
    
def main(argv):
    """ Main function, parses the command line arguments 
    and launches the splicing logic. """

    try:
        opts, args = getopt.getopt(argv, "hf:v", 
        ["help","file", "verbose"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    file = ""
    for opt, arg in opts:        
        if opt in ("-f","--file"):
            file = arg
        elif opt in ("-v","--verbose"):
            ch.setLevel(logging.DEBUG)
        else:
            usage()
            sys.exit()
    
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    
    if sliceImage(file, 72, 36):
        log.info("Done")
    else:
        log.info("Aborted")
    
if __name__ == '__main__':
    main(sys.argv[1:])
