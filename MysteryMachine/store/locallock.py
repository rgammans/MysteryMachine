#!/usr/bin/env python
#   			locallock.py - Copyright %author%
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
#
import threading
from  MysteryMachine.utils.locks import RRwLock

""" This is currently the lock manager in the MysteryMachine
library, however the plan is to support alternative lockmanagers,
for instance on that can meditate mulitprocess access to hgafile
stores.

As a result of the the lock manager not being a known object the
each schema node (MMBase) provides a lock property which is reserved
for use by the lock manager.

"""



class lock(object):
    classlock = threading.Lock()
    def __init__(self):
        self._ = None

    def __getattr__(self,attr):
        with self.__class__.classlock:
            if self._ is None:
                self._ = RWLock()

        return getattr(self._,attr)
  
    def __del__(self):
        assert self._ and not self._.held() , "Lock deleted while held"

class LocalLocks(object):
    """A local manager for simple in-process only locks

    

   """

    def __init__(self):
        self.locks = {}
        self.lock  = threading.Lock()

    def get_lock_object(self):
        """Return a new lock object to populate a node with"""
        return RRwLock()

    def wlock(self,node):
        #We don't check the lock type here because the effect
        # of doing would mean that the
        node.lock.acquire_write()

    def wunlock(self,node):
        node.lock.release()

    def rlock(self,node):
        node.lock.acquire_read()

    def runlock(self,node):
        #We can't check the lock type here because if the lock has
        # been promoted then it is now completely a write lock.
        node.lock.release()
