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

import MysteryMachine.schema.MMAttributeValue
import unittest
import logging


class ObjectTests(unittest.TestCase):
    def setUp(self):
        StartApp(["--cfgengine=ConfigDict", "--cfgfile=test.cfg", "--testmode"]) 
        self.logger = logging.getLogger("")
        self.system=MMSystem.Create("dict:ObjectTests")
        self.system.NewCategory( "Template" )
        self.dummyparent             = self.system.NewObject( "Template" )
        self.dummyparent[".defname"] = "name"
        
        self.parent                  = self.system.NewObject( "Template" )
        self.parent[".defname"]      =":mm:`:name`"
        
        self.system.NewCategory( "Dummy" )
        self.object                  = self.system.NewObject("Dummy") 
        self.object.set_parent(self.parent)       

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
        self.logger.debug( "----completed defname test------")

    def testAttrRef(self):
        self.object["data"] ="some data"
        self.assertEquals(str(self.object["data"]),"some data")
        def noAttrTst():
            return self.object["nodata"]
        self.assertRaises(KeyError,noAttrTst)

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

