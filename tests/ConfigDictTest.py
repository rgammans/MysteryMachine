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
Tests for the MysteryMachine.Schema AttributeValue module
"""

from MysteryMachine.ConfigDict import *
import unittest


class ConfigDictTest(unittest.TestCase):
    def setUp(self):
        self.cfg= pyConfigDict()
        self.cfg.read("test.cfg")
        pass
    
    def testRead(self):
        self.assertEqual(type(self.cfg["testsection"]),pyConfigDictSection)
        self.assertEqual(int(self.cfg["testsection"]["test"]),1)
        #TODO test __iter__    
   
    def testWrite(self):
        self.assertEqual(type(self.cfg["testsection"]),pyConfigDictSection)
        self.cfg["testsection"]["newval"]=1
        self.assertEqual(type(self.cfg["testsection"]),pyConfigDictSection)
        self.assertEqual(int(self.cfg["testsection"]["newval"]),1)

    def testDelete(self):
        self.assertEqual(type(self.cfg["testsection"]),pyConfigDictSection)
        self.assertEqual(int(self.cfg["testsection"]["test"]),1)
        del self.cfg["testsection"]["test"]
        self.assertEqual(self.cfg["testsection"]["test"],None)

    def testDict(self):
        self.assertEqual(type(self.cfg["extensions"]),pyConfigDict)
        self.assertEqual(type(self.cfg["extensions"]["testsection"]),pyConfigDictSection)
        self.assertEqual(int(self.cfg["extensions"]["testsection"]["test"]),1)
        self.assertEqual(int(self.cfg["extensions"]["value"]),1)

    def testList(self):
        self.assertEqual(type(self.cfg["testlist"]),pyConfigList)
        self.assertEqual(int(self.cfg["testlist"][0]),1)
        self.assertEqual(type(self.cfg["testlist"][1]),pyConfigDict)


def getTestNames():
	return [ 'ConfigDictTest.ConfigDictTest' ] 

if __name__ == '__main__':
    unittest.main()

