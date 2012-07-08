#!/usr/bin/env python
#   			plugin_load.py - Copyright Roger Gammans
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
# 
"""
Tests for dynamic loading of system plugins.
"""


from MysteryMachine import * 
from itertools import izip
import copy

import unittest
    
class dynamicLoad(unittest.TestCase):
    def setUp(self):
        self.ctx = StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/libtest.yaml", "--testmode"]) 
    def tearDown(self,):
        self.ctx.close()
    
    def testLoadStorePlugin(self):
        self.system=MMSystem.Create("dict:ObjectTests")

    def set_upSys(self):
        self.testLoadStorePlugin()
        self.system.NewCategory( "Template" )
        self.dummyparent             = self.system.NewObject( "Template" )
        self.dummyparent[".defname"] = "name"
        
        self.parent                  = self.system.NewObject( "Template" )
        self.parent[".defname"]      =":mm:`:name`"
        
        self.system.NewCategory( "Dummy" ,defaultparent =self.dummyparent)
        self.object                  = self.system.NewObject("Dummy") 
        self.object.set_parent(self.parent)       

        self.object2                  = self.system.NewObject("Dummy") 
  
    def testListLoad(self):
        self.set_upSys()
        self.object["list"] = [ ] 
        import MysteryMachine.schema.MMAttributeValue
        MysteryMachine.schema.MMAttributeValue.MakeAttributeValue("bidilink",{"anchordist":"1"})

    def testBidiLoad(self):
        self.set_upSys()
        
        
def getTestNames():
    return [ 'plugin_load.dynamicload' ]

if __name__ == '__main__':
    if "--debug" in sys.argv:
        lognr = sys.argv.index("--debug")+1
        log = sys.argv[lognr]
        myargs = sys.argv
        sys.argv = myargs[:lognr-1] + myargs[lognr+1:]
        logging.getLogger(log).setLevel(logging.DEBUG)
    unittest.main()
