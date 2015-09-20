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

import sys,cPickle
from xml.sax import make_parser
from xml.sax.handler import ContentHandler 

# this code is for building the transition layer for the map
# the world map is built of two layers: one for the world floor, and the other
# for the all the objects (including the player and NPC)
# This program accepts one argument, the original XML map file,
# and outputs another file with 1 or more added layers: the layers holding
# the information for the transition tiles that are rendered over the ground

# usage: transition.py mapfile
# outputs file new.xml, a simple text file that contains ONLY the new layers
# needed in the mapfile. At the moment you have to splice these in by hand;
# they must come AFTER the ground layer but BEFORE the building and objects
# layers. PM maximinus at the PARPG forums if any questions.

# some simple defines for each part of the tile
TOP             =   1
RIGHT           =   2
BOTTOM          =   4
LEFT            =   8
TOP_LEFT        =   16
TOP_RIGHT       =   32
BOTTOM_RIGHT    =   64
BOTTOM_LEFT     =   128

# side transition tiles always block corner tiles
# but which ones?
TOP_BLOCK       =   TOP_RIGHT+TOP_LEFT
RIGHT_BLOCK     =   TOP_RIGHT+BOTTOM_RIGHT
BOTTOM_BLOCK    =   BOTTOM_RIGHT+BOTTOM_LEFT
LEFT_BLOCK      =   TOP_LEFT+BOTTOM_LEFT
NONE            =   0

# now for each of the 15 different possible side variations we
# can know what corner pieces do not need to be drawn
# this table stores all of the allowed combinations
# based on the bit pattern for the side elements

CORNER_LOOKUP   =   [BOTTOM_BLOCK,  LEFT_BLOCK,
                     BOTTOM_LEFT,   TOP_BLOCK,
                     NONE,          TOP_LEFT,
                     NONE,          RIGHT_BLOCK,
                     BOTTOM_RIGHT,  NONE,
                     NONE,          TOP_RIGHT,
                     NONE,          NONE,
                     NONE]

class XMLTileData:
    def __init__(self, x, y, z, o, i=None):
        self.x = x
        self.y = y
        self.z = z
        self.object = o
        self.ident = i

class XMLLayerData:
    """Class to store one complete layer"""
    def __init__(self, x, y, name):
        self.x_scale = x
        self.y_scale = y
        self.name = name
        self.tiles = []

class LocalXMLParser(ContentHandler):
    """Class inherits from ContantHandler, and is used to parse the
       local map data"""
    def __init__(self):
        self.search = "map"
        self.layers = []
        self.current_layer = False
        self.final = []
    
    def startElement(self, name, attrs):
        """Called every time we meet a new element"""
        # we are only looking for the 'layer' elements, the rest we ignore
        if(name == "layer"):
            # grab the data and store that as well
            try:
                x = attrs.getValue('x_scale')
                y = attrs.getValue('y_scale')
                name = attrs.getValue('id')
            except(KeyError):
                sys.stderr.write("Error: Layer information invalid")
                sys.exit(False)
            # start a new layer
            self.layers.append(XMLLayerData(x, y, name))
            self.current_layer = True
        elif(name == "i"):
            # have a current layer?
            if self.current_layer == False:
                sys.stderr.write("Error: item data outside of layer\n")
                sys.exit(False)
            # ok, it's ok, let's parse and add the data
            try:
                x = attrs.getValue('x')
                y = attrs.getValue('y')
                z = attrs.getValue('z')
                o = attrs.getValue('o')
            except(KeyError):
                sys.stderr.write("Error: Data missing in tile definition\n")
                sys.exit(False)
            try:
                i = attrs.getValue('id')
            except(KeyError):
                i = None
            # convert tile co-ords to integers
            x = float(x)
            y = float(y)
            z = float(z)
            # now we have the tile data, save it for later
            self.layers[-1].tiles.append(XMLTileData(x, y, z, o, i))

    def endElement(self, name):
        if(name == "layer"):
            # end of current layer
            self.current_layer=False

class LocalMap:
    def __init__(self):
        self.layers = []
        self.ttiles = []
        self.render_tiles =[]
        self.min_x = 0
        self.max_x = 0
        self.min_y = 0
        self.max_y = 0

    def outputTransLayer(self, l_file, l_count):
        if(len(self.render_tiles) == 0):
            return True
        try:
            layer_name = "TransitionLayer" + str(l_count)
            l_file.write('''    <layer x_offset="0.0" pathing="''')
            l_file.write('''cell_edges_and_diagonals" y_offset="0.0"''')
            l_file.write(''' grid_type="square" id="''')
            l_file.write(layer_name + '''"''')
            l_file.write(''' x_scale="1" y_scale="1" rotation="0.0">\n''')
            l_file.write('        <instances>\n')
            for tile in self.render_tiles:
                l_file.write('''            <i x="''')
                l_file.write(str(tile.x))
            	l_file.write('''" o="''')
            	l_file.write(tile.object)
            	l_file.write('''" y="''')
            	l_file.write(str(tile.y))
            	l_file.write('''" r="0" z="0.0"></i>\n''')
            l_file.write('        </instances>\n    </layer>\n')
        except(IOError):
            sys.stderr.write("Error: Couldn't write data")
            return False
        return True

    def GetSurroundings(self, x, y, search):
        """Function called by buildTransLayer to see if a tile needs to
           display transition graphics over it (drawn on another layer)"""
        # check all of the tiles around the current tile
        value=0
        if(self.pMatchSearch(x,y+1,search) == True):
            value += RIGHT
        if(self.pMatchSearch(x-1,y+1,search) == True):
            value += BOTTOM_RIGHT
        if(self.pMatchSearch(x-1,y,search) == True):
            value += BOTTOM
        if(self.pMatchSearch(x-1,y-1,search) == True):
            value += BOTTOM_LEFT
        if(self.pMatchSearch(x,y-1,search) == True):
            value += LEFT
        if(self.pMatchSearch(x+1,y-1,search) == True):
            value += TOP_LEFT
        if(self.pMatchSearch(x+1,y,search) == True):
            value += TOP
        if(self.pMatchSearch(x+1,y+1,search) == True):
            value += TOP_RIGHT
        return value

    def getTransitionTiles(self, search):
        """Build up and return a list of the tiles that might
           need a transition tiles layed over them"""
        size = len(search)
        tiles = []
        for t in self.layers[0].tiles:
            # we are only interested in tiles that DON'T have what we are
            # are looking for (because they might need a transition gfx)
            if(t.object != None and t.object[:size] != search):
                # whereas now we we need to check all the tiles around
                # this tile
                trans_value = self.GetSurroundings(t.x, t.y, search)
                if(trans_value != 0):
                    # we found an actual real transition
                    tiles.append([t.x, t.y, trans_value])
        return tiles

    def getTransitionName(self, base, value, corner=False):
        if(corner == False):
            name = base + "-ts"
        else:
            name = base + "-tc"
        if(value < 10):
            name += "0"
        name += str(value)
        return name

    def buildTransLayer(self, search):
        """Build up the data for a transition layer
           search is the string that matches the start of the name of
           each tile that we are looking for"""
        transition_tiles = self.getTransitionTiles(search)       
        # now we have all the possible tiles, lets see what they
        # actually need to have rendered
        for t in transition_tiles:
            # first we calculate the side tiles:
            sides = (t[2]&15)
            if(sides != 0):
                # there are some side tiles to be drawn. Now we just
                # need to see if there are any corners to be done
                corners = (t[2]&240)&(CORNER_LOOKUP[sides-1])                    
                if(corners != 0):
                    # we must add a corner piece as well
                    corners = corners/16
                    name = self.getTransitionName(search, corners, True)
                    self.ttiles.append(XMLTileData(t[0], t[1], 0, name))
                # add the side tile pieces
                name = self.getTransitionName(search, sides, False)
                self.ttiles.append(XMLTileData(t[0], t[1], 0, name))
            else:
                # there are no side tiles, so let's just look at
                # the corners (quite easy):
                corners = (t[2]&240)/16
                if(corners != 0):
                    # there is a corner piece needed
                    name = self.getTransitionName(search, corners, True)
                    self.ttiles.append(XMLTileData(t[0], t[1], 0, name))

    def loadFromXML(self, filename):
        """Load a map from the XML file used in Fife
           Returns True if it worked, False otherwise"""
        try:
            map_file = open(filename,'rt')
        except(IOError):
            sys.stderr.write("Error: No map given!\n")
            return(False)
        # now open and read the XML file
        parser = make_parser()
        cur_handler = LocalXMLParser()
        parser.setContentHandler(cur_handler)
        parser.parse(map_file)
        map_file.close()
        # make a copy of the layer data
        self.layers = cur_handler.layers
        return True
    
    def getSize(self):
        """getSize stores the size of the grid"""
        for t in self.layers[0].tiles:
            if t.x > self.max_x:
                self.max_x = t.x
            if t.x < self.min_x:
                self.min_x = t.x
            if t.y > self.max_y:
                self.max_y = t.y
            if t.y < self.min_y:
                self.min_y = t.y
    
    def checkRange(self, x, y):
        """Grid co-ords in range?"""
        if((x < self.min_x) or (x > self.max_x) or \
           (y < self.min_y) or (y > self.max_y)):
           return False
        return True

    def pMatchSearch(self, x, y, search):
        """Brute force method used for matching grid"""
        # is the tile even in range?
        if(self.checkRange(x, y) == False):
            return False
        size = len(search)
        for t in self.layers[0].tiles:
            if((t.x == x) and (t.y == y) and (t.object[:size] == search)):
                return(True)
        # no match
        return False

    def coordsMatch(self, x, y, tiles):
        """Helper routine to check wether the list of tiles
           in tiles has any contain the coords x,y"""
        for t in tiles:
            if((t.x == x) and (t.y == y)):
                return True
        # obviously no match
        return False

    def saveMap(self, filename):
        """Save the new map"""
        # open the new files for writing
        try:
            map_file = open(filename, 'wt')
        except(IOError):
            sys.stderr.write("Error: Couldn't save map\n")
            return(False)
        # we don't know how many layers we need, let's do that now
        # this is a brute force solution but it does work, and speed
        # is not required in this utility
        layer_count = 0
        while(self.ttiles != []):
            recycled_tiles = []
            self.render_tiles = []
            for t in self.ttiles:
                if(self.coordsMatch(t.x, t.y, self.render_tiles) == False):
                    # no matching tile in the grid so far, so add it
                    self.render_tiles.append(t)
                else:
                    # we must save this for another layer
                    recycled_tiles.append(t)
            # render this layer
            if(self.outputTransLayer(map_file, layer_count) == False):
                return False
            layer_count += 1
            self.ttiles = recycled_tiles
        # phew, that was it
        map_file.close()
        print "Output new file as new.xml"
        print "Had to render", layer_count, "layers"
        return True
    
    def printDetails(self):
        """Debugging routine to output some details about the map
           Used to check the map loaded ok"""
        # display each layer name, then the details
        print "Layer ID's:",
        for l in self.layers:
            print l.name,
        print "\nMap Dimensions: X=", (self.max_x-self.min_x) + 1,
        print " Y=", (self.max_y-self.min_y) + 1

if __name__=="__main__":
    # pass a map name as the first argument
    if(len(sys.argv) < 2):
        sys.stderr.write("Error: No map given!\n")
        sys.exit(False)
        
    new_map = LocalMap()
    if(new_map.loadFromXML(sys.argv[1]) == True):
        new_map.getSize()
        new_map.buildTransLayer("grass")
        new_map.saveMap("new.xml")
        new_map.printDetails()

