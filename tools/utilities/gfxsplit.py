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
#   along with PARPG.  If not, see <http://www.gnu.org/licenses/>

import sys
import pygame

# place defines here

TILE_WIDTH  =   72
TILE_HEIGHT =   36
# is this is true, output a file of the pics together in the current folder
STITCH      =   False

# this is very much a simple routine, but we still have a simple class

class TileImage:
    def __init__(self, picture, name, y_off):
        self.image = picture
        self.filename = name
        self.y_offset = y_off

def writeXML(name, y_off):
    """Write the XML file as well
       Always the same small file so we do it automatically"""
    # we need to strip off the entire path up to the last
    # TODO: this code will not work on windows
    # strip off the png part and replace with the XML
    filename = name.split('/')[-1]
    if(filename == name):
        filename = name.split('\\')[-1]
    x_file = open(name[:-4]+".xml","wt")
    x_file.write('''<?fife type="object"?>\n''')
    x_file.write('''<object id="''')
    x_file.write(filename[:-4])
    x_file.write('''" namespace="PARPG" blocking="1" static="1">\n''')
    x_file.write('''    <image source="''')
    x_file.write(filename)
    x_file.write('''" direction="0"''')
    x_file.write(''' y_offset="''')
    x_file.write(y_off)
    x_file.write('''" />\n''')
    # the \n\n is ESSENTIAL otherwise the XML parser in FIFE craps out!
    x_file.write('''</object>\n\n''')
    x_file.close()

def stitchImages(files, width, height):
    """Put the images together and output them to stitched.png"""
    new_image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    x_pos = 0
    for i in files:
        new_image.blit(i.image, (x_pos, 0))
        x_pos += i.image.get_width()
    pygame.image.save(new_image, "stitched.png")
    
def saveFiles(files):
    """Given a list of TileImages, output them as seperate files
       Returns True if it worked"""
    # files is a list of TileImages
    complete = []
    width = 0
    height = 0
    for i in files:
        width += i.image.get_width()
        if(i.image.get_height() > height):
            height = i.image.get_height()
        try:
            pygame.image.save(i.image, i.filename)
            # output the XML file as well
            writeXML(i.filename, str(i.y_offset))
        except(IOError):
            print "Error: Failed to save",i.filename
            # if we saved some anyway, then tell the user
            if(complete != []):
                print "  Managed to save",
                for name in complete:
                    print name,
                print "\n"
            return False
        complete.append(i.filename)
    # seems like all was ok
    if(STITCH == True):
        stitchImages(files, width, height)
    return True
            
def splitImage(image, filename, data):
    """Quite complex this, as there are many differing layouts on the
       hexes that we could be dealing with. We blit from left to right
       data holds the hex position changes in [x,y] format.
       by one and the y value staying the same (on the grid map)"""
    # the starting point for the grab is always the middle of the image
    height = (image.get_height() / 2) + (TILE_HEIGHT / 2)
    width = 0
    x_pos = 0
    file_counter = 0
    tiles = []
    height_adjust = 0
    y_off_next = -((height - TILE_HEIGHT) / 2)
    for t in data:
        y_off = y_off_next
        if(t == 'm'):
            # switchback, so this tile must fill the whole width
            width += TILE_WIDTH / 2
            height_adjust = TILE_HEIGHT / 2
            y_off_next += (TILE_HEIGHT / 4) + (TILE_HEIGHT / 2)
            xoff = 0
        elif(t == 'r'):
            # moving forward on the y axis
            width = TILE_WIDTH / 2
            height_adjust = - (TILE_HEIGHT / 2)
            y_off_next += TILE_HEIGHT / 4
            xoff = TILE_WIDTH / 2
        elif(t == 'l'):
            # moving forward on the x axis
            width = TILE_WIDTH / 2
            height_adjust = TILE_HEIGHT / 2
            y_off_next -= TILE_HEIGHT / 4
            xoff = 0
        else:
            # TODO: Handle integer moves (i.e. > 1 tile up down)
            print "Error: Can't handle integer tile moves yet"
            sys.exit(False)
        # if the image is 256, then adjust
        # bug in the FIFE OpenGL code
        if(height == 256):
            height += 1
        # build the new surface
        new_surface = pygame.Surface((TILE_WIDTH, height), \
                                     pygame.SRCALPHA, 32)
        # now blit a strip of the image across
        new_surface.blit(image, (0+xoff, 0), pygame.Rect(x_pos, 0, \
                                                         width, height))
        # store the image for later
        tiles.append(TileImage(new_surface, \
            filename + chr(ord('a')+file_counter) + ".png",y_off))
        file_counter += 1
        # amend variables
        x_pos += width
        height += height_adjust
    return tiles
            
def convertFiles(filename, txt_data):
    """Take a file, slice into seperate images and then save these new images
       as filename0, filename1 ... filenameN
       Returns True if everything worked
       The second string gives the offsets from left to right. The first tile
       on the LHS MUST be in the centre of the image"""
    # first we need to ensure that the data sent is correct. split it up first
    data=[]
    for i in txt_data:
        data.append(i)
    if(len(data) < 2):
        print "Error: Invalid tile data layout"
        return False
    # validate each data statement
    for i in data:
        if((i != 'l')and(i != 'r')and(i != 'm')and(i.isdigit() == False)):
            # some issue
            print "Error: Can't decode tile string structure"
            return False
    # then load the file
    try:
        image = pygame.image.load(filename)
    except(pygame.error):
        print "Error: Couldn't load", filename
        return False        
    # split into seperate files
    # the [:-4] is used to split off the .png from the filename
    images = splitImage(image, filename[:-4], data)
    # save it and we are done
    if(images == []):
        # something funny happened
        print "Error: Couldn't splice given image file"
        return False
    return(saveFiles(images))

if __name__=="__main__":
    # check we have some options
    if(len(sys.argv) < 3):
        sys.stderr.write("Error: Not enough data given\n")
        sys.exit(False)
    # ok, so init pygame and do it
    pygame.init()
    sys.exit(convertFiles(sys.argv[1], sys.argv[2]))

