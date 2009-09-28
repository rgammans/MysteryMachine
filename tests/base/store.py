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
from MysteryMachine.schema.MMObject import MMObject
from MysteryMachine.schema.MMAttribute import MMAttribute

import sys

def listHelper(seq):
    result = []
    for i in seq:
        result.append(i)
    return result

class storeTests(object):
    """
    These test are intended to be generic store tests so that this test suite
    can be updated to help form a basic test suite for MysteryMachine store modules
    """
    def setUp(self):  
        self.mySetUp()

    def testCategories(self):
        cats=list(self.store.EnumCategories())
        self.assertEqual(len(cats),0)
        self.store.NewCategory("One")
        self.store.NewCategory("Two")
        cats=list(self.store.EnumCategories())
        self.assertEqual(len(cats),2)
        self.store.DeleteCategory("One")
        cats=list(self.store.EnumCategories())
        self.assertEqual(len(cats),1)

    def testObjects(self):
        #Check empty categories are..
        self.store.NewCategory("One")
        self.store.NewCategory("Two")
        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(len(objs1),0)
        self.assertEqual(len(objs2),0)
        
        o11=self.store.NewObject("One")
        o12=self.store.NewObject("One")
        o21=self.store.NewObject("Two")


        o1=self.store.GetObject("One:"+o12)
        self.assertTrue(isinstance(o1,MMObject))
        self.assertTrue(o1 is self.store.GetObject("One:"+o12))
        self.assertFalse(o1 is self.store.GetObject("One:"+o11))        

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

    #TODO Seperate out the bits which use the internal if.
    def testAttribute(self):
        #Create some cats and objs.
        self.store.NewCategory("One")
        self.store.NewCategory("Two")
        o11=self.store.NewObject("One")
        o12=self.store.NewObject("One")
        o21=self.store.NewObject("Two")

        #Set an attribute.
        o12obj = self.store.GetObject("One:"+o12)
        attr = MMAttribute("name","fred",o12obj)
        self.store.SetAttribute("One"+":"+o12+":name",attr)

        #Count attributes.
        objs1=list(self.store.EnumAttributes("One:"+o12))
        objs2=list(self.store.EnumAttributes("Two:"+o21))
        print objs1
        self.assertEqual(len(objs1),1)
        self.assertEqual(len(objs2),0)
        
        #Test presence
        self.assertTrue(self.store.HasAttribute("One:"+o12+":name"))
        self.assertFalse(self.store.HasAttribute("One:"+o11+":name"))
        self.assertFalse(self.store.HasAttribute("One:"+o12+":notname"))

        #Retrieve attribute.
        self.assertEquals(str(self.store.GetAttribute("One:"+o12+":name")),"fred")
        # Test same instance. 
        #TODO -  reconstruct attribute purely from the backing store.
         
    def testProxyObj(self):
        """
        Test the Object proxy used in MMObjects.
        
        this prolly requires an overridable method to get the obj to
        start with  
        """
        pass 


