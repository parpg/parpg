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
import sys
import os
import logging

from fife.extensions import pychan
from fife.extensions.pychan import widgets

from parpg import vfs

logger = logging.getLogger('filebrowser')

def u2s(string):
    # TODO: cryptic function name
    return string.encode(sys.getfilesystemencoding())

class FileBrowser(object):
    """FileBrowser displays directory and file listings from the vfs.
       The file_selected parameter is a callback invoked when a file selection
       has been made; its signature must be file_selected(path,filename). If
       select_dir is set, file_selected's filename parameter should be optional.
       The save_file option provides a box for supplying a new filename that
       doesn't exist yet. The select_dir option allows directories to be
       selected as well as files."""
    def __init__(self, engine, settings, file_selected, gui_xml_path,
                 close_callback=None, save_file=False, select_dir=False, 
                 extensions=('.dat',)):
        self.engine = engine
        self.settings = settings
        self.file_selected = file_selected

        self._widget = None
        self.save_file = save_file
        self.select_dir = select_dir
        self.close_callback = close_callback
        self.gui_xml_path = gui_xml_path 
        
        self.extensions = extensions
        # FIXME M. George Hansen 2011-06-06: Not sure that user_path is set
        #     correctly atm. Plus, I don't think that this should be
        #     hard-coded.
        self.path = os.path.relpath(os.path.join(self.settings.get("parpg", "DataPath"), 'saves'))
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.dir_list = []
        self.file_list = []
        
    def close(self):
        """Closes the browser"""        
        self._widget.hide()
        if self.close_callback:
            self.close_callback()
    
    def showBrowser(self):
        """Shows the file dialog browser"""
        if self._widget:
            self._widget.show()
            return
        xml_file = vfs.VFS.open(self.gui_xml_path)
        self._widget = pychan.loadXML(xml_file)
        self._widget.mapEvents({
            'dirList'       : self._setPath,
            'selectButton'  : self._selectFile,
            'closeButton'   : self.close
        })
        self._setPath()
        if self.save_file:
            self._file_entry = widgets.TextField(name='saveField', text=u'')    
            self._widget.findChild(name="fileColumn").\
                addChild(self._file_entry)
        self._widget.show()

    def _setPath(self):
        """Path change callback."""
        selection = self._widget.collectData('dirList')
        if not (selection < 0):
            new_dir = u2s(self.dir_list[selection])
            lst = self.path.split('/')
            if new_dir == '..' and lst[-1] != '..' and lst[-1] != '.':
                lst.pop()
            else:
                lst.append(new_dir)
            self.path = '/'.join(lst)
            
        def decodeList(list):
            fs_encoding = sys.getfilesystemencoding()
            if fs_encoding is None: fs_encoding = "ascii"
        
            new_list = []
            for i in list:
                try:
                    new_list.append(unicode(i, fs_encoding))
                except:
                    new_list.append(unicode(i, fs_encoding, 'replace'))
                    logger.debug("WARNING: Could not decode item:\n"
                                        "{0}".format(i))
            return new_list
            
        

        self.dir_list = []
        self.file_list = []
        
        dir_list = ('..',) + filter(lambda d: not d.startswith('.'), \
                                    self.engine.getVFS().\
                                    listDirectories(self.path))
        file_list = filter(lambda f: f.split('.')[-1] in self.extensions, \
                           self.engine.getVFS().listFiles(self.path))
        self.dir_list = decodeList(dir_list)
        self.file_list = decodeList(file_list)
        self._widget.distributeInitialData({
            'dirList'  : self.dir_list,
            'fileList' : self.file_list
        })

    def _selectFile(self):
        """ File selection callback. """
        self._widget.hide()
        selection = self._widget.collectData('fileList')

        if self.save_file:
            data = self._widget.collectData('saveField')
            if data:
                if (data.endswith(".dat")):
                    self.file_selected(self.path, \
                                u2s(self._widget.collectData('saveField')))
                else:
                    self.file_selected(self.path, 
                                       u2s(self._widget.collectData('saveField')) + '.dat')
                return
            

        if selection >= 0 and selection < len(self.file_list):
            self.file_selected(self.path, u2s(self.file_list[selection]))
            return
        
        if self.select_dir:
            self.file_selected(self.path)
            return

        logger.error('no selection')

    def _warningMessage(self):
        """Shows the warning message dialog when a file with a
           faulty extension was selected."""
        window = widgets.Window(title="Warning")
        text = "Please save the file as a .dat"
        label = widgets.Label(text=text)
        ok_button = widgets.Button(name="ok_button", text="Ok")
        window.addChildren([label, ok_button])
        window.mapEvents({'ok_button':window.hide})
        window.show()
