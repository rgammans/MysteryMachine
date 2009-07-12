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

from MysteryMachine.dict_store import *

import MysteryMachine.schema.MMAttributeValue
import unittest



class SystemProxy(dict_store):
    def __init__(self,name):
        dict_store.__init__(self,self)
        self.objmap = dict()
        LoadSystem(name,self)
        self.name = name

    def get_object(self,cat,id):
        path = cat +":"+id
        if not self.HasCategory(cat):
            self.NewCategory(cat,None)
        if not path in self.objmap:
            self.objmap[path]=self.NewObject(cat,None)
        return self.GetObject(cat+":"+self.objmap[path])

    def __repr__(self):
        return self.name

class ObjectTests(unittest.TestCase):
    def setUp(self):
        StartApp(["--cfgengine=pyConfigDict", "--cfgfile=test.cfg", "--testmode"]) 
        self.system=SystemProxy("ObjectTests")
        self.dummyparent             = self.system.get_object( "Template","1", )
        self.dummyparent[".defname"] = "name"
        
        self.parent                  = self.system.get_object( "Template","2", )
        self.parent[".defname"]      =":mm:`:name`"
        
        self.object                  = self.system.get_object("Dummy","1") 
        self.object.set_parent(self.parent)       


    def testgetparent(self):
        print "----starting getparent test------"
        self.assertTrue(self.parent is self.object.get_parent())
        print "----completed getparent test------"
 
    def testdefname(self):
#        """
#        Disabled tests until MMParser's tests are complete
        print "----starting defname test------"
        self.assertEquals(str(self.dummyparent),"name")
        self.object["name"]="test"
        print "--- next assert----"
        self.assertEquals(str(self.object),"test")
        print "----completed defname test------"
#        """
#        pass

    def testParentRef(self):
        p=self.object.get_parent()
        p["test"] = "test"
        self.assertEquals(self.object["test"],p["test"])
        self.object["test"] = "other"
        self.assertNotEquals(self.object["test"],p["test"])

def getTestNames():
	return [ 'Object.ObjectTests' ] 

if __name__ == '__main__':
    unittest.main()

