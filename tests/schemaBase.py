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
Tests for the MysteryMachine.schema MMBase class
"""

from __future__ import with_statement

from MysteryMachine.schema.MMBase import *
from MysteryMachine import *
import unittest

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

class BaseTest(unittest.TestCase):
    def testInit(self):
        with StartApp(["--cfgengine=ConfigDict", "--cfgfile=test.cfg"]) as g:
            if not bar in foo.__bases__: 
                foo.__bases__ +=  ( bar, )
            g.GetExtLib().register_helper(foo,bar)
           
            MMBase()
            #This tests __init__ completes.
            self.assertTrue(True)

    def testExtensions(self):
         with StartApp(["--cfgengine=ConfigDict", "--cfgfile=test.cfg"]) as g:
            if not bar in foo.__bases__: 
                foo.__bases__ +=  ( bar, )
            g.GetExtLib().register_helper(foo,bar)
           
            f=foo()
            self.assertTrue(bar in f.__class__.__bases__)
            self.assertTrue(bar in map(lambda x:type(x) , f._helpers))


    def testCanicalise(self):
        with StartApp(["--cfgengine=ConfigDict", "--cfgfile=test.cfg"]) as g:
            m  = MMBase()
            self.assertTrue("hi",m.canonicalise("Hi"))
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




def getTestNames():
	return [ 'schemaBase.BaseTest' ] 

if __name__ == '__main__':
    unittest.main()

