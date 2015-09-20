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

# Miscellaneous game functions

import sys
import os
import fnmatch

from textwrap import dedent
from contextlib import contextmanager
from parpg import vfs

def addPaths (*paths):
    """Adds a list of paths to sys.path. Paths are expected to use forward
       slashes, for example '../../engine/extensions'. Slashes are converted
       to the OS-specific equivalent.
       @type paths: ???
       @param paths: Paths to files?
       @return: None"""
    for p in paths:
        if not p in sys.path:
            sys.path.append(os.path.sep.join(p.split('/')))

def parseBool(value):
    """Parses a string to get a boolean value"""
    if (value.isdigit()):
        return bool(int(value))
    elif (value.isalpha):
        return value.lower()[0] == "t"
    return False

def locateFiles(pattern, root=os.curdir):
    """Locate all files matching supplied filename pattern in and below
    supplied root directory."""
    filepaths = []
    filenames = vfs.VFS.listFiles(root)
    for filename in fnmatch.filter(filenames, pattern):
        vfs_file_path = '/'.join([root, filename])
        filepaths.append(vfs_file_path)
    dirnames = vfs.VFS.listDirectories(root)
    for dirname in dirnames:
        subdir_filepaths = locateFiles(pattern, '/'.join([root, dirname]))
        filepaths.extend(subdir_filepaths)
    return filepaths

def dedent_chomp(string):
    """Remove common leading whitespace and chomp each non-blank line."""
    dedented_string = dedent(string).strip()
    lines = dedented_string.splitlines()
    formatted_lines = []
    for index in range(len(lines)):
        line = lines[index]
        if index == len(lines) - 1:
            # Don't do anything to the last line.
            pass
        elif not line or line.isspace():
            line = '\n\n'
        else:
            line = ''.join([line, ' '])
        formatted_lines.append(line)
    result = ''.join(formatted_lines)
    return result

@contextmanager
def cwd(dirname):
    cwd = os.getcwd()

    try:
        os.chdir(dirname)
        yield
    finally:
        os.chdir(cwd)
