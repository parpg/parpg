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

from PyQt4 import QtGui, QtCore

# goto_table stores label's so you can jump back to them
# they are stored in the format: {label (string): paragraph number (int, starts at 0)}
goto_table = {}

class ConversationNode(object):
    """
    The class for every node in the conversation tree
    """
    def __init__(self, label="", text="", type_="", options=[]):
        """
        Initialize the node
        @type label: string
        @param label: the label for the node
        @type text: string
        @param text: the text for the node
        @type type_: string
        @param type_: the type of node, either 'text' or 'option'
        @type options: list
        @param options: a list of all the option nodes
        @return: None
        """
        self.label = label
        self.text = text
        self.type_ = type_
        self.options = options


def parse(text):
    """
    Parse the text and create the tree structure from it
    @type text: string
    @param text: the text to parse
    @return: the root node
    """
    text = str(text).strip()

    if (text == ""):
        # if there is no text return an empty node
        return ConversationNode()

    # split the text into paragraphs
    paras = []
    for line in text.split('\n'):
        line = line.strip()
        if line != "":
            paras.append(line) 
            
    # if there is a label make sure to have it in the same paragraph as it's text
    for para in paras:
        if para.startswith("LABEL"):
            para_spot = paras.index(para)
            next_para = paras[para_spot+1]
            new_para = para + '\n' + next_para

            paras.remove(para)
            paras.remove(next_para)
            paras.insert(para_spot, new_para)

    # recursively parse the text and get the root node and end
    root, end = _parse(paras, 0, len(paras)-1)
    
    # if the end is not the end of the paragraphs, then throw a syntax error
    if (end != len(paras)):
        print "syntax error 1"

    # else return the root node
    else:
        return root


def _parse(paras, start, end):
    """
    Recursively parse the text
    @type paras: list
    @param paras: a list of the paragraphs in the text
    @type start: int
    @param start: the start of the text
    @type end: int
    @param end: the end of the text
    @return: the root node and end of text
    """
    # create a new node
    node = ConversationNode()

    # check for a label and extract it if its there
    if (paras[0].startswith("LABEL")):
        label_text = paras[0].split('\n')[0][6:]
        node.label = label_text
        goto_table[label_text] = 0
        paras[0] = paras[0].split('\n')[1]

    for i in xrange(start, end):
        # if the paragraph is an option, break the loop
        if (paras[i].startswith("OPTION")):
            break

        # if the paragraph is an endoption, exit the function and return the node and the end point
        elif (paras[i].startswith("ENDOPTION")):
            return node, i

        # else parse the text normally
        else:
            node.type = 'text'
            node.text = paras[i]
            
    # while not at the end of the text
    while i < end:
        # if the paragraph is an option, start the recursive parsing and append the option to the root node
        if (paras[i].startswith("OPTION")):
            txt = paras[i][7:]
            child, i = _parse(paras, i+1, end)
            child.type_ = 'option'
            child.text = txt
            node.options.append(child)
            
        # if the paragraph is an endoption, it is a syntax error
        elif (paras[i].startswith("ENDOPTION")):
            print "syntax error 2"

        # move to the next paragraph
        i += 1

    return node, i
