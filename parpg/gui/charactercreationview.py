from fife.extensions import pychan
from fife.extensions.pychan.widgets import Label, HBox

from parpg import vfs
from parpg.gui.spinner import IntSpinner

class CharacterCreationView(object):
    def __init__(self, xml_script_path='gui/character_creation.xml'):
        xml_file = vfs.VFS.open(xml_script_path)
        self.gui = pychan.loadXML(xml_file)
    
    def createStatisticList(self, statistics):
        statistics_list = self.gui.findChild(name='statisticsList')
        # Start with an empty list.
        statistics_list.removeAllChildren()
        for statistic in statistics:
            name = statistic.long_name
            hbox = HBox()
            hbox.opaque = 0
            label = Label(text=name)
            spinner = IntSpinner(lower_limit=0, upper_limit=100)
            hbox.addChildren(label, spinner)
            statistics_list.addChildren(hbox)
    
    def createTraitsList(self, traits):
        pass
    
    def updateMessageArea(self, message):
        message_area = self.gui.findChild(name='messageArea')
        message_area.text = unicode(message)