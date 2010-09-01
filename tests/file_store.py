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
from MysteryMachine.store.file_store import *

import unittest
from base.store import storeTests

import tempfile 
import shutil

class DummySystemClass:
    def getSelf(self):
        return self

DummySystem=DummySystemClass()

class filestoreTests(storeTests,unittest.TestCase):
    def mySetUp(self):
        StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"])
        self.mpath = tempfile.mkdtemp(prefix="mysmac")
        self.store=filestore("attrfile:"+self.mpath,create = False)
        self.store.set_owner(DummySystem)
        self.has_scm = False
    
    def tearDown(self):
        self.store.lock()
        shutil.rmtree(self.mpath)
        self.store.unlock()
#        os.rmdir(self.mpath)

    def testCanonicalise(self):
        import os
        self.assertEqual(self.store.GetCanonicalUri("."),os.getcwd())
        try:
            import posix
            #Skip test on non posix OS.
            self.assertEqual(self.store.GetCanonicalUri("~"),os.getenv("HOME"))
        except ImportError:
            pass
        path= tempfile.mkdtemp()
        try:
            os.remove("/tmp/mys-mac-test-symlink")
        except OSError:
            pass
        os.symlink(path,"/tmp/mys-mac-test-symlink")
        parentpath = os.path.realpath(path+os.sep+"..")
        self.assertEqual(self.store.GetCanonicalUri("/tmp/mys-mac-test-symlink"),path)
        self.assertEqual(self.store.GetCanonicalUri("/tmp/mys-mac-test-symlink/.."),parentpath)
        newpath  = path+os.path.sep+"test"
        os.mkdir(newpath)
        self.assertEqual(self.store.GetCanonicalUri("/tmp/mys-mac-test-symlink/test"),newpath)
        self.assertEqual(self.store.GetCanonicalUri("/tmp/mys-mac-test-symlink/test/.."),path)
        self.assertEqual(self.store.GetCanonicalUri("/tmp/mys-mac-test-symlink/../test/.."),parentpath)


class test2(storeTests,unittest.TestCase):
    def mySetUp(self):
        StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"])
        prefix = ""
        self.tmpexists = True
        try:
            import posix
            #Under possix try the same thing in a home dir.
            prefix = "~" 
        except ImportError:
            pass
        self.mpath = prefix + tempfile.mkdtemp(prefix="mysmac")
        self.parentpath = os.path.normpath(os.path.expanduser(self.mpath+os.path.sep+".."))
        self.tmpexists = os.path.exists(self.parentpath)
        os.makedirs(os.path.expanduser(self.mpath))
       
        self.store=filestore("attrfile:"+self.mpath,create = False)
        self.store.set_owner(DummySystem)
        self.has_scm = False
    
    def tearDown(self):
        self.store.lock()
        shutil.rmtree(os.path.expanduser(self.mpath))
        self.store.unlock()
        if not self.tmpexists: 
            os.rmdir(self.parentpath)


def getTestNames():
    	return [ 'file_store.filestoreTests' , 'file_store.tests2' ] 

if __name__ == '__main__':
    unittest.main()
    
