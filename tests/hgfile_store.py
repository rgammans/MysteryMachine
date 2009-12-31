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
from MysteryMachine.store.hgfile_store import *
from MysteryMachine.store.Base import Base
from MysteryMachine.store import GetPath
from base.scm import scmTests

import unittest

import os
import tempfile 
import shutil

import sys

class BasicStore(Base):
    uriScheme = "basic"
    def __init__(self,*args,**kwargs):
        super(BasicStore,self).__init__(*args,**kwargs)
        self.path = GetPath(args[0])         
        if 'create' in kwargs and kwargs['create']:
            os.mkdir(self.path)
    
    def get_path(self):
        return self.path

    def ReadFile(self,name):
        f = file(os.path.join(self.path,name),"r")
        rv = f.read()
        f.close()
        return rv

    def WriteFile(self,name,content):
        f = file(os.path.join(self.path,name),"w")
        f.write(content)
        f.close()
        self.Add_file(name)

class hgstoreTests(scmTests, unittest.TestCase):
    def setUp(self):
        StartApp(["--cfgengine=ConfigDict", "--cfgfile=test.cfg", "--testmode"])
        try:
            testpath = tempfile.mkdtemp("mysmachg")
        except:
            pass
        self.testtype = type("HgTestStore", (HgStoreMixin , BasicStore ), {'uriScheme':"hgbasic"} )
        #Ensure delte - will create again in a moment
        os.rmdir(testpath)
        self.store= self.testtype("hgbasic:"+testpath,create = True)
   

def getTestNames():
    	return [ 'hgfile_store.hgstoreTests' ] 

if __name__ == '__main__':
    unittest.main()
    
