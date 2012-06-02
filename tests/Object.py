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
Tests for the MysteryMachine.Schema MMObject  module
"""

from MysteryMachine import * 
from MysteryMachine.schema.MMSystem import * 
from MysteryMachine.schema.MMObject import MMObject
from MysteryMachine.schema.MMAttribute import * 

from MysteryMachine.store.dict_store import *

import MysteryMachine.Exceptions as Error

import MysteryMachine.schema.MMAttributeValue
import unittest
import logging
import itertools

class ObjectTests(unittest.TestCase):
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

        self.object2                  = self.system.NewObject("Template") 
        self.logger.debug( "dummy => " ,repr(self.dummyparent))
        self.logger.debug( "parent => " ,repr(self.parent))
        self.logger.debug( "object => " , repr(self.object))

    def testgetparent(self):
        self.logger.debug( "----starting getparent test------")
        self.assertTrue(self.parent is self.object.get_parent())
        self.logger.debug( "----completed getparent test------")



    def testdefname(self):
        self.logger.debug( "----starting defname test------")
        self.assertEquals(str(self.dummyparent),"name")
        self.object["name"]="test"
        self.logger.debug( "--- next assert----")
        self.assertEquals(str(self.object),"test")
        self.assertEquals(str(self.object2),repr(self.object2))
        self.logger.debug( "----completed defname test------")

    def testAttrRef(self):
        self.object["data"] ="some data"
        self.assertEquals(str(self.object["data"]),"some data")
        def noAttrTst(obj):
            return obj["nodata"]
        self.assertRaises(KeyError,noAttrTst,self.object)
        try:
            import MysteryMachine.store.file_store
        except:
            return
        ##Also test dereference using the filestore
        tmppath = tempfile.mkdtemp()
        os.rmdir(tmppath)
        self.sys2 = MMSystem.Create("attrfile:" + tmppath)
        self.sys2.NewCategory( "Dummy" )
        obj  = self.sys2.NewObject("Dummy")
        obj["data"] = "soemdata"
        self.assertEquals(str(obj["data"]),"soemdata")
        self.assertEquals(str(obj["DATa"]),"soemdata")
        self.assertRaises(KeyError,noAttrTst,obj) 

        obj["atref"]=obj["data"].getRef()
        self.assertEquals(obj,obj.getRef())
        self.assertEquals(obj["data"],obj["atref"].getSelf())


    def testParentRef(self):
        p=self.object.get_parent()
        p["test"] = "test"
        self.assertEquals(str(self.object["test"]),str(p["test"]))
        self.object["test"] = "other"
        self.assertNotEquals(str(self.object["test"]),str(p["test"]))
        #Test parent update
        p[".defname"] = "parent"
        #Test parent de-ref
        self.object[".defname"]= "object" 
        self.assertEquals(str(self.object), "object")
        self.assertEquals(str(p), "parent")

    def testDefaultParent(self):
        obj2 = self.system.NewObject("Dummy")
        self.assertEquals(str(obj2[".defname"]),"name") 
        #Test parent de-ref
        obj2[".defname"]= "object" 
        self.assertEquals(str(obj2), "object")
        self.assertEquals(str(self.dummyparent), "name")
 
    def testInheritedEval(self):
        p=self.object.get_parent()
        p["test"] = "test"
        self.object["test"] = "other"
        #Test parent update
        p["name"] = ":mm:`:test`"
        #Test parent ref
        self.assertEquals(p["name"].GetFullExpansion(), "test")
        self.assertEquals(self.object["name"].GetFullExpansion(), "other")
    
    def testFetchHiddenfrom_cache(self,):
        self.parent[".secret"] = "test"
        #Hold ref , to ensure attr stays in cache,
        s = self.object[".secret"]
        self.assertEquals("test",str(self.object[".secret"]))
 

    def testParentAbuse(self):
        self.object2["attribute"] ="An attribute"
        self.assertRaises(Error.InvalidParent,self.object.set_parent,self.object2["attribute"])

        # Try to create a pointless loop in the parent heirachy.
        self.assertRaises(Error.InvalidParent,self.parent.set_parent,self.object)
        #Just make sure endless loops don't happen
        self.assertRaises(KeyError,self.parent.__getitem__,"fooe")

    def testBreakParentRef(self):
        self.parent["testattr"] = "somedata"
        self.dummyparent["testattr"] = "otherdata"
        self.assertEquals(str(self.object["testattr"]),"somedata")
        self.object.set_parent(MMNullReferenceValue())
        self.assertRaises(KeyError,self.object.__getitem__,"testattr")

        myobj = self.system.NewObject("dummy")
        self.assertEquals(str(myobj["testattr"]),"otherdata")
        myobj = self.system.NewObject("dummy",MMNullReferenceValue())
        self.assertRaises(KeyError,myobj.__getitem__,"testattr")

        self.object.set_parent(self.parent)
        self.assertEquals(str(self.object["testattr"]),"somedata")
        v = self.object["testattr"]
        self.object.set_parent(MMNullReferenceValue())
        #Test fetch of disappeared attribute raises KeyErrpr
        self.assertRaises(KeyError,self.object.__getitem__,"testattr")
        
        #Test de-reference of store but dissapeared aatr raises 
        # ReferenceError
        self.assertRaises(ReferenceError,str,v.get_value())
        




    def testIterIf(self):
        self.assertRaises(KeyError,self.object.__getitem__,"testattr")
        self.object["Attr1"] = "some data"
        self.object["name"]  = "fred blogs"
        self.assertTrue("name" in self.object)
        self.assertTrue("attr1" in self.object)
        self.assertEquals(len(list(iter(self.object))),2)
        names = [ "attr1" , "name" ]
        fndNames= []
        for k,v in self.object.iteritems():
            self.assertTrue(k in names)
            self.assertFalse(k in fndNames)
            fndNames += [ k ]
            self.assertTrue(isinstance( v, MMAttribute))
            self.assertEquals(v,self.object[k])

        attrv = list(self.object.__iter__())
        self.assertEqual(len(attrv),2)
        attrk = list(self.object.iterkeys())
        self.assertEqual(len(attrk),2)

        for k,v in itertools.izip(attrk,attrv):
            self.assertEquals(self.object[k],v)
        
        #Check contains and iter are consistent.
        for a in attrk:
            self.assertTrue(a in names)

        p=self.object.get_parent()
        p["attr_none"]="fooo"
        attrk = list(self.object.EnumAttributes())
        self.assertEqual(len(attrk),3)
        #Check contains is false for inherited
        ok =False
        for a in attrk:
            if a not in names: ok = True
        self.assertTrue(ok,"__contains__ is true for inherited (should be false)")



    def testNotify(self):
       def testexpect(obj):
            self.exception = None
            try:
                attr = [ x.name for x in obj]
                for k,v in self.val.iteritems():
                    self.assertTrue(k in attr,"%s not in attributes"%k)
                    self.assertEquals(str(obj[k]),v)
            except Exception, e:
                self.exception =e

       def update(obj):
            update.count+=1
       update.count = 0
       lastcount = update.count 

       self.object["name"]  = "fred blogs"
       self.object.register_notify(update)
       self.object.register_notify(testexpect)
       self.assertEquals(update.count,lastcount)
       self.val ={ 'newname':'value'} 
       self.object['newname']='value'
       self.assertTrue(update.count > lastcount)
       lastcount = update.count 

       self.object["name"]  = "fred blogs2"
       self.assertTrue(update.count > lastcount)
       if self.exception: raise self.exception

       lastcount = update.count 

       self.object.unregister_notify(update)
       self.val["another"] ="brick in the wall"
       self.object["another"] ="brick in the wall"
       self.assertEquals(update.count,lastcount)
       if self.exception: raise self.exception


def getTestNames():
	return [ 'Object.ObjectTests' ] 

if __name__ == '__main__':
    unittest.main()

