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
            files = list( cl[0].manifest() )
        return cl, files

def DeleteFile(store,name,):
     if store.supports_txn: store.start_store_transaction()
     f = os.unlink(os.path.join(store.get_path(),name))
     store.Remove_file(name)
     if store.supports_txn: store.commit_store_transaction()

def WriteFile(store,name,content):
     if store.supports_txn: store.start_store_transaction()
     f = open(os.path.join(store.get_path(),name),"w")
     f.write(content)
     f.close()
     store.Add_file(name)
     if store.supports_txn: store.commit_store_transaction()

def ReadFile(store,name):
     f = open(os.path.join(store.get_path(),name),"r")
     rv = f.read()
     f.close()
     return rv



class scmTests(object):
    def testSCM(self):
        WriteFile(self.store,"test1","Test data")
        self.store.commit("commit msg")
        #Check size of changelog + files contained.
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEqual(len(clog),1)
        self.assertEqual(len(files),1)

        #Check uptodate 
        self.assertTrue(self.store.uptodate())

        #change a file.
        WriteFile(self.store,"test1","different data")
        self.store.commit("changed the data")
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEqual(len(clog),2)
        self.assertEqual(len(files),1)
 
        #add another file
        WriteFile(self.store,"test2","More test data")
 
        #Check uptodate 
        self.assertFalse(self.store.uptodate())

        # commit.
        self.store.commit("another commit")
        #Check size of changelog + files contained.
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEqual(len(clog),3)
        self.assertEqual(len(files),2)

        #Check uptodate 
        self.assertTrue(self.store.uptodate())

       
        #rollback - redo checks.
        self.store.rollback()
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEqual(len(clog),2)
        self.assertEqual(len(files),1)
        
   
        # revert - check file contents.
        changelog = list( self.store.getChangeLog() )
        rev = changelog[-1]
        self.store.revert(rev)
        self.assertEqual(ReadFile(self.store,"test1"),"Test data") 
        try:
            #Remove 'test2' before cleaning it is ok for it
            #to be removeed or to belfet by cleaning.
            #  - or to have gone already
            os.unlink(os.path.join(self.store.get_path(),"test2"))
        except Exception: pass
        self.doCleanTst()

    def testSCM_remove_add_the_same_file(self):
        """ This tests for a delete/recreate error where teh csm is told
        to remove the file but not add it back again"""
        WriteFile(self.store,"test1","Test data")
        self.store.commit("commit msg")
        #Check size of changelog + files contained.
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEqual(len(clog),1)
        self.assertEqual(len(files),1)

        DeleteFile(self.store,"test1",)
        #Use different data as some scm fail if to commit if not changes are in the
        # source files
        WriteFile(self.store,"test1","Test data1")
        self.store.commit("commit msg")
        clog  ,files = getfiles_and_changelog(self.store)
        self.assertEqual(len(clog),2)
        self.assertEqual(len(files),1)



    def doCleanTst(self):
        self.store.lock()
        self.store.clean()
        for dirpath,dirs,files in os.walk(self.store.get_path()):
             self.processDirs(dirs)
             self.assertEqual(len(files),0, f"Unexpected ({dirpath}) files: {files}")
        self.store.unlock() 

