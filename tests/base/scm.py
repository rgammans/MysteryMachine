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
Tests for the MysteryMachine store scm functions module
"""

import unittest

import os
import tempfile 
import shutil

import sys


def getfiles_and_changelog(store):
        cl = list(store.getChangeLog())
        files = []
        if len(cl) > 0:
            for f in cl[len(cl)-1]: files+= [ f] 
        return cl, files


def WriteFile(store,name,content):
     f = file(os.path.join(store.get_path(),name),"w")
     f.write(content)
     f.close()
     store.Add_file(name)

def ReadFile(store,name):
     f = file(os.path.join(store.get_path(),name),"r")
     rv = f.read()
     f.close()
     return rv



class scmTests(object):
    def testSCM(self):
        WriteFile(self.store,"test1","Test data")
        self.store.commit("commit msg")
        #Check size of changelog + files contained.
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEquals(len(clog),1)
        self.assertEquals(len(files),1)

        #Check uptodate 
        self.assertTrue(self.store.uptodate())

        #change a file.
        WriteFile(self.store,"test1","different data")
        self.store.commit("changed the data")
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEquals(len(clog),2)
        self.assertEquals(len(files),1)
 
        #add another file
        WriteFile(self.store,"test2","More test data")
 
        #Check uptodate 
        self.assertFalse(self.store.uptodate())

        # commit.
        self.store.commit("another commit")
        #Check size of changelog + files contained.
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEquals(len(clog),3)
        self.assertEquals(len(files),2)

        #Check uptodate 
        self.assertTrue(self.store.uptodate())

       
        #rollback - redo checks.
        self.store.rollback()
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEquals(len(clog),2)
        self.assertEquals(len(files),1)
 
        # revert - check file contents.
        changelog = list( self.store.getChangeLog() )
        rev = changelog[0]
        self.store.revert(rev)
        self.assertEquals(ReadFile(self.store,"test1"),"Test data") 

        self.store.lock()
        self.store.clean()
        for dirpath,dirs,files in os.walk(self.store.get_path()):
             if '.hg' in dirs:
                #Don't scan .hg directory.
                del dirs[dirs.index('.hg')]
             self.assertEquals(len(files),0)
    

