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
import types

idle_installed=0
try: 
    import idlelib.PyShell
    idle_installed = 1
except ImportError:
    pass

bpython_installed = 0
try: 
    import bpython.cli
    import curses
    bpython_installed = 1
except ImportError:
    pass

if bpython_installed + idle_installed < 1:
    raise ImportError("Must have one of BPython or Idle installed")

import MysteryMachine
from MysteryMachine.schema.MMAttribute import MMAttribute
from MysteryMachine.schema.MMAttributeValue import MakeAttributeValue

import tempfile
import os
import sys
import logging

class UiBase(object):
    def __init__(self,args = [] ):    
        self.args      = args
        self.in_curses = False 
        self.logger = logging.getLogger("MysteryMachine.Ui.cli")

    def edit_attribute(self,attr):
        """
        Launches a text editor allowing an attribute's contents to be editted.
        """
        print self,attr
        myval   =  attr.get_value()
        myparts = myval.get_parts()
        if len ( myparts ) == 1:
            key = myparts.keys()[0]
            newstr = self.edit_str(myparts[key])
            newpart  = { key: newstr}
            newval   = MakeAttributeValue(myval.get_type(),newpart)
            attr.set_value(newval)
        else:
            raise RuntimeError("Can't edit mulitpart attribute")

    def edit_str(self,string):
        """
        Launches a text editor on a tempory file conatinaing string.
        Returns the contents of the file when the editor is closed.
        """
        #NamedTemporary file works really well on Unix but 
        #  is a complete blowout under windows - where there
        #  is no way to unlock the file and *not* delete it
        fd, fname  = tempfile.mkstemp(suffix=".attribute")
        f = os.fdopen(fd,"w+")
        f.write(string)
        f.close()
        self.launch_edit(fname)
        f = open(fname,"r")
        newval = f.readlines()
        f.close()
        try:
            os.remove(fname)
        except (WindowsError,OSError) as e:
            self.logger.warn(str(e))
            pass
        return "".join(newval)

    def launch_edit(self,filename):
        """
        Starts a text editor on a named file
        """
        if sys.platform[:3] == "win":
            editor = os.getenv("EDITOR","edit")
        else:
            editor = os.getenv("EDITOR","vi")
            
        #Save and restore curses mode.
        # =Can't guarantee - curses is availble.
        if self.in_curses:
            curses.def_prog_mode()
            curses.reset_shell_mode()
        os.system(editor +" "+ filename)
        if self.in_curses: 
            curses.reset_prog_mode()
            try:
                bpython.cli.stdscr.redrawwin()
            except NameError,AttributeError:
                #This means we bython is updated or we are not 
                #uses the curses implemenation
                pass

    def DoPatches(self):
         #Monkeypatch MAttributr to call out to a local editor.
         MMAttribute.edit =  types.UnboundMethodType(self.edit_attribute,None,MMAttribute)


if bpython_installed:
    class BPython(UiBase):

        def Run(self):
            self.DoPatches()

            with MysteryMachine.StartApp(self.args) as ctx:
                self.in_curses = True
                bpython.cli.main(args=["--quiet",] ,locals_ = { 'ctx': ctx })



if idle_installed:
    class IdleBackend(UiBase):
        def _Run(self):
            self.DoPatches()
 
            self.lib = MysteryMachine.StartApp(self.args)
            import atexit
            atexit.register(self._Exit)
            return  self.lib.__enter__()

        def _Exit(self):
            self.lib.__exit__()
       

    class Idle(UiBase):
        def Run(self):
            sys.argv = [ "dummy",  "-t", "Mystery Machine",'-c']
            if __name__ == '__main__':                
                # 
                # We can't guarantee to find our module in the Python namespace
                # and MysteryMachine/Idle doesn't run well without subprocess control
                # so we run it without the monkey patch stuff provided by IdleBackend.
                #
                # We also don't bother with the patching as I doubt the edit patch would
                # work right
                #
                sys.argv += [ 
                             "import MysteryMachine\n"+ 
                             "import atexit\n"+ 
                             "ctx=MysteryMachine.StartApp(" + str(self.args)+").__enter__()\n"+
                             "atexit.register(ctx.close)" 
                            ]

            else:
               with MysteryMachine.StartApp() as lib:
                    sys.argv += [
                                 "import "+__name__+"\n"+
                                 "ctx = "+__name__+".IdleBackend("+str(lib.GetArgv())+")._Run()"
                                ]

            idlelib.PyShell.main()

def main():
    from MysteryMachine.Main import process_args 

    options = process_args()
    if bpython_installed:
        ui = BPython(options)
    elif idle_installed:
        ui = Idle(options)
    else:
        raise LogicError("Can't get here - should have raised ImportError during import")
        

    ui.Run() 

if __name__ == '__main__':
    main()
