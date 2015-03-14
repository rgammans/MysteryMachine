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
import MysteryMachine.store.file_store
import unittest
import tempfile
import shutil
from MysteryMachine import * 
from itertools import izip
import copy
from MysteryMachine.store.dict_store import *


    
class complexValTest(unittest.TestCase):
    def setUp(self):
        self.ctx = StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"]) 
        self.logger = logging.getLogger("")
        self.logger.setLevel(logging.INFO)
        import tempfile
        d=tempfile.mkdtemp()
        os.rmdir(d)
        #self.system=MMSystem.Create("hgafile:"+d)
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

    def tearDown(self,): 
        self.ctx.close()

    def testListInheirtance(self):
        
        self.parent["a_list"]  = [ "" ]
        self.assertEquals(self.parent["a_list"].get_value().get_type(), "list")
        self.assertEquals(self.object["a_list"].get_value().get_type(), "list")
        self.assertEquals(self.parent["a_list"][0].get_raw(), "")
        self.assertEquals(self.object["a_list"][0].get_raw(), "")

       ##This is counter-intuiutive *but* anything else would be too confusing...
        #  the reason we have changed data in both elements is because we have called
        #  setitem on the value object change the shared value directly...
        # XXX XXX XXX
        # This has chnaged with acid compliance - now modifying object[a_list] auto vivifies 
        # the attribute in COW like manner.
        self.object["a_list"][0]  =  "data"
        #self.assertEquals(self.parent["a_list"][0].get_raw(), "data")
        self.assertEquals(self.parent["a_list"][0].get_raw(), "")
        self.assertEquals(self.object["a_list"][0].get_raw(), "data")

        self.object["a_list"]  =  [ "differentdata" ]
        self.assertEquals(self.parent["a_list"][0].get_raw(), "")
        self.assertEquals(self.object["a_list"][0].get_raw(), "differentdata")

        self.object["c_list"]  =  [ "differentdata" ,"moredata"]
        self.assertEquals(self.object["c_list"][0].get_raw(), "differentdata")
        self.assertEquals(self.object["c_list"][1].get_raw(), "moredata")

        oldlevel= self.logger.getEffectiveLevel()
        #New list for testing the append behavior
        # first check we have an empty list.
        self.parent["b_list"]  = [ ]
        self.assertEquals(len(self.parent["b_list"]), 0) 
        self.assertEquals(len(self.object["b_list"]), 0)
       
        #Now append through the object and check it has the right data in an element
        # and the ancestor attribute is untouched
        #o=self.object["b_list"]
        #o.append("S")
        self.object["b_list"].append("S")
        self.assertEquals(len(self.object["b_list"]), 1)
        self.assertEquals(self.object["b_list"][0].get_raw(), "S")
        self.assertEquals(len(self.parent["b_list"]), 0)

        self.logger.setLevel(oldlevel)

    def testListAndDlink(self):
        self.object["linklist"]  = [dlk.CreateAnchorPoint(self.object)] * 2 
        self.assertEquals(self.object["linklist"][0].get_value().get_type(), "bidilink")
        self.assertEquals(self.object["linklist"][0].get_anchor(), self.object)
        self.assertEquals(self.object["linklist"][1].get_value().get_type(), "bidilink")
        self.assertEquals(self.object["linklist"][1].get_anchor(), self.object)
        self.object2["link"] = dlk.CreateAnchorPoint(self.object2)
        self.object2["link2"] = dlk.CreateAnchorPoint(self.object2)
        self.object["linklist"][0] = dlk.ConnectTo(self.object2["link"]) 
        self.assertEquals(self.object["linklist"][0].get_anchor(), self.object)
        self.assertEquals(self.object["linklist"][0].get_object(), self.object2)



    def testListAndDlink_with_shadows(self):
        """This is typical behaviour of a manymnay linkng client"""
        #Create empty list on parent
        self.dummyparent["linklist"]  = []
        #override with a ancohr on the object.
        self.object2["linklist"].append(dlk.CreateAnchorPoint(self.object2))
        self.assertEquals(self.object2["linklist"][0].get_value().get_type(), "bidilink")
        self.assertEquals(self.object2["linklist"][0].get_anchor(), self.object2)

        self.object["link"] = dlk.CreateAnchorPoint(self.object)
        self.object2["linklist"][0] = dlk.ConnectTo(self.object["link"]) 
        self.assertEquals(self.object2["linklist"][0].get_anchor(), self.object2)
        self.assertEquals(self.object2["linklist"][0].get_object(), self.object)
        self.assertEquals(self.object["link"].get_anchor(), self.object)
        self.assertEquals(self.object["link"].get_object(), self.object2)

    def testListAndDlink_with_dup_shadows(self):
        """This id another typical behaviour of a manymnay linkng client"""
        #Create empty list on parent
        self.dummyparent["linklist"]  = []
        self.parent["link"]  = dlk.CreateAnchorPoint(self.parent)
        self.assertEquals(self.object["link"].get_anchor(), self.object)
        x  = self.dummyparent["linklist"]
        #override with a ancohr on the object.
        self.object2["linklist"].append(dlk.CreateAnchorPoint(self.object2))
        self.assertEquals(self.object2["linklist"][0].get_value().get_type(), "bidilink")
        self.assertEquals(self.object2["linklist"][0].get_anchor(), self.object2)

        self.object2["linklist"][0] = dlk.ConnectTo(self.object["link"]) 
        self.assertEquals(self.object2["linklist"][0].get_anchor(), self.object2)
        self.assertEquals(self.object2["linklist"][0].get_object(), self.object)
        self.assertEquals(self.object["link"].get_anchor(), self.object)
        self.assertEquals(self.object["link"].get_object(), self.object2)


        ##Now do it again.
        object3     = self.system.NewObject("Dummy")
        object3.set_parent(self.parent)
        object4     = self.system.NewObject("Dummy") 
        object4["linklist"].append(dlk.CreateAnchorPoint(object4))
        object4["linklist"][0] = dlk.ConnectTo(object3["link"]) 
        self.assertEquals(object4["linklist"][0].get_anchor(), object4)
        self.assertEquals(object4["linklist"][0].get_object(), object3)
        self.assertEquals(object3["link"].get_anchor(), object3)
        self.assertEquals(object3["link"].get_object(), object4)



    def test_should_remember_an_empty_list(self):
        self.parent["a_list"]  = [  ]
        self.assertEquals(len(self.parent["a_list"]),0)
        self.assertEquals(len(self.object["a_list"]),0)
        path=tempfile.mkdtemp()
        os.rmdir(path)
        self.system=MMSystem.Create("attrfile:" + path)
        self.system.NewCategory("Test")
        obj = self.system.NewObject("Test")
        objname = repr(obj).split(":")[-1]
        obj["a_list"]  = [  ]
        self.assertEquals(len(obj["a_list"]),0)
        self.assertEquals(len(obj["a_list"]),0)
        obj = None
        self.system =None
        shutil.rmtree(path)

    def UnstorableLinkList(self): 
        attr = MMUnstorableAttribute(".temp",[],self.object)
        self.assertEquals(attr.get_type(),"list")
        attr.append(dlk.CreateAnchorPoint(self.object))
        self.assertRaises(KeyError,self.object.__getitem__,".temp")
        self.object2["link2"] = dlk.CreateAnchorPoint(self.object2)
        attr[0] = dlk.ConnectTo (self.object2["link2"])
        self.assertRaises(KeyError,self.object.__getitem__,".temp")
        self.assertEqual(self.object2["link"].get_partner(),None)



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
