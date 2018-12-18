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

import logging

from MysteryMachine.schema.Locker import * 
import unittest
from mock.schema_top import *

## Ensure there is alogging handler
logging.getLogger("").addHandler(logging.StreamHandler())

class MockNode(object):
    def __init__(self,):
        self.in_write = False
        self.in_read = False
        self.done = False
        self.done_read = False
        self.done_write = False
        fp = fakeParent()
        self.is_deleted = False
        self.tm =  fp.tm
        self.written = False
        self.discarded = False

    def get_tm(self,):
        return self.tm

    def get_root(self):
        return self

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

    def writeback(self,):
        self.written = True

    def discard(self,):
        self.discarded = True

    def _do_notify(self,): pass

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
        self.assertFalse(self.n.written)

        self.assertFalse(self.n.in_write)
        with GenericLock(self.n,"write"):
            self.assertTrue(self.n.in_write)
        self.assertFalse(self.n.in_write)
        self.assertTrue(self.n.written)

        self.n.written =False
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
        self.assertFalse(self.n.written)
        #CHeck exception got propgatied too.
        self.assertTrue(raised)


    def testReadLock(self,):
        ##Test normally entry exit
        self.assertFalse(self.n.in_read)
        with ReadLock(self.n):
            self.assertTrue(self.n.in_read)
        self.assertFalse(self.n.in_read)
        self.assertFalse(self.n.written)

        ##Test abnormal exit.
        self.assertFalse(self.n.in_read)
        raised = False
        try:
            with ReadLock(self.n):
                self.assertTrue(self.n.in_read)
                raise DummyException()
        except DummyException:
            raised = True
        self.assertFalse(self.n.written)
        self.assertFalse(self.n.in_read)
        #CHeck exception got propgatied too.
        self.assertTrue(raised)

    def testWriteLock(self,):
        ##Test normally entry exit
        self.assertFalse(self.n.in_write)
        with WriteLock(self.n):
            self.assertTrue(self.n.in_write)
        self.assertFalse(self.n.in_write)
        self.assertTrue(self.n.written)

        ##Test abnormal exit.
        self.assertFalse(self.n.in_write)
        raised = False
        self.n.written = False
        try:
            with WriteLock(self.n):
                self.assertTrue(self.n.in_write)
                raise DummyException()
        except DummyException:
            raised = True
        self.assertFalse(self.n.written)
        self.assertFalse(self.n.in_write)
        #CHeck exception got propgatied too.
        self.assertTrue(raised)


    def test_Writer_decorator(self,):
        class Node(MockNode):
            @Writer
            def write(self,):
                do_something(self,)

        self.n= Node()
        self.n.write()
        self.assertTrue(self.n.done)
        self.assertTrue(self.n.done_write)
        self.assertFalse(self.n.done_read)
        self.assertFalse(self.n.in_write)

    def test_Reader_decorator(self,):

        class Node(MockNode):
            @Reader
            def read(self,):
                do_something(self,)

        self.n = Node()
        self.n.read()
        self.assertTrue(self.n.done)
        self.assertTrue(self.n.done_read)
        self.assertFalse(self.n.done_write)
        self.assertFalse(self.n.in_read)

    def test_test_Write_recusre_decorator(self,):
        class Node(MockNode):
            @Writer
            def write(self,):
                recurse(self,)

            @Writer
            def do_something(self,):
                do_something(self,)


        self.n = Node()
        self.n.write()
        self.assertTrue(self.n.done)
        self.assertTrue(self.n.done_write)
        self.assertFalse(self.n.done_read)
        self.assertFalse(self.n.in_write)

if __name__ == '__main__':
    unittest.main()

