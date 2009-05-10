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
from MysteryMachine.schema.MMObject import MMObject
from MysteryMachine.schema.MMAttribute import * 

import MysteryMachine.schema.MMAttributeValue
import unittest



class ObjTest(MMObject):
    def __init__(self,id,parent,**kwargs):
  
        super(ObjTest,self).__init__(id,parent)
        self.items = {}
        for key in kwargs:
           self.items[key] = kwargs[key] 
 #       self.parent = SystemProxy()

    def __repr__(self):
        return self.id
    def __delitem__(self,name):
        del self.items[name]
    def __setitem__(self,name,val):
        self.items[name]=val
    def __getitem__(self,name):
        if name not in self.items:
            return super(ObjTest,self).__getitem__(name)
        else:
            return self.items[name]

class SystemProxy:
    cache = dict()
    def get_object(self,cat,id):
        id = cat +":" +id
        if id not in self.__class__.cache:
            self.__class__.cache[id] = ObjTest(id,self)
        return self.__class__.cache[id]

class ObjectTests(unittest.TestCase):
    def setUp(self):
        StartApp(["--cfgengine=pyConfigDict", "--cfgfile=test.cfg", "--testmode"]) 
        self.dummyparent             = SystemProxy().get_object( "Template","1", )
        self.dummyparent[".defname"] = "name"
        
        self.parent                  = SystemProxy().get_object( "Template","2", )
        self.parent[".defname"]      ="mm`:name`"
        
        self.object                  = SystemProxy().get_object("Dummy","1") 
        self.object.set_parent(self.parent)       


    def testgetparent(self):
        self.assertTrue(self.parent is self.object.get_parent())
 
    def testdefname(self):
        """
        Disabled tests until MMParser's tests are complete
        self.assertEquals(str(self.dummyparent),"name")
        self.object["name"]="test"
        self.assertEquals(str(self.object),"test")
        """
        pass

    def testParentRef(self):
        p=self.object.get_parent()
        p["test"] = CreateAttributeValue("simple" , [ MMAttributePart( "", "test") ] , )
        self.assertEquals(self.object["test"],p["test"])
        self.object["test"] = CreateAttributeValue("simple" , [ MMAttributePart( "" , "other") ] )
        self.assertNotEquals(self.object["test"],p["test"])

def getTestNames():
	return [ 'Object.ObjectTests' ] 

if __name__ == '__main__':
    unittest.main()

