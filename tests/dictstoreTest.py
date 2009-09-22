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
from base.store import storeTests

class DummySystemClass:
    def getSelf(self):
        return self

DummySystem=DummySystemClass()

testscount = 0

class dictstoreTests(storeTests,unittest.TestCase):
    """
    These test are intended to be generic store tests so that this test suite
    can be updated to help form a basic test suite for MysteryMachine store modules
    """
    def mySetUp(self):
        global testscount
        StartApp(["--cfgengine=pyConfigDict", "--cfgfile=test.cfg", "--testmode"]) 
        #Ensure each new time this starts we use a new system
        testscount = testscount + 1
        self.store=dict_store("dict:test"+str(testscount))
        self.store.set_owner(DummySystem)
   
    
def getTestNames():
    	return [ 'dictstoreTest.dictstoreTests' ] 

if __name__ == '__main__':
    unittest.main()
    
