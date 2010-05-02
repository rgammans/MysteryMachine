#!/usr/bin/env python
#   			MysteryMachine/Ui/cli.py - Copyright R Gammans
# 
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from __future__ import with_statement

import sys
import bpython.cli

import MysteryMachine
from MysteryMachine.schema.MMAttribute import MMAttribute
from MysteryMachine.schema.MMAttributeValue import MakeAttributeValue
import mercurial

import tempfile
import os

import curses

def closed(self):
    """A fixup function so mercurial and bpython play well together"""
    return False


def launch_edit(filename):
    """
    Starts a text editor on a named file
    """
    if sys.platform == "win":
        editor = os.getenv("EDITOR","edit")
    else:
        editor = os.getenv("EDITOR","vi")
        
    #Save and restore curses mode.
    curses.reset_shell_mode()
    os.system(editor +" "+ filename)
    curses.reset_prog_mode()

def edit_str(string):
    """
    Launches a text editor on a tempory file conatinaing string.
    Returns the contents of the file when the editor is closed.
    """
    f = tempfile.NamedTemporaryFile(suffix=".attribute",mode="w+")
    f.write(string)
    f.flush()
    launch_edit(f.name)
    f.seek(0L)
    newval = f.readlines()
    f.close()
    return "\n".join(newval)

def edit_attribute(self):
    """
    Launches a text editor allowing an attribute's contents to be editted.
    """
    myval   =  self.get_value()
    myparts = myval.get_parts()
    if len ( myparts ) == 1:
        key = myparts.keys()[0]
        newstr = edit_str(myparts[key])
        newpart  = { key: newstr}
        newval   = MakeAttributeValue(myval.get_type(),newpart)
        self.set_value(newval)
    else:
        raise RuntimeError("Can't edit mulitpart attribute")

class UiPython(object):
    def __init__(self,args=[]):
        self.args = args

    def mercurial_ui(self):
        return mercurial.ui.ui()

    def Run(self):
        
        #Mercurial 1.4 calls sys.stdout.closed() - this ensures that call exists
        if not hasattr(bpython.cli.Repl,"closed"):
            bpython.cli.Repl.closed = closed

        #Monkeypatch MAttributr to call out to a local editor.
        MMAttribute.edit = edit_attribute 
        
 
        with MysteryMachine.StartApp(self.args) as ctx:
            bpython.cli.main(args=("--quiet",) ,locals_ = { 'ctx': ctx })


if __name__ == '__main__':
    ui = UiPython(sys.argv[1:])
    ui.Run() 


