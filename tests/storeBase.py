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
Tests for the MysteryMachine MMStore base module
"""

from MysteryMachine import * 
from MysteryMachine.store import *
from MysteryMachine.store.Base import *

import unittest

class fakeBase(object):
    pass

class fakeSys(fakeBase):
   def getSelf(self):
        return self 

class sysTests(unittest.TestCase):
    def setUp(self):
        StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"]) 

    def testRegistration(self):
        self.assertRaises(KeyError,GetStore,"test:")
        class teststore(Base):
            uriScheme = "test"
        self.assertTrue(isinstance(GetStore("test:") , teststore))

    def testUriHandlers(self):
        # Test GetPath
        self.assertEquals(GetPath("kks:asdas"),"asdas")
        self.assertEquals(GetPath("kksia:hsasdas:a\sad:"),"hsasdas:a\sad:")
        # Test GetScheme
        self.assertEquals(GetScheme("kks:asdas"),"kks")
        self.assertEquals(GetScheme("kksia:hsasdas:a\sad:"),"kksia")
        # Test GetCanonical
        class cantest1(Base): 
            uriScheme = "identity"
 
        class cantest2(Base):
            uriScheme = "dummy"
            @staticmethod
            def GetCanonicalUri(uri):
                return "dummy%:"
        
        self.assertEquals(GetCanonicalUri("identity:asdasda"),"identity:asdasda")
        self.assertEquals(GetCanonicalUri("dummy:asdasd")    ,"dummy:dummy%:")

    def testLoaded(self):
        class teststore(Base):
            uriScheme = "test2"
        # Test create.
        testobj = CreateStore("test2:qwertyuiop:e")
        self.assertTrue(isinstance(testobj,teststore))
        # Test geturi
        self.assertEquals(testobj.getUri(),"test2:qwertyuiop:e")
        # test get/set owner. 
        owncontainter = dict()
        owncontainter["Owner"] = fakeSys()
        testobj.set_owner(owncontainter["Owner"])
        self.assertTrue(testobj.get_owner().getSelf() is owncontainter["Owner"])
        owncontainter["Owner"]  = None
        def operateOnProxy(testobj):
            return testobj.get_owner().getSelf()
        self.assertRaises(ReferenceError, operateOnProxy , testobj)

def getTestNames():
    	return [ 'mmsystemTest.sysTests' ] 

if __name__ == '__main__':
    unittest.main()
    

