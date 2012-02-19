#!/usr/bin/env python
#   			grammarTest.py - Copyright Roger Gammans
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
Tests for the MysteryMachine.Schema.Locker module
"""
from __future__ import with_statement

from MysteryMachine.schema.Locker import * 
import unittest

class TransactionManagerStub(object):
    """A mock transactionmanager so the MystertMachine still 
     works untl I've tested all the other parts needed"""
    def __init__(self,):
        self.writing =set()
        self.reading = set()
    def start_write(self,node):
        self.writing.add(node)
    def end_write(self,node):
        self.writing.remove(node)
    def start_read(self,node):
        self.reading.add(node)
    def end_read(self,node):
        self.reading.remove(node)
    def maybe_abort(self,xaction):
        import copy
        for n in copy.copy(self.reading):
            n.end_read()
        for n in copy.copy(self.writing):
            n.end_write()
        



class MockNode(object):
    def __init__(self,):
        self.in_write = False
        self.in_read = False
        self.done = False
        self.done_read = False
        self.done_write = False
        self.tm =  TransactionManagerStub()

    def get_tm(self,):
        return self.tm

    def get_root(self):
        return self

    def start_read(self,):
        self.tm.start_read(self)
        self.in_read = True

    def end_read(self,):
        #assert self.in_read,"trying to end a read outside in_read"
        self.in_read = False
        self.tm.end_read(self)

    def start_write(self,):
        self.tm.start_write(self)
        self.in_write = True

    def end_write(self,):
        #assert self.in_write,"trying to end a write outside in_write"
        self.in_write = False
        self.tm.end_write(self)


##This is not intended to be part of Mock Node,
# we monkeypatch it in for tests
def do_something(self):
    self.done = True
    if self.in_write: self.done_write =True
    if self.in_read: self.done_read =True


def recurse(self,):
    self.do_something()

class DummyException(Exception): pass

class lockerTest(unittest.TestCase):

    def setUp(self,):
         self.n = MockNode()

    def testGenericLock(self,):
        ##Test normally entry exit
        self.assertFalse(self.n.in_read)
        with GenericLock(self.n,"read"):
            self.assertTrue(self.n.in_read)
        self.assertFalse(self.n.in_read)

        self.assertFalse(self.n.in_write)
        with GenericLock(self.n,"write"):
            self.assertTrue(self.n.in_write)
        self.assertFalse(self.n.in_write)

        ##Test abnormal exit.
        self.assertFalse(self.n.in_write)
        raised = False
        try:
            with GenericLock(self.n,"write"):
                self.assertTrue(self.n.in_write)
                raise DummyException()
        except DummyException:
            raised = True
        self.assertFalse(self.n.in_write)
        #CHeck exception got propgatied too.
        self.assertTrue(raised)


    def testReadLock(self,):
        ##Test normally entry exit
        self.assertFalse(self.n.in_read)
        with ReadLock(self.n):
            self.assertTrue(self.n.in_read)
        self.assertFalse(self.n.in_read)

        ##Test abnormal exit.
        self.assertFalse(self.n.in_read)
        raised = False
        try:
            with ReadLock(self.n):
                self.assertTrue(self.n.in_read)
                raise DummyException()
        except DummyException:
            raised = True
        self.assertFalse(self.n.in_read)
        #CHeck exception got propgatied too.
        self.assertTrue(raised)

    def testWriteLock(self,):
        ##Test normally entry exit
        self.assertFalse(self.n.in_write)
        with WriteLock(self.n):
            self.assertTrue(self.n.in_write)
        self.assertFalse(self.n.in_write)

        ##Test abnormal exit.
        self.assertFalse(self.n.in_write)
        raised = False
        try:
            with WriteLock(self.n):
                self.assertTrue(self.n.in_write)
                raise DummyException()
        except DummyException:
            raised = True
        self.assertFalse(self.n.in_write)
        #CHeck exception got propgatied too.
        self.assertTrue(raised)


    def test_Writer_decorator(self,):
        imethod = type(self.n.end_write)
        self.n.write = imethod(Writer(do_something),self.n,type(self.n))
        self.n.write()
        self.assertTrue(self.n.done)
        self.assertTrue(self.n.done_write)
        self.assertFalse(self.n.done_read)
        self.assertFalse(self.n.in_write)

    def test_Reader_decorator(self,):
        imethod = type(self.n.end_write)
        self.n.read = imethod(Reader(do_something),self.n,type(self.n))
        self.n.read()
        self.assertTrue(self.n.done)
        self.assertTrue(self.n.done_read)
        self.assertFalse(self.n.done_write)
        self.assertFalse(self.n.in_read)


if __name__ == '__main__':
    unittest.main()

