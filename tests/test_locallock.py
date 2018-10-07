#!/usr/bin/env python
#   			test_locallock.py - Copyright Roger Gammans
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
Tests for the MysteryMachine Minimal lock manager. 
"""

from MysteryMachine.store.locallock import LocalLocks
import unittest
import thread, threading
import time

def start_new_thread( func, args ,kwargs = None):
    threading.Thread(target = func, args =args,kwargs = kwargs).start()


class Node(object):
    def __init__(self,lock):
        self.lock = lock

class LockManagerTest(unittest.TestCase):
    def setUp(self):
        self.lm = LocalLocks()
        self.node = Node(self.lm.get_lock_object())

    def test_write_lock_unlock(self):
        self.assertFalse(self.node.lock and self.node.lock.held())
        self.lm.wlock(self.node)
        self.assertTrue(self.node.lock.held())
        self.lm.wunlock(self.node)
        self.assertFalse(self.node.lock.held())
 
    def test_read_lock_unlock(self):
        self.assertFalse(self.node.lock and self.node.lock.held())
        self.lm.rlock(self.node)
        self.assertTrue(self.node.lock.held())
        self.lm.runlock(self.node)
        self.assertFalse(self.node.lock.held())
       
    def test_rw_conflict(self):
        def writer():
            self.lm.wlock(self.node)
            self.gotlock = True
            
        self.assertFalse(self.node.lock and self.node.lock.held())
        self.lm.rlock(self.node)
        self.assertTrue(self.node.lock.held())
        self.gotlock= False
        start_new_thread(writer,())
        self.assertTrue(self.node.lock.held())
        time.sleep(1)
        self.assertFalse(self.gotlock)
        self.assertTrue(self.node.lock.held())
        self.lm.runlock(self.node)
        time.sleep(1)
        self.assertTrue(self.gotlock)
        self.assertTrue(self.node.lock.held())
        self.lm.wunlock(self.node)

    def test_ww_conflict(self):
        wait1 = threading.Semaphore(0)
        wait2 = threading.Semaphore(0)
        def writer():
            self.lm.wlock(self.node)
            self.gotlock = True
            wait1.acquire()            
            self.lm.wunlock(self.node)
            wait2.release()

        self.assertFalse(self.node.lock and self.node.lock.held())
        self.lm.wlock(self.node)
        self.assertTrue(self.node.lock.held())
        self.gotlock= False
        start_new_thread(writer,())
        time.sleep(1)
        self.assertTrue(self.node.lock.held())
        self.assertFalse(self.gotlock)
        self.lm.wunlock(self.node)
        time.sleep(1)
        self.assertTrue(self.gotlock)
        self.assertTrue(self.node.lock.held())
        wait1.release()
        wait2.acquire()

    def test_wr_conflict(self):
        wait1 = threading.Semaphore(0)
        wait2 = threading.Semaphore(0)
 
        def reader():
            self.lm.rlock(self.node)
            self.gotlock = True
            wait1.acquire()            
            self.lm.runlock(self.node)
            wait2.release()
            
        self.lm.wlock(self.node)
        self.gotlock= False
        start_new_thread(reader,())
        time.sleep(1)
        self.assertFalse(self.gotlock)
        self.lm.wunlock(self.node)
        time.sleep(1)
        self.assertTrue(self.gotlock)
        wait1.release()
        wait2.acquire()



def getTestNames():
	return [ 'test_lockman.LockManagerTest' ] 

if __name__ == '__main__':
    unittest.main()

