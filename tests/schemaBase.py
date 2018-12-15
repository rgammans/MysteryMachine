#/!/usr/bin/env python
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
Tests for the MysteryMachine.schema MMBase class
"""

from __future__ import with_statement

from MysteryMachine.schema.MMBase import *
from MysteryMachine import *
import unittest
from mock.schema_top import *

class foo(MMBase):
   def __init__(self):
        super(foo,self).__init__() 

#def __init__(self):
#        print "foo init()"
#        print super()
#        super().__init__()

class bar(object):
    def __init__(self,owner):
         self.owner = owner 
         self.is_deleted = False
    def __hash__(self):
         return hash(self.owner)
    def __eq__(self,o):
          return type(o) == type(self) and self.owner == o.owner

class BaseTest(unittest.TestCase):
    def testInit(self):
        with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml"]) as g:
            g=None
            g=MMBase()
            #This tests __init__ completes.
            self.assertTrue(g is not None)


    def testCanicalise(self):
        with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml"]) as g:
            m  = MMBase()
            self.assertEqual("hi",m.canonicalise("Hi"))
            self.assertEqual("hi_world",m.canonicalise("Hi_world"))
            self.assertRaises(ValueError,m.canonicalise,";")
            self.assertRaises(ValueError,m.canonicalise,"s ad ")
            self.assertRaises(ValueError,m.canonicalise,"sdas/das;")
            self.assertRaises(ValueError,m.canonicalise,"kjkl\\jlkjsa")
            self.assertRaises(ValueError,m.canonicalise,"sdA:Ass")
            self.assertRaises(ValueError,m.canonicalise,"foo,bar")
            self.assertRaises(ValueError,m.canonicalise,"sad.ss")
            self.assertRaises(ValueError,m.canonicalise,"[ss")
            self.assertRaises(ValueError,m.canonicalise,"s]s")
            self.assertRaises(ValueError,m.canonicalise,"*")
            self.assertRaises(ValueError,m.canonicalise,"\"hiya\"")
            self.assertRaises(ValueError,m.canonicalise,"ss``")
            self.assertRaises(ValueError,m.canonicalise,"ss=")

    def testContainer(self):
        with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml"]) as g:
            m = MMContainer()
            m.owner = fakeParent()
            v = bar("one")
            m._set_item(1,v)
            #Whitebox test.
            self.assertTrue(m.cache[1] is v)
            self.assertTrue(m._get_item(1,bar,"one") is v)
            vf2 = m._get_item(2,bar,"two")
            self.assertEqual(vf2,bar("two"))
            self.assertTrue(m._get_item(2,bar,"two") is vf2)
            m._invalidate_item(1)
            self.assertRaises(KeyError ,m.cache.__getitem__,1)
            self.assertFalse(m._get_item(1,bar,"one") is v)


    def testContainerEnum(self):
        with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml"]) as g:
            m = MMContainer()
            m.owner = fakeParent()
            v = bar("one")
            m._set_item("1",v)
            self.assertIn("1",list(m._EnumX(lambda :[".hidden","nothidden"],)))
            self.assertNotIn(".hidden",list(m._EnumX(lambda :[".hidden","nothidden"],)))
            self.assertIn("nothidden",list(m._EnumX(lambda :[".hidden","nothidden"],)))
            self.assertIn(".hidden",list(m._EnumX(lambda :[".hidden","nothidden"],inc_hidden = True)))
            #Check valguard
            self.assertNotIn("1",list(m._EnumX(lambda :[],val_guard = lambda x:x is not v)))




    def testNotify(self):
        def update(obj):
            update.count+=1
        update.count = 0
        with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml"]) as g:
            m = MMContainer()
            m.owner = fakeParent()
            v = bar("one")
            self.val = v
            m.register_notify(update)
            m._set_item(1,v)
            m._invalidate_item(1)
            self.assertTrue(update.count > 0)
            last= update.count
            m.unregister_notify(update)
            m._set_item(1,v)
            m._invalidate_item(1)
            self.assertEqual(update.count,last)
  

def getTestNames():
	return [ 'schemaBase.BaseTest' ] 

if __name__ == '__main__':
    unittest.main()

