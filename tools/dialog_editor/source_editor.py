#!/usr/bin/env python2
#
#   This file is part of PARPG.
#
#   PARPG is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   PARPG is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with PARPG.  If not, see <http://www.gnu.org/licenses/>.
"""
Provides classses used by the source editor portion of the dialogue editor.
"""

from PySide import QtCore, QtGui

class Highlighter(QtGui.QSyntaxHighlighter):
    """ 
    Responsible for appropriately highlighting various parts of dialogue
        scripts such as keywords and comments. Also highlights syntax errors.
        
    @ivar foreground: foreground colors to be used to highlight various
        formats within a dialogue file.
    @type foreground: dictionary of Qt.GlobalColors
    @ivar weight: weight to be used to highlight various formats within a 
        dialogue file.
    @type weight: dictionary of QFont.Weights
    """

    def __init__(self, parent=None):
        """
        Initialize a new L{Highlighter} instance.

        @param parent: parent widget
        @type parent: QObject
        """

        super(Highlighter, self).__init__(parent)

        self.foreground = dict(keyword_error=QtCore.Qt.red,
                               document_error=QtCore.Qt.red,
                               keyword=QtCore.Qt.darkBlue,
                               comment=QtCore.Qt.blue,
                               quotation=QtCore.Qt.darkGreen,
                               document=QtCore.Qt.yellow)
        self.weight = dict(keyword=QtGui.QFont.Bold)

        self.setupFormats()
        self.setupCompletion()


    def setupFormats(self):
        """
        Setup the various formats used for highlighting.

        @ivar highlighting_rules: rules to use for highlighting the dialogue
            file
        @type highlighting_rules: list of tuples containing the pattern to
            match for the rule followed by the format to apply when a match is
            found
        @var keyword_error_format: format used to highlight keyword syntax
            errors
        @type keyword_error_format: QTextCharFormat
        @var document_error_format: format used to highlight document begin and
            document end syntax errors
        @type document_error_format: QTextCharFormat
        @var keyword_format: format used to highlight keywords 
        @type keyword_format: QTextCharFormat
        @var comment_format: format used to highlight comments
        @type comment_format: QTextCharFormat
        @var quotation_format: format used to highlight quoted strings
        @type quotation_format: QTextCharFormat
        @var document_format: format used to highlight the beginning and end
            of a dialogue document (eg. "---" and "...")
        @type document_format: QTextCharFormat
        """

        keyword_error_format = QtGui.QTextCharFormat()
        keyword_error_format.setForeground(self.foreground['keyword_error'])
        self.highlighting_rules = [(QtCore.QRegExp('^(?!\")[A-Z]{1,}'),
                                   keyword_error_format)]

        document_error_format = QtGui.QTextCharFormat()
        document_error_format.setForeground(self.foreground['document_error'])
        self.highlighting_rules.append((QtCore.QRegExp('^[\.-].*$'),
                                        document_error_format))

        keyword_format = QtGui.QTextCharFormat()
        keyword_format.setForeground(self.foreground['keyword'])
        keyword_format.setFontWeight(self.weight['keyword'])

        keyword_patterns = ['\\bNPC_NAME\\b', '\\bAVATAR_PATH\\b',
                            '\\bSTART_SECTION\\b', '\\bSECTIONS\\b',
                            '\\bID\\b', '\\bSAY\\b', '\\bACTIONS\\b',
                            '\\bRESPONSES\\b', '\\bREPLY\\b',
                            '\\bGOTO\\b', '\\bCONDITION\\b']

        self.highlighting_rules += [(QtCore.QRegExp(pattern), keyword_format)
                                    for pattern in keyword_patterns]

        comment_format = QtGui.QTextCharFormat()
        comment_format.setForeground(self.foreground['comment'])
        self.highlighting_rules.append((QtCore.QRegExp('^#.*$'),
                                        comment_format))

        quotation_format = QtGui.QTextCharFormat()
        quotation_format.setForeground(self.foreground['quotation'])
        self.highlighting_rules.append((QtCore.QRegExp('\".*\"'),
                                       quotation_format))

        document_format = QtGui.QTextCharFormat()
        document_format.setForeground(self.foreground['document'])
        self.highlighting_rules.append((QtCore.QRegExp('^-{3,3}$|^\.{3,3}$'),
                                        document_format))

    def setupCompletion(self):
        completion_list = ['NPC_NAME', 'AVATAR_PATH',
                                'START_SECTION', 'SECTIONS', 
                                'ID', 'SAY', 'ACTIONS', 
                                'RESPONSES', 'REPLY',
                                'GOTO', 'CONDTIION']
        self.completer = QtGui.QCompleter(completion_list, self)

    def highlightBlock(self, text):
        """
        Highlight the currently loaded dialogue file according to the
        highlighting rules.

        @param text: the text to be highlighted if a matching rule is found
        @type text: string
        """
        for pattern, format in self.highlighting_rules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)

            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)


