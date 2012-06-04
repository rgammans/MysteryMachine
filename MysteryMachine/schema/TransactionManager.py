#!/usr/bin/env python
#   			TransactionManager.py - Copyright R G Gammans
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

from __future__ import with_statement

import threading
import logging

class Transaction(object):
    def __init__(self):
       self.reset()

    def __nonzero__(self):
        return bool(self.count)
 
    def reset(self):
        self.count = 0
        self.manual = False
        self.rlocked = [ ]
        self.wlocked = [ ]

    def inc(self,manual,readnode,writenode):
        if not self.count:
            self.begin(manual)

        self.count += 1
        if writenode is not None: self.wlocked += [ writenode ]
        if readnode is not None: self.rlocked += [ readnode ]

    def dec(self,manual):
        if not self.count:
            raise RuntimeError("Not in Transaction")

        self.count -=1 

        if not self.count:
            self.end(manual)
            if self.manual:
                raise RuntimeError("Forcable completed a user xaction - lock count error")

    def begin(self,manual):
        self.manual =manual
     
    def end(self,manual):
        if self.manual and manual:
            self.manual = False


class TransactionProperty(threading.local):
    def __init__(self):
        self.xaction = Transaction() 
    def __get__(self,instance,owner):
        return self.xaction
    def __set__(self,instance,value):
        self.xaction = value 
     

class TransactionManager(object):
    """Transaction management for the MysteryMachine system

    This class implements the user level locking APIs or intent signalling
    APIs and manages starting commit and aborting transactions. 

    This class is also the gateway to the plugabble lock managers.
    
    We need pluggable lock managers as different store will need different
    ways of co-ordinating lock between mulitple process if the support
    multi -access.

    Hooks however are provided to support multiprocess access if needed

    This object has a state variable which can be one of
        'idle','xaction_aborted','xaction_commited','in_xaction'

    (and a number of commit internal phases)
    The first three are functionally identical except that they indicate
    the last operations results. 'in_xaction' should only be possible
    if self.xaction.count > 0 and indicates a transaction is in progress.
      

    """
    #Yes this is a global per_thread count of locks held.
    xaction = TransactionProperty()

    def __init__(self,lockmanager,store):
        self.lm = lockmanager
        self.logger = logging.getLogger("MysteryMachine.schema.TransactionManager.tm")
        self.store  = store
        #Yes this is a global per_thread count of locks held.
        self.state   = 'idle'
        #self.xaction = Transaction()

    def inc(self,m):
        if self.state not in [ "idle","in_xaction","xaction_aborted","xaction_commited"]:
            raise RuntimeError("in comit")
        self.state = 'in_xaction'
        self.xaction.inc(m,None,None)

    def dec(self,m,commit = True):
        self.xaction.dec(m)
        if not self.xaction:
            if commit:
                self._do_commit()
            else:
                self._do_abort()

    def start_write(self,node):
        self.logger.debug( "tm start write node %r"%node)
        if node not in self.xaction.wlocked:
            self.logger.debug( "locking %r"%node)
            self.lm.wlock(node)
            self.xaction.inc(False,None,node)
        else: self.xaction.inc(False,None,None)

        self.state = 'in_xaction'
        return self.xaction

    def start_read(self,node):
        self.logger.debug( "tm start read node %r"%node)
        if node not in self.xaction.rlocked:
            if node not in self.xaction.wlocked:
                #A Write lock is good enough.
                self.lm.rlock(node)
                #but only add it the list if
                #we actually lock it.
                rnode = node
            else: rnode = None
            self.xaction.inc(False,rnode,None)
        else: self.xaction.inc(False,None,None)
        self.state = 'in_xaction'
        return self.xaction


    def _check_xaction(self,xaction):
        ok = True
        if self.xaction is  not xaction:
            #No exception as we don't want to interfere more with
            # dodgy control flow path.
            self.logger.error("Mismatch transaction detected %r <->%r"%(self.xaction,xaction))
            #FIXME XXX XXX XXX FIXME
            #ok = False
        return ok


    def end_read(self,node,xaction):
        self.logger.debug("end read node %r"%node)
        if not self._check_xaction(xaction): return
        self.dec(False)

    def end_write(self,node,xaction):
        self.logger.debug("end write node %r"%node)
        if not self._check_xaction(xaction): return
        self.dec(False)
        self.logger.debug( "\t count %i"%self.xaction.count  )

    def begin_xaction(self):
        self.inc(True)
        return self.xaction

    def commit_xaction(self,xaction):
        if not self._check_xaction(xaction): return
        self.dec(True)

    def abort_xaction(self,xaction):
        if not self._check_xaction(xaction): return
        self.dec(True,False)

    def maybe_abort(self,xaction):
        """Used to abort only auto tranasctions"""
        #if not self._check_xaction(xaction): return
        self.logger.debug( "maybe abort (%s)-%i"%(self.xaction.manual,self.xaction.count))
        self.dec(False)
 
    def abort_write(self,xaction,node):
        """Used to abort only auto tranasctions"""
        #if not self._check_xaction(xaction): return
        self.dec(False,False)
 

    abort_read = abort_write

    def _do_abort(self):
        self.store.lock()
        self._release_allr()
        for obj in self.xaction.wlocked:
            obj.discard()
        self._release_allw()
        self.store.unlock()
        #Create new tranasction
        self.xaction = Transaction()
        self.state = 'xaction_aborted' 

    def _do_commit(self):
        self.state = "tx_commit_1"
        txn = self.store.start_store_transaction() #Begin rollbackable xaction
        self._release_allr()
        self.state = "tx_commit_2"
        try:
            #Sort into topdown order.(Len of node address uses as a simple
            #indicator of depth in tree). An objects parents *must* have
            #a shorter length node name.                          
            # We need to do this so any containers are created first.
            #
            ordered_modified = sorted(self.xaction.wlocked,key=lambda x:len(repr(x)))

            #First do depth first removal of deleted nodes.
            for obj in reversed(ordered_modified):
                if obj.is_deleted: obj.writeback()

            #Then do topdown creation and modification.
            for obj in ordered_modified:
                if not obj.is_deleted:
                    obj.writeback()
        except:
            self.state = "tx_commit_abort"
            import sys
            self.logger.debug("Commit except: %s,%s,%s"%sys.exc_info())
            self.store.abort_store_transaction()
            self._do_abort()
            raise
        else:
            self.state = "tx_commit_3"
            notify_list = list(self.xaction.wlocked)
            self._release_allw()
            self.state = "tx_commit_4"
            self.store.commit_store_transaction()
            for obj in notify_list:
                obj._do_notify()
        self.logger.debug( "commit")
        self.state = 'xaction_commited' 


    def _release_allr(self):
        for obj in self.xaction.rlocked:        
            self.lm.runlock(obj)
        self.xaction.rlocked = [ ]

    def _release_allw(self):
        for obj in self.xaction.wlocked:
            self.lm.wunlock(obj)
        self.xaction.wlocked = [ ]

    commited = property(lambda self: self.state == 'xaction_commited')

