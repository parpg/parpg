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
from fife.extensions import pychan

from parpg import vfs

class RestartDialog(object):
    def __init__(self, settings):
        self.settings = settings
        xml_file = vfs.VFS.open('gui/restart_dialog.xml')
        self.window = pychan.loadXML(xml_file)
        self.window.mapEvents({'closeButton': self.hide})

    def hide(self):
        self.window.hide()

    def show(self):
        self.window.show()
