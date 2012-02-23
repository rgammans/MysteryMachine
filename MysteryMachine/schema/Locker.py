#!/usr/bin/env python
#   			Locker.py - Copyright Roger Gammans
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
"""
MysteryMachine schema Lock utilities.

This module provides decorators and context managers which implement
the MysteryMachine schema locking protocol.

In most cases you won't need to worry about this protocol unless you
are implementing a new Attribute Values classs or extending the 
schema in some manner.

This context managers and decorators here are used to mark 
functions as readers or writers. It is not an error to 
call nested functions so wrapper around existing schema calls
do not need to me marked as Readers or Writers.

Additonally you should use the System level begin,commit,abort
transaction methods to group together your changes for ACID
compliance. 

The decorators here are used internally to inform the transaction
manager of which nodes are in use, (Read or write) by the 
current transaction.

"""


from __future__ import with_statement
import threading
import logging


class GenericLock(object):
    """A context manager type object for handling write locking"""
    def __init__(self,n,locktype):
        self.node = n
        self.tm   = n.get_root().get_tm()
        self.lock =   getattr(self.node,"start_"+locktype)
        self.unlock = getattr(self.node,"end_"+locktype)
        self.xaction= None

    def __enter__(self):
        self.xaction = self.lock()

    def __exit__(self,etype,evalue,tb):
        if etype is None:
            self.unlock()
        else:
            self.tm.maybe_abort(self.xaction)
        return False 


class WriteLock(GenericLock):
    """A write locking context manager"""
    def __init__(self,n):
        super(WriteLock,self).__init__(n,"write")

class ReadLock(GenericLock):
    """A read locking context manager"""
    def __init__(self,n):
        super(ReadLock,self).__init__(n,"read")


def Locker(locktype,arg):
    """A decorator type object for handling write locking"""
    def decorator(f):
        def wrapper(*args,**kwargs):
            node = None
            try:
                node = args[arg]
            except TypeError ,e:
                node = kwargs[arg]

            with GenericLock(node,locktype) as l:
                return f(*args,**kwargs)

        wrapper.__name__ = f.__name__
        wrapper.__doc__  = f.__doc__
        return wrapper
    return decorator



Writer = Locker('write',0)
Writer.__doc__ = """
This decorator should be used on a method which modifies it's
node in the MysteryMachine schema

"""
Reader = Locker('read',0)
Reader.__doc__ = """
This decorator should be used on a method which retruns a value 
based on it's nodes state.

"""
