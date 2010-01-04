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
from MysteryMachine.store.hgfile_class import *

import unittest
from base.store import storeTests
from base.scm import scmTests

import tempfile 
import shutil

class DummySystemClass:
    def getSelf(self):
        return self

DummySystem=DummySystemClass()

class filestoreTests(scmTests,storeTests,unittest.TestCase):
    def mySetUp(self):
        StartApp(["--cfgengine=ConfigDict", "--cfgfile=test.cfg", "--testmode"])
        self.mpath = tempfile.mkdtemp(prefix="mysmac")
        os.rmdir(self.mpath)
        self.store=HgFileStore("hgafile:"+self.mpath,create = True)
        self.store.set_owner(DummySystem)
        self.has_scm     = True
    
    def tearDown(self):
        self.store.lock()
        shutil.rmtree(self.mpath)
        self.store.unlock()
#        os.rmdir(self.mpath)

    def processDirs(self,dirs):
        if '.hg' in dirs:
           #Don't scan .hg directory.
           del dirs[dirs.index('.hg')]


def getTestNames():
    	return [ 'file_store.filestoreTests' ] 

if __name__ == '__main__':
    unittest.main()
    
