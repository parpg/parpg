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

import sys

from PyQt4 import QtCore, QtGui
from parpg.writingEditor import WritingEditor

def createApplication():
    app = QtGui.QApplication(sys.argv)
    editor = WritingEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    createApplication()
