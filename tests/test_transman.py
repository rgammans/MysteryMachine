#!/usr/bin/env python
#   			test_transman.py - Copyright Roger Gammans
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
Tests for the MysteryMachine TransactionManager
"""

from __future__ import with_statement

from MysteryMachine.schema.TransactionManager import * 
from MysteryMachine.schema.Locker import * 
from MysteryMachine.store.locallock import LocalLocks
import unittest
import thread
from mock.schema_top import mock_store
import time

class TestError(Exception):
    pass

class RootNode(object):
     def __init__(self,tm,store):
        self.store = store
        self.tm    = tm
        self.lm    = tm.lm

     def get_tm(self):
        return self.tm

     def get_lm(self):
        return self.tm.lm


class Node(object):
    def __init__(self,root):
        self.in_write = False
        self.in_read = False
        self.done = False
        self.done_read = False
        self.done_write = False
        self.is_deleted = False
        self.tm =  root.tm
        self.written = False
        self.discarded = False
        self._lock = None
        self.root = root
        self.store = root.store
        self.fail_write = False

    def start_read(self,):
        x = self.tm.start_read(self)
        self.in_read = True

    def end_read(self,x):
        #assert self.in_read,"trying to end a read outside in_read"
        self.in_read = False
        self.tm.end_read(self,x)

    def abort_read(self,x):
        #assert self.in_read,"trying to end a read outside in_read"
        self.in_read = False
        self.tm.abort_read(self,x)


    def start_write(self,):
        x = self.tm.start_write(self)
        self.in_write = True
        return x

    def end_write(self,x):
        #assert self.in_write,"trying to end a write outside in_write"
        self.in_write = False
        self.tm.end_write(self,x)

    def abort_write(self,x):
        #assert self.in_write,"trying to end a write outside in_write"
        self.in_write = False
        self.tm.abort_write(self,x)


    def _do_notify(self,): pass

    def get_root(self):
        return self.root

    def writeback(self):
        self.written = True
        #Verify Guarantee transaction manager is supposed to make
        assert self.store.in_txn, "store not locked during writeback"
        if self.fail_write: raise TestError("Cant")

    def discard(self):
        self.discarded = True
        #Verify Guarantee transaction manager is supposed to make
        #assert self.store.in_txn, "store not locked during discard"
    
    def fail_update(self):
        raise ValueError("Shan't")

    ##This whole method is really the decorator test.
    @Writer
    def set_value(self,v):
        #Check locked
        assert self.lock.held()  , "Node not locked on write"
        self.value = v
 
    def _get_lock(self,):
        if self._lock is None:
            self._lock = self.get_root().lm.get_lock_object()
        return self._lock
    
    lock = property(_get_lock,None,None)




class TransactionManagerTest(unittest.TestCase):
    def setUp(self):
        store = mock_store()
        lm    = LocalLocks()
        self.tm = TransactionManager(lm,store)
        root    = RootNode(self.tm,store)
        self.node = Node(root)

    def testauto_commit(self):
        self.assertFalse(self.tm.commited)
        x = self.tm.start_write(self.node)
        self.assertFalse(self.tm.commited)
        self.tm.end_write(self.node,x)
        self.assertTrue(self.tm.commited)

    def testmanual_commit(self):
        self.assertFalse(self.tm.commited)
        x = self.tm.begin_xaction()
        self.assertFalse(self.tm.commited)
        y = self.tm.start_write(self.node)
        self.assertFalse(self.tm.commited)
        self.tm.end_write(self.node,y)
        self.assertFalse(self.tm.commited)
        self.tm.commit_xaction(x)
        self.assertTrue(self.tm.commited)
    
    def test_recursive_lock(self):
        self.assertFalse(self.tm.commited)
        self.assertFalse(self.tm.commited)
        x= self.tm.start_write(self.node)
        self.assertFalse(self.tm.commited)
        y=self.tm.start_write(self.node)
        self.assertFalse(self.tm.commited)
        self.tm.end_write(self.node,y)
        self.assertFalse(self.tm.commited)
        self.tm.end_write(self.node,x)
        self.assertTrue(self.tm.commited)

    def test_rw_conflict(self):
        def writer():
            self.tm.start_write(self.node)
            self.gotlock = True
            
        x=self.tm.begin_xaction()
        y=self.tm.start_read(self.node)
        self.gotlock= False
        thread.start_new_thread(writer,())
        time.sleep(1)
        self.assertFalse(self.gotlock)
        self.tm.end_read(self.node,y)
        time.sleep(1)
        self.assertFalse(self.gotlock)
        self.tm.commit_xaction(x)
        time.sleep(1)
        self.assertTrue(self.gotlock)

    def test_ww_conflict(self):
        def writer():
            self.tm.start_write(self.node)
            self.gotlock = True
            
        x=self.tm.begin_xaction()
        y=self.tm.start_write(self.node)
        self.gotlock= False
        thread.start_new_thread(writer,())
        time.sleep(1)
        self.assertFalse(self.gotlock)
        self.tm.end_write(self.node,y)
        time.sleep(1)
        self.assertFalse(self.gotlock)
        self.tm.commit_xaction(x)
        time.sleep(1)
        self.assertTrue(self.gotlock)

    def test_wr_conflict(self):
        def reader():
            self.tm.start_read(self.node)
            self.gotlock = True
            
        x=self.tm.begin_xaction()
        y=self.tm.start_write(self.node)
        self.gotlock= False
        thread.start_new_thread(reader,())
        time.sleep(1)
        self.assertFalse(self.gotlock)
        self.tm.end_write(self.node,y)
        time.sleep(1)
        self.assertFalse(self.gotlock)
        self.tm.commit_xaction(x)
        time.sleep(1)
        self.assertTrue(self.gotlock)


    def test_autoabort(self):
        def _dotest():
            with WriteLock(self.node):
                self.node.fail_update()

        self.assertRaises(ValueError, _dotest)
        self.assertEquals(self.tm.state , "xaction_aborted")
        

    def test_noautoabort_manual_xaction(self):
        def _dotest():
            with WriteLock(self.node):
                self.node.fail_update()
        
        x=self.tm.begin_xaction()
        self.assertRaises(ValueError, _dotest)
        self.assertNotEquals(self.tm.state , "xaction_aborted")
        self.tm.commit_xaction(x)
        self.assertEquals(self.tm.state , "xaction_commited")
        self.assertTrue(self.tm.commited)

    def test_manual_abort(self):
        self.assertFalse(self.tm.commited)
        x=self.tm.begin_xaction()
        self.assertFalse(self.tm.commited)
        y=self.tm.start_write(self.node)
        self.assertFalse(self.tm.commited)
        self.tm.end_write(self.node,y)
        self.assertFalse(self.tm.commited)
        self.tm.abort_xaction(x)
        self.assertFalse(self.tm.commited)
        self.assertEquals(self.tm.state , "xaction_aborted")
        self.assertEquals(self.tm.xaction.count,0)

    def test_exception_during_commit(self):
        self.node.fail_write = True
        self.assertFalse(self.tm.commited)
        x = self.tm.start_write(self.node)
        self.assertFalse(self.tm.commited)
        self.assertRaises(TestError,self.tm.end_write,self.node,x)
        self.assertEquals(self.tm.state , "xaction_aborted")

class TransactionManagerDecoratorTest(unittest.TestCase):
    def setUp(self):
        store = mock_store()
        lm    = LocalLocks()
        self.tm = TransactionManager(lm,store)
        root    = RootNode(self.tm,store)
        self.node = Node(root)

    def testdecorator(self):
       self.assertFalse(self.tm.commited)
       self.node.set_value("a test value")
       self.assertTrue(self.tm.commited)

def getTestNames():
	return [ 'test_transman.LockManagerTest' , 'test_transman.TransactionManagerDecoratorTest' ] 

if __name__ == '__main__':
    unittest.main()

