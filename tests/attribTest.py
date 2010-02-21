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
Tests for the MysteryMachine.Schema AttributeValue module
"""
import sys
from MysteryMachine.schema.MMAttributeValue import MMAttributeValue
from MysteryMachine.schema.MMAttribute import * 
import unittest

class DummyPart:
    def __init__(self,x):
        self.x=x
    def get_value(self):
        return self.x

class fakeParent:
    def __init__(self):
        self.updated = False
    def Updated(self):
        return self.updated

    def __setitem__(self,name,val):
        self.updated = True
    def resetUpdate(self):
        self.updated = False
class attribTest(unittest.TestCase):
    
    def testCreate(self):
       attr=MMAttribute("document","test\n----\n\n\nA Message",None)
       #sys.stderr.write(str(attr.get_raw_rst))
       self.assertEqual(attr.get_raw_rst(),"test\n----\n\n\nA Message")

    # TODO
    # Test MMObject fetching
    # Test handling of parse errors.
    # Test AttributeValue export resolution.
    def testAttrValExport(self):
       attr=MMAttribute("document","test\n----\n\n\nA Message",None)
       self.assertEquals("test\n----\n\n\nA Message",attr.get_raw())

    def testAttrParentStuff(self):
       p = fakeParent()
       attr=MMAttribute("document","test\n----\n\n\nA Message",p)
       self.assertTrue(p is attr.get_owner())
       v = attr.get_value()

       attr.set_value("diff")
       self.assertTrue(p.Updated())
       v1 = attr.get_value()
       self.assertEquals("diff",str(v1))

def getTestNames():
    return [ 'attribTest.attribTest' ] 

if __name__ == '__main__':
    unittest.main()

