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


def getfiles_and_changelog(store):
        cl = list(store.getChangeLog())
        files = []
        if len(cl) > 0:
            for f in cl[len(cl)-1]: files+= [ f] 
        return cl, files

class hgstoreTests(unittest.TestCase):
    def setUp(self):
        StartApp(["--cfgengine=pyConfigDict", "--cfgfile=test.cfg", "--testmode"])
        try:
            testpath = tempfile.mkdtemp("mysmachg")
        except:
            pass
        self.testtype = type("HgTestStore", (HgStoreMixin , BasicStore ), {'uriScheme':"hgbasic"} )
        #Ensure delte - will create again in a moment
        os.rmdir(testpath)
        sys.stderr.write("hgbasic:path - %s\n" % testpath)
        self.store= self.testtype("hgbasic:"+testpath,create = True)
   
    def testSCM(self):
        self.store.WriteFile("test1","Test data")
        self.store.commit("commit msg")
        #Check size of changelog + files contained.
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEquals(len(clog),1)
        self.assertEquals(len(files),1)

        #change a file.
        self.store.WriteFile("test1","different data")
        self.store.commit("changed the data")
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEquals(len(clog),2)
        self.assertEquals(len(files),1)
 
        #add another file
        self.store.WriteFile("test2","More test data")
        # commit.
        self.store.commit("another commit")
        #Check size of changelog + files contained.
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEquals(len(clog),3)
        self.assertEquals(len(files),2)
        
        #rollback - redo checks.
        self.store.rollback()
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEquals(len(clog),2)
        self.assertEquals(len(files),1)
 
        # revert - check file contents.
        changelog = list( self.store.getChangeLog() )
        rev = changelog[0]
        self.store.revert(rev)
        self.assertEquals(self.store.ReadFile("test1"),"Test data") 

        pass

    
def getTestNames():
    	return [ 'hgfile_store.hgstoreTests' ] 

if __name__ == '__main__':
    unittest.main()
    
