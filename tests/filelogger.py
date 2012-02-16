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
Tests for the MysteryMachine store filelogger  module
"""

import unittest

import os
import tempfile 
import shutil
import time

import sys

import MysteryMachine.store.FileLogger as fl

def dontdo(*args,**kwargs): pass

class floggerTests(unittest.TestCase):
    def setUp(self,):
        self.dirname  = tempfile.mkdtemp()
        self.flog = fl.FileLogger(self.dirname)
        

    def tearDown(self):
        #self.flog.close()
        shutil.rmtree(self.dirname)
        #os.rmdir(self.dirname)
        pass


    def filecontents(self,fname):
        try:
            f =file(os.path.join(self.dirname,fname),"r")
            contents = "\n".join(f.readlines())
            f.close()
            return contents
        except: return None

    def testlogger(self):
        t = self.flog.start_transaction()
        self.flog.Add_File(t,"test1","Test data")
        self.flog.Add_File(t,"test2","Test other data")

        #Check no changes have been made.
        self.assertNotEqual(self.filecontents("test1") ,"Test data")
        self.assertNotEqual(self.filecontents("test2") ,"Test other data")

        self.flog.commit_transaction(t)
        #Check changes.
        self.assertEqual(self.filecontents("test1") ,"Test data")
        self.assertEqual(self.filecontents("test2") ,"Test other data")
    
        self.flog.freeze()
        self.assertEquals(self.flog.in_use_logs, [] )
        self.flog.thaw()
        
        t = self.flog.start_transaction()
        self.flog.Delete_File(t,"test1")
        self.assertEqual(self.filecontents("test1") ,"Test data")
        self.flog.commit_transaction(t)
        self.assertEqual(self.filecontents("test1") ,None)

        t = self.flog.start_transaction()
        self.assertRaises( OSError, self.flog.Add_File ,t,"foo/test2","Test other data99")
        
        self.flog.Create_Dir(t,"foo/")
        self.flog.Add_File(t,"foo/test2","Test other data102")
        self.flog.commit_transaction(t)
        #self.assertRaises( OSError , self.flog.commit_transaction,t)   
        self.assertEqual(self.filecontents("foo/test2") ,"Test other data102")

        #Test DeleteDir.
        t = self.flog.start_transaction()
        self.assertRaises(OSError , self.flog.Delete_Dir,t,"foo/")
        self.assertRaises(OSError , self.flog.Delete_Dir,t,"test2")
        self.assertRaises(OSError , self.flog.Delete_File,t,"foo/")
        self.assertRaises(OSError , self.flog.Add_File,t,"foo","data")
        self.flog.Delete_File(t,"foo/test2")
        self.flog.Delete_Dir(t,"foo/")
        self.flog.commit_transaction(t)

 
    def test_overlapp_detection(self):
        t = self.flog.start_transaction()
        self.assertRaises(fl.OverlappedTransaction, self.flog.start_transaction)
        #ok the cleanup

    def test_overlapp_recovery(self):
        #Build a logfile with an overlapped tx.
        t = self.flog.start_transaction()
        self.flog.Add_File(t,"test1","Test data")
        #White box trick to defeat overlapp detection, so
        #we can test how recovery fails wit a malformed log.
        self.flog.tx = None
        t = self.flog.start_transaction()
        self.flog.Add_File(t,"test2","Test other data")
        self.flog.commit_transaction(t)
        self.flog = None
        self.assertRaises(fl.RecoveryError, fl.FileLogger ,self.dirname)
        self.assertNotEqual(self.filecontents("test1") ,"Test data")

    def testlogger_recovery_abort(self,):
        #checkpint
        t = self.flog.start_transaction()
        self.flog.Add_File(t,"test1","Test data")
        self.flog.Add_File(t,"test2","Test other data")
        #Check no changes have been made.
        self.assertNotEqual(self.filecontents("test1") ,"Test data")
        self.assertNotEqual(self.filecontents("test2") ,"Test other data")

        self.flog = None
        self.flog2 = fl.FileLogger(self.dirname)
        self.flog2.freeze()
        self.assertNotEqual(self.filecontents("test1") ,"Test data")
        self.assertNotEqual(self.filecontents("test2") ,"Test other data")

    def testlogger_recovery_abort_then_commit(self,):
        #checkpint
        t = self.flog.start_transaction()
        self.flog.Add_File(t,"test1","Test data")
        self.flog.Add_File(t,"test2","Test other data")
        self.flog.abort_transaction(t)
        #Check no changes have been made.
        self.assertNotEqual(self.filecontents("test1") ,"Test data")
        self.assertNotEqual(self.filecontents("test2") ,"Test other data")

        t = self.flog.start_transaction()
        self.flog.Add_File(t,"test2","More other data")
        self.flog.Add_File(t,"test3","Test other data")
        self.flog.commit_transaction(t)
        self.flog = None
        self.assertNotEqual(self.filecontents("test1") ,"Test data")
        self.assertEqual(self.filecontents("test2") ,"More other data")
        self.assertEqual(self.filecontents("test3") ,"Test other data")


        self.flog2 = fl.FileLogger(self.dirname)
        self.flog2.freeze()
        self.assertNotEqual(self.filecontents("test1") ,"Test data")
        self.assertEqual(self.filecontents("test2") ,"More other data")
        self.assertEqual(self.filecontents("test3") ,"Test other data")


    def testlogger_recovery_commit(self,):
        t = self.flog.start_transaction()
        x1 = fl.ReplaceAll_Operation(os.path.join(self.dirname,"testA"),"DAyasda",self.flog.new_opid())
        x2 = fl.ReplaceAll_Operation(os.path.join(self.dirname,"testB"),"sDsdsaAyasda",self.flog.new_opid())
        #Castrate the operations so recovery is guranteed to have soemthing
        # to do.
        x1._do = dontdo
        x2._do = dontdo

        self.flog._add_operation(t,x1)
        self.flog._add_operation(t,x2)
        self.flog.commit_transaction(t)
        #Check no changes have been made.
        self.assertNotEqual(self.filecontents("testA") ,"DAyasda")
        self.assertNotEqual(self.filecontents("testB") ,"sDsdsaAyasda")

        self.flog = None
        #Open a new logger to trigegr recovery.
        self.flog2 = fl.FileLogger(self.dirname)
        self.flog2.freeze()
        #Get Fs quesicent and check recovery.
        self.assertEqual(self.filecontents("testA") ,"DAyasda")
        self.assertEqual(self.filecontents("testB") ,"sDsdsaAyasda")
        #check no

    def test_logfile_truncation(self,):
        #checkpint
        t = self.flog.start_transaction()
        self.flog.Add_File(t,"test1","Test data")
        self.flog.Add_File(t,"test2","Test other data")
        self.flog.commit_transaction(t)

        t = self.flog.start_transaction()
        self.flog.Add_File(t,"test2","More other data")
        self.flog.Add_File(t,"test3","Test other data")
        self.flog.commit_transaction(t)
        lfile = self.flog.logf.fname
        self.assertEquals(len(self.flog.in_use_logs), 1 ) 
        self.flog.freeze()
        
        #All Xactions are now committed.
        log = fl.LogFile(lfile,readonly = True)
        #Check there are no entries in the journal if we replay it.
        self.assertEquals(len(self.flog.in_use_logs), 0 ) 
        self.assertEquals(list(iter(log)), [ ] ) 
        self.flog.thaw()
 
        t = self.flog.start_transaction()
        self.flog.Add_File(t,"test2","Test other data")
        self.flog.commit_transaction(t)
        self.assertEquals(len(self.flog.in_use_logs), 1 ) 

        #Check we are reusing the exiting logfile
        self.assertEquals(self.flog.logname,lfile)
        

    def test_operations(self,):

        f = tempfile.NamedTemporaryFile()
        f.close()
        xact = fl.ReplaceAll_Operation(f.name,"testcontent","1")
        xact1 = fl.ReplaceAll_Operation(f.name,"testcontent",2)
        xact_str = str(xact)
        self.assertEqual(len(xact_str),len(xact))
        self.assertNotEqual(xact.opid,xact1.opid)
        
        #Check operation write.
        xact1.do()
        self.assertEquals(self.filecontents(f.name),"testcontent")

        xact2 = fl.JournaledOperation.load(iter(xact_str))
        self.assertEqual(xact2.opid,xact.opid)
        self.assertEqual(xact2.target,xact.target)
        self.assertEqual(xact2.content,xact.content)
        #Check callback
        self.called = False
        self.last = -1
        time.sleep(30)
        self.assertFalse(self.called)
        xact2.do(callback = self.completeCallback,sync = False)
        time.sleep(30)
        self.assertTrue(self.called)
        self.assertEqual(self.last,xact2.opid)
        

    def completeCallback(self,xid):
        self.last = xid
        self.called = True

#def getTestNames():
#    	return [ 'file_store.filestoreTests' , 'file_store.tests2' ] 

if __name__ == '__main__':
    unittest.main()
    
