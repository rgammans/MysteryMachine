#!/usr/bin/env python
#   			schema_top.py - Copyright Roger Gammans
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
This provides mocking object to simulated the various calls
which ascend the schema tree.

This allows us to test the leaf node types independently of 
their containers.
"""

##Import a mock object from higher up the schema -
# so we don't need to re implement it
#
# MMSYstem current as a mock TransactionManager until we 
# have fully integrated the ACID complaince features.

from MysteryMachine.schema.TransactionManager import TransactionManager
from MysteryMachine.schema.MMAttribute import * 


class mock_lockman:
    def wlock(*args): pass
    def wunlock(*args): pass
    def rlock(*args): pass
    def runlock(*args): pass

class mock_store(object):
    def __init__(self,):
        self.txns_committed = 0
        self.txns_aborted = 0
        self.attrs = {}
        self.attrs_txn = {}
        self.in_txn = False

    def start_store_transaction(self,*args):
        if self.attrs_txn: raise RuntimeError("Previous Txn not complete")
        if self.in_txn: raise RuntimeError("Previous Txn not complete")
        self.in_txn = True

    def abort_store_transaction(self,*args):
        if not self.in_txn: raise RuntimeError("Txn not started")
        self.attrs_txn = { }
        self.in_txn = False
        self.txns_aborted += 1

    def commit_store_transaction(self,*args):
        if not self.in_txn: raise RuntimeError("Txn not started")
        self.attrs.update(self.attrs_txn)
        self.attrs_txn = { }
        self.in_txn = False
        self.txns_committed += 1

    def SetAttribute(self,name,attrtype,attrparts):
        self.attrs_txn[name] = (attrtype,attrparts)

    def lock(*args): pass
    def unlock(*args): pass

class fakeParent:
    def __init__(self):
        self.updated = False
        self.store = mock_store()
        self.tm = TransactionManager(mock_lockman(),self.store)

    def Updated(self):
        return self.updated

    def get_nodeid(self,): return ""

    def getSelf(self,):
        return self

    def writeback(self,):
        self.updated = True
    def resetUpdate(self):
        self.updated = False

    def get_tm(self,):
        return self.tm 

    def get_encoding(self):
        return "ascii"

