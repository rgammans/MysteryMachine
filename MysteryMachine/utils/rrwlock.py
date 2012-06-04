#!/usr/bin/env python
#   			rrwlock.py - Copyright R Gammans
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

"""Recursive  reader-writer locks in Python
Many readers can hold the lock XOR one and only one writer"""


from __future__ import with_statement
import threading

#Based on public domain code from.
#From: http://www.majid.info/mylos/weblog/2004/11/04.html


class _mylocal(threading.local):
    def __init__(self):
        self.rcount = 0

class RRwLock:
  """
A simple reader-writer lock Several readers can hold the lock
simultaneously, XOR one writer. Write locks have priority over reads to
prevent write starvation.

This lock can be acquired recursively.
"""
  def __init__(self):
    self.rwlock = 0
    self.writers_waiting = 0
    self.monitor = threading.Lock()
    self.readers_ok = threading.Condition(self.monitor)
    self.writers_ok = threading.Condition(self.monitor)
    self.tlocal =  _mylocal()
    self.wcount =  0
    self.writer  = None


  def _acquire_read(self):
       while self.rwlock < 0 or self.writers_waiting:
            self.readers_ok.wait()
       self.rwlock += 1
       self.tlocal.rcount += 1

  def acquire_read(self):
    """
    Acquire a read lock. Several threads can hold this typeof lock.
    It is exclusive with write locks.
    """
    with self.monitor:
        if self.rwlock == -1 and self.writer == threading.currentThread():
            #We already have a write lock - we don't acquire try to acquire
            # a read lock.- we increment the number of write locks.
            self.wcount +=1 
        else:
            return self._acquire_read()

  def acquire_write(self):
       """
       Acquire a write lock. Only one thread can hold this lock, and
       only when no read locks are also held.

       This method does an implicit promote - so it's not a good idea
       to call this if you already have a read lock , unless you are very sure what
       you are doing. The promote converts all lock held by this thread to write locks
       """
       with self.monitor:
          if self.tlocal.rcount > 0:
              return self._promote()
          else:
              return self._acquire_write()

  def _acquire_write(self):
      #If we currently hold the write lock - just inc our count.
      if self.rwlock == -1 and self.writer == threading.currentThread():
          self.wcount +=1 
          return
      
      while self.rwlock != 0:
        self.writers_waiting += 1
        self.writers_ok.wait()
        self.writers_waiting -= 1
      self.writer = threading.currentThread()
      self.wcount = 1
      self.rwlock = -1

  def held(self,):
    """ Primairly used for debugging - as there is no
    meaning to the test as it responnse is tsale before
    you can do anything with it"""
    return self.rwlock != 0

  def _promote(self):
    """Promote an already-acquired read lock to a write lock
    WARNING: it is very easy to deadlock with this method"""
    #Release all our read locks...
    self.rwlock -= self.tlocal.rcount
    while self.rwlock != 0:
      self.writers_waiting += 1
      self.writers_ok.wait()
      self.writers_waiting -= 1
    self.writer = threading.currentThread()
    self.rwlock = -1
    #Convert count of read locks to count of write locks,   
    # this converts allour held read lock to write, and adds one for our new lock!
    self.wcount = self.tlocal.rcount + 1
    self.tlocal.rcount = 0

 
  def release(self):
    """
    Release a lock once, whether read or write.
    
    A Prmoted lock needs to released twice. Once fro the acquire_read() then 
    for the acquire_write()
    """
    with self.monitor:
      #Determine lock type.
      wlock = self.rwlock < 0
      if wlock:
        self.wcount -= 1
        if self.wcount == 0:
          self.rwlock = self.tlocal.rcount 
          self.writer = None
      else:
        self.rwlock -= 1
        self.tlocal.rcount -= 1
        if self.tlocal.rcount < 0:
            raise RuntimeError()
      
      wake_writers = self.writers_waiting and self.rwlock == 0
      wake_readers = self.writers_waiting == 0 and self.rwlock >= 0

    if   wake_writers: self.wake_writers()
    elif wake_readers: self.wake_readers()

  def wake_writers(self):
      self.writers_ok.acquire()
      self.writers_ok.notify()
      self.writers_ok.release()

  def wake_readers(self):
      self.readers_ok.acquire()
      self.readers_ok.notifyAll()
      self.readers_ok.release()

if __name__ == '__main__':
  import time
  rwl = RRwLock()
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
  Reader().start()
  time.sleep(1)
  Reader().start()
  time.sleep(1)
  ReaderWriter().start()
  time.sleep(1)
  WriterWriter().start()
  time.sleep(1)
  Reader().start()
