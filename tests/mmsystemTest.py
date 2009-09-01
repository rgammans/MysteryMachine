#!/usr/bin/env python
#   			mmsystemTest.py - Copyright Roger Gammans
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
Tests for the MysteryMachine MMSystem  module
"""

from MysteryMachine import * 
from MysteryMachine.schema.MMSystem import *

import MysteryMachine.store.dict_store

import unittest


class sysTests(unittest.TestCase):
    def setUp(self):
        StartApp(["--cfgengine=pyConfigDict", "--cfgfile=test.cfg", "--testmode"]) 
        self.sys=MMSystem.Create("dict:test")

    def testCategory(self):
        cats=list(self.sys.EnumCategories())
        self.assertEqual(len(cats),0)
        self.sys.NewCategory("One",None)
        self.sys.NewCategory("Two",None)
        cats=list(self.sys.EnumCategories())
        self.assertEqual(len(cats),2)
        self.sys.DeleteCategory("One")
        cats=list(self.sys.EnumCategories())
        self.assertEqual(len(cats),1)

    def testObjects(self):
        #Check empty categories are..
        self.sys.NewCategory("One",None)
        self.sys.NewCategory("Two",None)
        objs1=list(self.sys.EnumObjects("One"))
        objs2=list(self.sys.EnumObjects("Two"))
        self.assertEqual(len(objs1),0)
        self.assertEqual(len(objs2),0)
        
        o11=self.sys.NewObject("One",None)
        o12=self.sys.NewObject("One",None)
        o21=self.sys.NewObject("Two",None)
  
        self.assertTrue(self.sys.get_object("One",repr(o12).split(":")[1]) is o12)
        
        objs1=list(self.sys.EnumObjects("One"))
        objs2=list(self.sys.EnumObjects("Two"))
        self.assertEqual(len(objs1),2)
        self.assertEqual(len(objs2),1)
   
        self.sys.DeleteObject(repr(o12))
        self.sys.DeleteObject(repr(o21))

        objs1=list(self.sys.EnumObjects("One"))
        objs2=list(self.sys.EnumObjects("Two"))
        self.assertEqual(len(objs1),1)
        self.assertEqual(len(objs2),0)
   
        o21=self.sys.NewObject("Two",None)
    
    def testLoaded(self):
        # __init__ del calls them ok.
        # Test open / create semanitcs.
        self.assertEquals(UnEscapeSystemUri(EscapeSystemUri("dict:test")),"dict:test")
        self.assertEquals(EscapeSystemUri("dict:test"),str(self.sys))
        self.assertTrue(GetLoadedSystemByName(str(self.sys)) is self.sys)
      
      
def getTestNames():
    	return [ 'mmsystemTest.sysTests' ] 

if __name__ == '__main__':
    unittest.main()
    
