#!/usr/bin/env python
#   			grammarTest.py - Copyright Roger Gammans
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
Tests for complex MysteryMachine.Schema bugs which met or have had reported.

This tests the complete shcema and doesn't try to use mock object to
simplify the tests.

"""

from MysteryMachine.schema.MMListAttribute import * 
import MysteryMachine.schema.MMDLinkValue as dlk
from MysteryMachine.schema.MMListAttribute import _Key as ListKey 
from MysteryMachine.schema.MMAttributeValue import * 
from MysteryMachine.schema.MMAttribute import * 
from MysteryMachine.schema.MMObject import * 
from MysteryMachine.schema.MMBase import * 
import unittest
from MysteryMachine import * 
from itertools import izip
import copy
from MysteryMachine.store.dict_store import *


    
class complexValTest(unittest.TestCase):
    def setUp(self):
        StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"]) 
        self.logger = logging.getLogger("")
        self.system=MMSystem.Create("dict:ObjectTests")
        self.system.NewCategory( "Template" )
        self.dummyparent             = self.system.NewObject( "Template" )
        self.dummyparent[".defname"] = "name"
        
        self.parent                  = self.system.NewObject( "Template" )
        self.parent[".defname"]      =":mm:`:name`"
        
        self.system.NewCategory( "Dummy" ,defaultparent =self.dummyparent)
        self.object                  = self.system.NewObject("Dummy") 
        self.object.set_parent(self.parent)       

        self.object2                  = self.system.NewObject("Dummy") 
  
    def testListInheirtance(self):
        self.parent["a_list"]  = [ "" ]
        self.assertEquals(self.parent["a_list"].get_value().get_type(), "list")
        self.assertEquals(self.object["a_list"].get_value().get_type(), "list")
        self.assertEquals(self.parent["a_list"][0].get_raw(), "")
        self.assertEquals(self.object["a_list"][0].get_raw(), "")

        ##This is counter-intuiutive *but* anything else would be too confusing...
        #  the reason we have changed data in both elements is because we have called
        #  setitem on the value object change the shared value directly...
        self.object["a_list"][0]  =  "data"
        self.assertEquals(self.parent["a_list"][0].get_raw(), "data")
        self.assertEquals(self.object["a_list"][0].get_raw(), "data")

        self.object["a_list"]  =  [ "differentdata" ]
        self.assertEquals(self.parent["a_list"][0].get_raw(), "data")
        self.assertEquals(self.object["a_list"][0].get_raw(), "differentdata")


    def testListAndDlink(self):
        self.object["linklist"]  = [dlk.CreateAnchorPoint(self.object)] * 2 
        self.assertEquals(self.object["linklist"][0].get_value().get_type(), "bidilink")
        self.assertEquals(self.object["linklist"][0].get_anchor(), self.object)
        self.assertEquals(self.object["linklist"][1].get_value().get_type(), "bidilink")
        self.assertEquals(self.object["linklist"][1].get_anchor(), self.object)
        self.object2["link"] = dlk.CreateAnchorPoint(self.object2)
        self.object2["link2"] = dlk.CreateAnchorPoint(self.object2)
        self.object["linklist"][0] = dlk.ConnectTo(self.object2["link"]) 
        print self.object["linklist"][0].get_value().get_parts()
        self.assertEquals(self.object["linklist"][0].get_anchor(), self.object)
        self.assertEquals(self.object["linklist"][0].get_object(), self.object2)
def getTestNames():
    return [ 'complexValueBugs.complexValTest' ]

if __name__ == '__main__':
    if "--debug" in sys.argv:
        lognr = sys.argv.index("--debug")+1
        log = sys.argv[lognr]
        myargs = sys.argv
        sys.argv = myargs[:lognr-1] + myargs[lognr+1:]
        logging.getLogger(log).setLevel(logging.DEBUG)
    unittest.main()
