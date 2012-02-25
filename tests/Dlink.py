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
Tests for the MysteryMachine.Schema Dlink  module
"""

from MysteryMachine import * 
from MysteryMachine.schema.MMSystem import * 
from MysteryMachine.schema.MMObject import MMObject
from MysteryMachine.schema.MMAttribute import * 

from MysteryMachine.store.dict_store import *

import MysteryMachine.schema.MMAttributeValue
import MysteryMachine.schema.MMDLinkValue as dlk
import unittest
import logging

import sys

#logging.basicConfig(level=logging.DEBUG)
#logging.getLogger("MysteryMachine.schema.MMDLinkValue").setLevel(logging.DEBUG)

class DlinkTests(unittest.TestCase):
    def setUp(self):
        StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"]) 


        self.system=MMSystem.Create("dict:ObjectTests")
        self.system.NewCategory( "Template" )
        self.dummyparent             = self.system.NewObject( "Template" )
        self.dummyparent[".defname"] = "name"
        
        self.parent                  = self.system.NewObject( "Template" )
        self.parent[".defname"]      =":mm:`:name`"
        
        self.system.NewCategory( "Dummy" ,defaultparent =self.dummyparent)
        self.object1                  = self.system.NewObject("Dummy") 
        self.object2                  = self.system.NewObject("Dummy") 
        self.object3                  = self.system.NewObject("Dummy") 
        self.object1.set_parent(self.parent)       

        #self.logger.debug( "dummy => " ,repr(self.dummyparent))
        #self.logger.debug( "parent => " ,repr(self.parent))
        #self.logger.debug( "object1 => " , repr(self.object1))
        #self.logger.debug( "object2 => " , repr(self.object2))


    def testLink(self):
        dlk.CreateBiDiLink(self.object1,"link",self.object2,"link" )
        self.assertEquals(self.object1["link"].get_object(),self.object2)        
        self.assertEquals(self.object2["link"].get_object(),self.object1)        
        self.assertEquals(self.object2["link"].get_partner(),self.object1["link"])        
        self.assertEquals(self.object1["link"].get_partner(),self.object2["link"])        
        self.assertEquals(self.object1["link"].get_anchor(),self.object1)        
        self.assertEquals(self.object2["link"].get_anchor(),self.object2)        
 
    def testMove(self):
        dlk.CreateBiDiLink(self.object1,"link",self.object2,"link" )
        self.assertEquals(self.object1["link"].get_object(),self.object2)        
        
        #Do move and check all three values
        object3 = self.system.NewObject("Dummy") 
        object3["newlink"]=dlk.CreateAnchorPoint(object3) 
        object3["newlink"]=self.object2["link"] 
        self.assertEquals(self.object1["link"].get_object(),object3)        
        self.assertEquals(object3["newlink"].get_object(),self.object1)        
        self.assertEquals(self.object2["link"].get_object(),None)        
        self.assertEquals(self.object1["link"].get_partner(),object3["newlink"])        
        self.assertEquals(object3["newlink"].get_partner(),self.object1["link"])        
        self.assertEquals(self.object2["link"].get_partner(),None)        
        self.assertEquals(self.object1["link"].get_anchor(),self.object1)        
        self.assertEquals(self.object2["link"].get_anchor(),self.object2)        
        self.assertEquals(object3["newlink"].get_anchor(),object3)        
        
        def raiseerror(obj,attrname):
            obj[attrname]=self.object2["link"] 
        #Try invalid move toan anchorpoint and check it hasn't changed  src or created the object
        
        #New code does something different here!
        #self.assertRaises(dlk.BiDiLinkTargetMismatch,raiseerror,self.object1,"newlink")
        #self.assertRaises(KeyError,self.object1.__getitem__,"newlink")    
        
        self.object1["newlink"] = self.object2["link"]
        self.assertEquals(self.object2["link"].get_object(),None)        
        self.assertEquals(self.object2["link"].get_anchor(),self.object2)  
        #Anchordist is preserved when copying anchors..      
        self.assertEquals(self.object1["newlink"].get_anchor(),self.object1)        
           
 
        #Try valid copy of an anchor point
        self.object2["newlink"]=self.object2["link"] 
        self.assertEquals(self.object2["newlink"].get_partner(),None)        
        self.assertEquals(self.object2["newlink"].get_anchor(),self.object2) 
        
        #Try invalid move toan anchorpoint and check it hasn't changed  src or dest object
        #again code has chnaged here.
        #self.assertRaises(dlk.BiDiLinkTargetMismatch,raiseerror,self.object1,"link")
        #self.assertEquals(self.object1["link"].get_partner(),object3["newlink"])        
        #self.assertEquals(self.object1["link"].get_anchor(),self.object1)        
        #self.assertEquals(self.object1["link"].get_object(),object3)        

        self.object1["link"] = self.object2["link"]
        self.assertEquals(self.object1["link"].get_partner(),None)        
        self.assertEquals(self.object1["link"].get_anchor(),self.object1)        


        #self.object1["link"]=self.object2["link"] 

        #FIXME:(reinstate test) Just breaking a link...
        dlk.CreateBiDiLink(self.object1,"1link",self.object2,"1link" )
        self.object1["1link"] = dlk.CreateAnchorPoint(self.object1)
        self.assertEquals(self.object1["1link"].get_anchor(),self.object1)        
        self.assertEquals(self.object2["1link"].get_anchor(),self.object2)        
        self.assertEquals(self.object1["1link"].get_object(),None)        
        self.assertEquals(self.object2["1link"].get_object(),None)        
        self.assertEquals(self.object1["1link"].get_partner(),None)        
        self.assertEquals(self.object2["1link"].get_partner(),None)        



    def testConnectTo(self):
        #Connect two AnchorPoints and test initial state
        self.object1["2link"]=dlk.CreateAnchorPoint(self.object1)
        self.object2["2link"]=dlk.CreateAnchorPoint(self.object2)
        self.do_actual_connect_to_test()


    def testConnectTo_with_local_copy(self):
        #Connect two AnchorPoints and test initial state
        self.object1["2link"]=dlk.CreateAnchorPoint(self.object1)
        self.object2["2link"]=dlk.CreateAnchorPoint(self.object2)
        ###Make a copy of the values to keep them in the cache...
        self.attr_o1_2link = self.object1["2link"]
        self.attr_o2_2link = self.object2["2link"]
        self.do_actual_connect_to_test()

    def do_actual_connect_to_test(self,):
        self.assertEquals(self.object1["2link"].get_anchor(),self.object1)        
        self.assertEquals(self.object1["2link"].get_partner(),None)        
        self.assertEquals(self.object1["2link"].get_object(),None)        
        self.assertEquals(self.object2["2link"].get_anchor(),self.object2)    
        self.assertEquals(self.object2["2link"].get_partner(),None)        
        self.assertEquals(self.object2["2link"].get_object(),None)        
        self.object1["2link"] = dlk.ConnectTo(self.object2["2link"])
        self.assertEquals(self.object1["2link"].get_anchor(),self.object1)        
        self.assertEquals(self.object1["2link"].get_partner(),self.object2["2link"])        
        self.assertEquals(self.object1["2link"].get_object(),self.object2)        
        self.assertEquals(self.object2["2link"].get_anchor(),self.object2)    
        self.assertEquals(self.object2["2link"].get_partner(),self.object1["2link"])        
        self.assertEquals(self.object2["2link"].get_object(),self.object1) 
        #Use a new anchor point and move / ConnectTo to it.
        self.object2["3link"]=dlk.CreateAnchorPoint(self.object2)
        link=dlk.ConnectTo(self.object2["3link"])
        self.object1["2link"]=link
        self.assertEquals(self.object1["2link"].get_anchor(),self.object1)        
        self.assertEquals(self.object1["2link"].get_partner(),self.object2["3link"])        
        self.assertEquals(self.object1["2link"].get_object(),self.object2)        

        self.assertEquals(self.object2["3link"].get_anchor(),self.object2)    
        self.assertEquals(self.object2["3link"].get_partner(),self.object1["2link"])        
        self.assertEquals(self.object2["3link"].get_object(),self.object1)

        self.assertEquals(self.object2["2link"].get_anchor(),self.object2)    
        self.assertEquals(self.object2["2link"].get_partner(),None)        
        self.assertEquals(self.object2["2link"].get_object(),None)


    def testShadowing(self):
        self.dummyparent["objlink1"] = dlk.CreateAnchorPoint(self.dummyparent)
        self.object1["link2"] = dlk.CreateAnchorPoint(self.object1)
        self.object2["objlink1"] = dlk.ConnectTo( self.object1["link2"])
        self.assertEquals(self.object1["link2"].get_object(),self.object2)
        self.assertEquals(self.object2["objlink1"].get_object(),self.object1)
        self.assertEquals(self.dummyparent["objlink1"].get_object(),None)
        self.assertEquals(self.dummyparent["objlink1"].get_anchor(),self.dummyparent)

    def testUnstored(self):
        self.object2["uobjlink1"] = dlk.CreateAnchorPoint(self.object2)
        self.object3["uobjlink1"] = dlk.CreateAnchorPoint(self.object3)
        attr = MMUnstorableAttribute("foo", dlk.CreateAnchorPoint(self.object1) , self.object1)
        self.assertRaises(KeyError,self.object1.__getitem__,"foo")
        #Test that the value can be set multiple times with a problems
        attr.set_value (dlk.ConnectTo( self.object2["uobjlink1"]))
        attr.set_value (dlk.ConnectTo( self.object3["uobjlink1"]))
        self.assertEquals(   self.object2["uobjlink1"].get_object() , None )
        self.assertEquals(   self.object3["uobjlink1"].get_object() , None )
        self.assertRaises(KeyError,self.object1.__getitem__,"foo")
        self.object1["ulink2"] = attr
        self.assertEquals(self.object1["ulink2"].get_object(),self.object3)
        self.assertEquals(self.object3["uobjlink1"].get_object(),self.object1)

    def testUnstoredWithShadow(self):
        self.dummyparent["usobjlink1"] = dlk.CreateAnchorPoint(self.dummyparent)
        attr = MMUnstorableAttribute("foo", dlk.CreateAnchorPoint(self.object1) , self.object1)
        self.assertRaises(KeyError,self.object1.__getitem__,"foo")
        attr.set_value (dlk.ConnectTo( self.object3["usobjlink1"]))
        attr.set_value (dlk.ConnectTo( self.object2["usobjlink1"]))
        self.assertEquals(   self.object2["usobjlink1"].get_object() , None )
        self.assertEquals(   self.object3["usobjlink1"].get_object() , None )
        self.assertRaises(KeyError,self.object1.__getitem__,"foo")
        self.object1["uslink2"] = attr
        self.object2["usobjlink1"] = dlk.ConnectTo( self.object1["uslink2"])
        self.assertEquals(self.object1["uslink2"].get_object(),self.object2)
        self.assertEquals(self.object2["usobjlink1"].get_object(),self.object1)
        self.assertEquals(self.dummyparent["usobjlink1"].get_object(),None)
        self.assertEquals(self.dummyparent["usobjlink1"].get_anchor(),self.dummyparent)
    
    def testSetValueMovingAnchor(self):
        self.dummyparent["anchor"] = dlk.CreateAnchorPoint(self.dummyparent)
        self.assertEquals(self.dummyparent["anchor"].get_anchor(),self.dummyparent)
        self.dummyparent["anchor"].set_value(dlk.CreateAnchorPoint(self.system["Template"]))
        self.assertEquals(self.dummyparent["anchor"].get_anchor(),self.system["Template"])
        self.dummyparent["anchor"].set_value(dlk.CreateAnchorPoint(self.dummyparent["anchor"]))
        self.assertEquals(self.dummyparent["anchor"].get_anchor(),self.dummyparent["anchor"])
        self.dummyparent["anchor"].set_value(dlk.CreateAnchorPoint(self.dummyparent))
        self.assertEquals(self.dummyparent["anchor"].get_anchor(),self.dummyparent)

    def testSetValueMovingAnchorInUnstorable(self):
        attr = MMUnstorableAttribute("foo", dlk.CreateAnchorPoint(self.object1) , self.object1)
        self.assertEquals(attr.get_anchor(),self.object1)
        attr.set_value(dlk.CreateAnchorPoint(self.system["Dummy"]))
        self.assertEquals(attr.get_anchor(),self.system["Dummy"])
        attr.set_value(dlk.CreateAnchorPoint(self.object1))
        self.assertEquals(attr.get_anchor(),self.object1)
        
        

def getTestNames():
	return [ 'Dlink.DlinkTests' ] 

if __name__ == '__main__':
#    loader = unittest.TestLoader()
#    suite = loader.loadTestsFromTestCase(ObjectTests)
#    suite.debug()
     import sys
     if "--debug" in sys.argv:
        sys.argv.remove("--debug")
        logging.getLogger("MysteryMachine.schema.MMDLinkValue").setLevel(1)
        logging.getLogger("MysteryMachine.schema.MMObject").setLevel(1)
    
     unittest.main()

