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
import mercurial

def closed(self):
    """A fixup function so mercurial and bpython play well together"""
    return False

class UiPython(object):
    def __init__(self,args=[]):
        self.args = args

    def mercurial_ui(self):
        return mercurial.ui.ui()

    def Run(self):
        
        #Mercurial 1.4 calls sys.stdout.closed() - this ensures that call exists
        if not hasattr(bpython.cli.Repl,"closed"):
            bpython.cli.Repl.closed = closed

        with MysteryMachine.StartApp(self.args) as ctx:
            bpython.cli.main(args=("--quiet",) ,locals_ = { 'ctx': ctx })


if __name__ == '__main__':
    ui = UiPython(sys.argv[1:])
    ui.Run() 


