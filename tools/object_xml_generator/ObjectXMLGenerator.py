"""Generates FIFE object XML for an animation or static object.

Only suitable for new objects, as x and y offset's are not recognized.
After generation, tweaking of the x and y offset's will be needed For
proper positioning.
"""
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as md


class GenerateXML(object):
    """Defines methods to be inherited for StaticXML and AnimationXML"""

    def writeXML(self, element, file_, object=True):
        """Write pretty XML to file.
        
        @type element: xml.etree.ElementTree.Element
        @param element: Root Element containing XML to write to file
        @type file_: file
        @param file_: File to write XML to
        @type object: bool
        @param object: Used to differentiate between objects and animations
        """
        try:
            xml_text = md.parseString(ET.tostring(element)).toprettyxml()
            xml_text = xml_text.split('\n')
            if object:
                xml_text[0] = '<?fife type="object"?>'
                file_.write('\n'.join(xml_text))
            else:
                file_.write('\n'.join(xml_text[1:]))
        finally:
            file_.close()
            print "XML written to " + file_.name
        
class AutoAnimationXML(GenerateXML):
    """Generate the XML for an animated object"""
    def __init__(self, path, name=None, blocking='1', namespace='PARPG',
                 x_offset='0', y_offset='0', delay='100', **kwargs):
        """
        @type path: str
        @param path: Path of object to define
        @type name: str
        @param name: Name of object to define
        @type blocking: str
        @param blocking: '1' if the object is blocking
        @type namespace: str
        @param namespace: namespace of the object
        @type x_offset: str
        @param x_offset: x_offset of the animation
        @type y_offset: str
        @param y_offset: y_offset of the animation
        @type delay: str
        @param delay: Delay between animation frames
        """
        self.ROOT_PATH = path
        if name == None:
            name = os.path.basename(path)
        print name
        self.TOP_ATTRIB = {'blocking': blocking, 'namespace': namespace, 
                           'id': name, 'static': static, 'x_offset': x_offset,
                           'y_offset': y_offset}
        self.TOP_ATTRIB.update(kwargs)
        self.actions = {}
        self.findActions()
        self.findRotations()
        self.makeXML()

    def findActions(self):
        """Determine the actions in the root directory."""
        for item in os.listdir(self.ROOT_PATH):
            path_to_item = os.path.join(self.ROOT_PATH, item)
            if item == '.svn':
                continue
            if os.path.isdir(path_to_item):
                self.actions[item] = [path_to_item]

    def findRotations(self):
        """Determine the rotations in all the actions."""
        for action in self.actions:
            for rotation in os.listdir(self.actions[action][0]):
                if rotation != '.svn':
                    self.actions[action].append(rotation)

    def autoMakeXML(self):
        """Generate top and bottom XML for the object."""
        self.makeTopXML()
        self.makeBottomXML()

    def makeTopXML(self):
        """Make the XML for the object."""
        root_element = ET.Element("object", self.TOP_ATTRIB)
        for action in self.actions:
            sub = ET.SubElement(root_element, "action", {"id": action})
            for rotation in sorted(self.actions[action][1:]):
                path = os.path.join(action, rotation, "animation.xml")
                ET.SubElement(sub, "animation", {"source": path,
                                                 "direction": rotation})
        xml_file = open(os.path.join(self.ROOT_PATH, 
                                    "%s.xml" % self.TOP_ATTRIB['id']), "w")
        self.writeXML(root_element, xml_file)
        print "Making top XML in %s" % self.ROOT_PATH
    
    def makeBottomXML(self):
        """Make XML for the actions."""
        for action, rotations in self.actions.iteritems():
            for i in range(1, 9):
                name = "%s:%s:%s" % (self.TOP_ATTRIB['id'], action, 
                                     rotations[i])
                root_element = ET.Element("animation", {"delay":self.delay,
                                          "namespace":"PARPG",
                                          "id": name, "x_offset": "0",
                                          "y_offset": "0"})
                path = os.path.join(self.ROOT_PATH, action, rotations[i])
                image_list = sorted([image for image in os.listdir(path) if
                                     image.endswith(".png")],
                                     key=lambda f: self.frameNum(f))
                for image in image_list:
                    ET.SubElement(root_element, "frame", {"source": image})
                xml_file = open(os.path.join(path, "animation.xml"), "w")
                self.writeXML(root_element, xml_file, False)
    def frameNum(self, name):
        """Get the frame number of an image.
        
        @type name: str
        @param name: File name to get number of
        """
        return int(name.split('_')[-1].split('.')[0])

class AutoStaticXML(GenerateXML):
    """Generate XML definition for a static object"""
    
    def __init__(self, path, id=None, blocking='1', namespace='PARPG',
                 x_offset='0', y_offset='0', **kwargs):
        """
        @type path: str
        @param path: Directory to generate XML inside of.
        @type id: str
        @param id: Name of the object
        @type blocking: str
        @param blocking: 1 or 0, specifies if the item is blocking
        @type namespace: str
        @param namespace: Namespace of object, always PARPG
        @type x_offset: str
        @param x_offset: Define the x_offset of the object
        @type y_offset: str
        @param y_offset: Define the y_offset of the object
        """
        if id is None:
            id = '_'.join(os.path.split(path)[1].split("_")[:-1])

        self.TOP_ATTRIB = {'id': id, 'blocking': blocking,
                           'namespace': namespace, 'x_offset': x_offset,
                           'y_offset': y_offset, 'static': '0'}
        self.TOP_ATTRIB.update(kwargs)
        self.ROOT_PATH = path
        self.dirStructure(path)

    def readDirectories(self, path, type_dict):
        """Find all .png files in a directory and sub-directories.
        
        @type path: str
        @param path: Path of directory to read
        @type type_list: dict
        @param type_list: Dictionary to add directories and filenames to
        """
        for item in os.listdir(path):
            path_to_item = os.path.join(path, item)
            if item == ".svn": # Ignore .svn directories
                continue
            elif os.path.isdir(path_to_item):
                type_dict[item] = ["dir", path_to_item]
            elif item.endswith(".png"):
                type_dict[item] = ["bottom", path]
        
    def dirStructure(self, path, type_dict=None):
        """Generate XML definitions for all the .pngs in the root directory.
        
        @type type_dict: dict
        @param type_dict: Stores content of directory
        @type path: str
        @param path: Path to search
        """
        if type_dict == None:
            type_dict = {}
        if path == None:
            path = self.ROOT_PATH
        self.readDirectories(path, type_dict)
        for item in type_dict:
            if type_dict[item][0] == 'dir':
                sub_dict = {}
                self.dirStructure(type_dict[item][1], sub_dict)
            else:
                if os.path.basename(path).isdigit():
                    pass
                else:
                    self.makeXML(os.path.join(type_dict[item][1], item))
                break
            
    def makeXML(self, path):
        """Make the XML definitions for static objects.
        
        @type path: str
        @param path: Path containing images to make XML for
        """
        # The id attribute:
        # For a path of '/blah/blah/blah/object_name/shopping_trolley_000.png'
        # Will extract shopping_trolley_000.png, and then proceed to
        # Split it at the "_", take everything but the last element, 
        # which would be 000.png in the case, and then rejoin them
        # together to get the ID name. the above example,
        # id = 'shopping_trolley'
        xml_file_name = os.path.join(os.path.split(path)[0], id + '.xml')
        xml_file = open(xml_file_name, 'w')
        root_element = ET.Element("object", self.TOP_ATTRIB)
        images = sorted([item for item in os.path.split(path)[0]
             if item.endswith('.png')])
        for item in images:
            # The direction attribute:
            # Item is something like red_d_trolley_045.png
            # item.split("_")[-1] = "045.png"
            # "045.png".split(".")[0] = "045", which would be the rotation
            direction = item.split("_")[-1].split(".")[0]
            ET.SubElement(root_element, "image", {"direction": direction,
                                                      "source": item,
                                                     "x_offset": x_offset,
                                                     "y_offset": y_offset})
        
        self.writeXML(root_element, xml_file)
