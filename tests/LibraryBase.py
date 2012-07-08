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

from MysteryMachine.ConfigYaml import *
#Use our own hash class to test for modification.
from MysteryMachine.ExtensionSecureID import *
import unittest

import types
import logging
import sys
import tempfile

########################################
## DANGER, Will Robinson,  DANGER 
########################################
## This test is pretty naff - it
## depends critically on the current
## implementation of the yaml module return native dict and lists,
## rather than another implemantion of them.
## but the test was quickly copied from the 
## ConfigDict tests

## I suspect just commenting out the type tests
## will still leave the a valuable test - as all the 
## dict actions are sepearatley tested... But still

logging.getLogger("").addHandler(logging.StreamHandler(sys.stderr)) 

class ConfigYamlTest(unittest.TestCase):
    def setUp(self):
        self.id = ExtensionSecureID.fromPathName("tests/test.yaml")
        self.cfg= ConfigYaml(False)
        self.cfg.read("tests/test.yaml")
        pass
    
    def testRead(self):
        self.assertEqual(type(self.cfg["testsection"]),dict)
        self.assertEqual(int(self.cfg["testsection"]["test"]),1)
        #TODO test __iter__    
   
    def testWrite(self):
        self.assertEqual(type(self.cfg["testsection"]),dict)
        self.cfg["testsection"]["newval"]=1
        self.assertEqual(type(self.cfg["testsection"]),dict)
        self.assertEqual(int(self.cfg["testsection"]["newval"]),1)

    def testDelete(self):
        self.assertEqual(type(self.cfg["testsection"]),dict)
        self.assertEqual(int(self.cfg["testsection"]["test"]),1)
        del self.cfg["testsection"]["test"]
        self.assertRaises(KeyError,lambda : self.cfg["testsection"]["test"])

    def testDict(self):
        self.assertEqual(type(self.cfg["extensions"]),dict)
        self.assertEqual(type(self.cfg["extensions"]["testsection"]),dict)
        self.assertEqual(int(self.cfg["extensions"]["testsection"]["test"]),1)
        self.assertEqual(int(self.cfg["extensions"]["value"]),1)

    def testList(self):
        self.assertEqual(type(self.cfg["testlist"]),list)
        self.assertEqual(int(self.cfg["testlist"][0]),1)
        self.assertEqual(type(self.cfg["testlist"][1]),dict)
    
    def testiter(self):
        for i in self.cfg:
            self.assertFalse(self.cfg is i)
        for i in self.cfg["testsection"]:
            self.assertFalse(self.cfg["testsection"] is i)
        for i in self.cfg["testlist"]:
            self.assertFalse(self.cfg["testlist"] is i)       

    def testNoFile(self):
        tstfile = tempfile.NamedTemporaryFile(suffix=".yaml")
        tstfile = tstfile.name
        try:
            os.remove(tstfile) 
        except:
            pass
        cfg= ConfigYaml()
        cfg.read(tstfile)
        cfg['test1'] ="foo"
        cfg['test2'] = {'a':'2' }
        cfg.write()
        cfg = None
        cfg1 = ConfigYaml()
        cfg1.read(tstfile)
        self.assertEquals(cfg1['test1'],"foo")
        self.assertEquals(cfg1['test2'],{'a':'2' })
         #cleanup
        try:
            os.remove(tstfile) 
        except:
            pass 

    

    def testTestMode(self):
        tstfile = tempfile.NamedTemporaryFile(suffix=".yaml")
        tstfile = tstfile.name
        #Set testmode
        cfg= ConfigYaml()
        cfg.read(tstfile)
        cfg.testmode()
        #Make change
        cfg["new"]="Really!"
        #Release the handle
        cfg = None
        cfg1=ConfigYaml()
        cfg1.read("/tmp.mmtest.yaml")
        self.assertRaises(KeyError,lambda x:cfg1[x],"new")

def getTestNames():
	return [ 'ConfigYamlTest.ConfigYamlTest' ] 

if __name__ == '__main__':
    unittest.main()

