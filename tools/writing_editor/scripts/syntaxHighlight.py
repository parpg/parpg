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

from PyQt4 import QtCore, QtGui

class SyntaxHighlighter(QtGui.QSyntaxHighlighter):
    """
    A class to highlight the syntax keywords
    """

    def highlightBlock(self, text):
        """
        Highlight the syntax in the text of self.widget
        @type text: QtCore.QString
        @param text: the text to highlight syntax in
        @return: None
        """
        boldCmdFormat = QtGui.QTextCharFormat()
        boldCmdFormat.setFontWeight(QtGui.QFont.Bold)
        boldCmdFormat.setForeground(QtGui.QColor("blue"))

        cmdFormat = QtGui.QTextCharFormat()
        cmdFormat.setForeground(QtGui.QColor("blue"))
        
        quoteFormat = QtGui.QTextCharFormat()
        quoteFormat.setForeground(QtGui.QColor("green"))

        commentFormat = QtGui.QTextCharFormat()
        commentFormat.setForeground(QtGui.QColor("red"))
            
        bold_cmds = ["NPC", "AVATAR", "START", "SECTIONS"]
        cmds = ["say", "responses", "pc", "dialogue", "end", "back", "\"", "'"]
        comments = ["#"]
        
        all_cmds = cmds + bold_cmds + comments
        for cmd in all_cmds:
            # if its a comment
            if (cmd == "#"):
                startExp = QtCore.QRegExp(cmd)
                startIndex = text.indexOf(startExp)
                self.setFormat(startIndex, text.length(), commentFormat)

            # if its a quote
            elif (cmd == "\"" or cmd == "'"):
                startExp = QtCore.QRegExp(cmd)
                startIndex = text.indexOf(startExp)
                if (self.format(startIndex) == commentFormat):
                    return
                else:
                    endIndex = text.indexOf(startExp, startIndex+1)
                    quoteLength = endIndex - startIndex + 1
                    self.setFormat(startIndex, quoteLength, quoteFormat)

            # if its just a regular command
            elif cmd in cmds:
                expression = QtCore.QRegExp(cmd)
                index = int(text.indexOf(expression))
                while (index >= 0):
                    length = int(expression.matchedLength())
                    self.setFormat(index, length, cmdFormat)
                    index = text.indexOf(expression, index + length)                

            # if its a command that needs to be bold
            elif cmd in bold_cmds:       
                expression = QtCore.QRegExp(cmd)
                index = int(text.indexOf(expression))
                while (index >= 0):
                    length = int(expression.matchedLength())
                    self.setFormat(index, length, boldCmdFormat)
                    index = text.indexOf(expression, index + length)

            else:
                raise Exception("SyntaxHighlighter: Cannot find command %s" % cmd)
