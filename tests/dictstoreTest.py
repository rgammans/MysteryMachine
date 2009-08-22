#!/usr/bin/env python
#   			storeTest.py - Copyright Roger Gammans
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
Tests for the MysteryMachine dictstore  module
"""

from MysteryMachine import * 
from MysteryMachine.store.dict_store import *

import unittest

def listHelper(seq):
    result = []
    for i in seq:
        result.append(i)
    return result

class DummySystemClass:
    def getSelf(self):
        return self

DummySystem=DummySystemClass()

class storeTests(unittest.TestCase):
    """
    These test are intended to be generic store tests so that this test suite
    can be updated to help form a basic test suite for MysteryMachine store modules
    """
    def setUp(self):
        StartApp(["--cfgengine=pyConfigDict", "--cfgfile=test.cfg", "--testmode"]) 
        self.store=dict_store("dict:test")
        self.store.set_owner(DummySystem)

    def testCategories(self):
        cats=list(self.store.EnumCategories())
        self.assertEqual(len(cats),0)
        self.store.NewCategory("One",None)
        self.store.NewCategory("Two",None)
        cats=list(self.store.EnumCategories())
        self.assertEqual(len(cats),2)
        self.store.DeleteCategory("One")
        cats=list(self.store.EnumCategories())
        self.assertEqual(len(cats),1)

    def testObjects(self):
        #Check empty categories are..
        self.store.NewCategory("One",None)
        self.store.NewCategory("Two",None)
        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(len(objs1),0)
        self.assertEqual(len(objs2),0)
        
        o11=self.store.NewObject("One",None)
        o12=self.store.NewObject("One",None)
        o21=self.store.NewObject("Two",None)


        o1=self.store.GetObject("One:"+o12)
        
        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(len(objs1),2)
        self.assertEqual(len(objs2),1)
   
        self.store.DeleteObject("One"+":"+o12)
        self.store.DeleteObject("Two"+":"+o21)

        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(len(objs1),1)
        self.assertEqual(len(objs2),0)
   
    
def getTestNames():
    	return [ 'dictstoreTest.storeTests' ] 

if __name__ == '__main__':
    unittest.main()
    
