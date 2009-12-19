#!/usr/bin/env python
#   			tests/utils.py - Copyright Roger Gammans
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
This is a combined test fro the MysteryMachine utils modules
"""

from MysteryMachine.utils import path,locks 
#Use our own hash class to test for modification.
import unittest

import os
import threading
import time

class UtilsTest(unittest.TestCase):
    def testPath_make_rel(self):
        path1 = [ "etc" , "something" , "else" , "somewhere", "else" ]
        path2 = [ "home" , "user" , "etc" , "something" ]

        self.assertEqual(path.make_rel(os.path.join(*path1),os.path.join(*path1)),[ "." ])
        self.assertEqual(path.make_rel(os.path.join(os.sep,*path1),os.sep),[ os.sep ])
        self.assertEqual(path.make_rel(os.sep,os.path.join(os.sep,*path1)), [ os.path.join(*path1) ])
        self.assertEqual(path.make_rel(os.path.join(*path2),os.path.join(*path1)),[ os.path.join(*path1) ])
        
        self.assertEqual(path.make_rel(os.path.join(*path2),os.path.join(*path1),os.path.join(*path2)),[ os.path.join(*path1) ,"." ])

    #
    # These next tests for the locking code aren't the best
    # tests. Eg, they almost certainly have poor coverage,
    # but I can see how to improve them to test thread corner
    # cases in a deterministic way. Patches welcome ;-).
    #
    def testLocks_RWLock(self):
        test = self
        class rwtest(threading.Thread):
            def run(self):
                  rwl = locks.RWLock()
                  class Reader(threading.Thread):
                    def run(self):
                      print self, 'start'
                      rwl.acquire_read()
                      print self, 'acquired'
                      time.sleep(5)    
                      print self, 'stop'
                      rwl.release()
                  class Writer(threading.Thread):
                    def run(self):
                      print self, 'start'
                      rwl.acquire_write()
                      print self, 'acquired'
                      time.sleep(10)    
                      print self, 'stop'
                      rwl.release()
                  class ReaderWriter(threading.Thread):
                    def run(self):
                      print self, 'start'
                      rwl.acquire_read()
                      print self, 'acquired'
                      time.sleep(5)    
                      rwl.promote()
                      print self, 'promoted'
                      time.sleep(5)    
                      print self, 'stop'
                      rwl.release()
                  class WriterReader(threading.Thread):
                    def run(self):
                      print self, 'start'
                      rwl.acquire_write()
                      print self, 'acquired'
                      time.sleep(10)    
                      print self, 'demoted'
                      rwl.demote()
                      time.sleep(10)    
                      print self, 'stop'
                      rwl.release()
                  r1 =Reader()
                  r1.start()
                  time.sleep(1)
                  r2 = Reader()
                  r2.start()
                  time.sleep(1)
                  rw = ReaderWriter()
                  rw.start()
                  time.sleep(1)
                  wr = WriterReader()
                  wr.start()
                  time.sleep(1)
                  r3 = Reader()
                  r3.start()
                  r1.join()
                  r2.join()
                  r3.join()
                  rw.join()
                  wr.join()

                  test.assertEquals(rwl.rwlock,0) 
                  test.assertEquals(rwl.writers_waiting,0) 
    
        workthread = rwtest()
        workthread.start()
        workthread.join(60.0)
        #If the test is still running we consider the
        # system to be deadlocked!
        self.assertFalse(workthread.isAlive()) 

    def testLocks_RRwLock(self):
        test = self
        class rwtest(threading.Thread):
            def run(self):
                  rwl = locks.RRwLock()
                  class Reader(threading.Thread):
                    def run(self):
                      print self, 'start'
                      rwl.acquire_read()
                      print self, 'acquired'
                      time.sleep(5)    
                      print self, 'stop'
                      rwl.release()
                  class Writer(threading.Thread):
                    def run(self):
                      print self, 'start'
                      rwl.acquire_write()
                      print self, 'acquired'
                      time.sleep(10)    
                      print self, 'stop'
                      rwl.release()
                  class ReaderWriter(threading.Thread):
                    def run(self):
                      print self, 'start'
                      rwl.acquire_read()
                      print self, 'acquired'
                      time.sleep(5)    
                      rwl.acquire_write()
                      print self, 'promoted'
                      time.sleep(5)    
                      print self, 'stop'
                      rwl.release()
                      rwl.release()
                  class WriterWriter(threading.Thread):
                    def run(self):
                      print self, 'start'
                      rwl.acquire_write()
                      print self, 'acquired'
                      time.sleep(10)    
                      rwl.acquire_write()
                      print self, 'acquired 2'
                      time.sleep(5)    
                      print self, 'stop 2'
                      rwl.release()
                      time.sleep(5)    
                      print self, 'stop'
                      rwl.release()
                  class ReaderReaderWriter(threading.Thread):
                    def run(self):
                      print self, 'start'
                      rwl.acquire_read()
                      print self, 'acquired'
                      time.sleep(2)
                      rwl.acquire_read()
                      print self, 'acquired 2'
                      time.sleep(5)    
                      rwl.acquire_write()
                      print self, 'promoted'
                      time.sleep(5)    
                      print self, 'stop'
                      rwl.release()
                      rwl.release()
                      rwl.release()
                  r1 = Reader()
                  r1.start()
                  time.sleep(1)
                  r2 = Reader()
                  r2.start()
                  time.sleep(1)
                  rw = ReaderWriter()
                  rw.start()
                  time.sleep(1)
                  ww =WriterWriter()
                  ww.start()
                  time.sleep(1)
                  r3= Reader()
                  r3.start()
                  time.sleep(20)
                  rrw = ReaderReaderWriter()
                  rrw.start()
 
                  r1.join()
                  r2.join()
                  r3.join()
                  rw.join()
                  ww.join()
                  rrw.join()
                  test.assertEquals(rwl.wcount,0)
                  test.assertEquals(rwl.rwlock,0) 
                  test.assertEquals(rwl.writers_waiting,0) 
    
        workthread = rwtest()
        workthread.start()
        workthread.join(60.0)
        #If the test is still running we consider the
        # system to be deadlocked!
        self.assertFalse(workthread.isAlive()) 

def getTestNames():
	return [ 'utils.UtilsTest' ] 

if __name__ == '__main__':
    unittest.main()

