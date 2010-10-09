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
from MysteryMachine import StartApp 
import unittest

from types import NoneType

class DummyPart(object):
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


class container(MMAttributeContainer):
    def __init__(self,*args,**kwargs):
        super(MMAttributeContainer,self).__init__(*args,**kwargs)
        self.parent = kwargs.get('parent',None)
        self.items  = { }
    def __getitem__(self,i):
        if i not in self.cache: 
            if self.parent:
                pattr = self.parent[i]
                return  MMAttribute(i,ShadowAttributeValue(self,attrname=i,object=self),
                                self,copy = False) 
            else: raise KeyError(i)
        return self._get_item(i,NoneType)
    def __setitem__(self,k,v):
        self.items[k] = self._set_item(k,v)
        return self.items[k]

    def __delitem__(self,i):
        del self.items[i]
        return self._invaldate_item(i)

    def __iter__(self):
        for k in self.cache.keys():
            yield k
    def get_parent(self):
        return self.parent

class attribTest(unittest.TestCase):
    def setUp(self):
        StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"])    
 
    def testCreate(self):
       attr=MMAttribute("document","test\n----\n\n\nA Message",None)
       #sys.stderr.write(str(attr.get_raw_rst))
       self.assertEqual(attr.get_raw_rst(),"test\n----\n\n\nA Message")
       attr2 =MMAttribute("otherdoc",attr.get_value(),None)
       self.assertEqual(attr.get_value(),attr2.get_value())
       self.assertFalse(attr.get_value() is attr2.get_value())
       attr3 =MMAttribute("otherdoc",attr.get_value(),None ,copy = False)
       self.assertEqual(attr.get_value(),attr3.get_value())
       self.assertTrue(attr.get_value() is attr3.get_value())
 

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

    def testAttribContainer(self):
        m = container()
        #Keep the attrib around so it stays in the cache.
        a = m._set_item("name","str")
        self.assertEquals(type( a ) , MMAttribute )
        self.assertEquals(type( m._get_item("name",DummyPart,"Crap")) , MMAttribute )
        self.assertEquals(str(a),"str")
        self.assertEquals( m._get_item("name",DummyPart,"Crap") , a )
        b = m._set_item("name","no string")
        self.assertEquals(a,b)
        c = m._set_item("notname","foo")
        self.assertNotEquals(b,c)
        b = m._set_item("name",c)
        self.assertEquals(str(a),"foo")
    
    def testInheritance(self):
        parentobj = container()
        childobj  = container(parent = parentobj )

        parentobj["foo"] = "test"
        self.assertEquals(parentobj["foo"].get_raw(),"test")
        self.assertEquals(childobj["foo"].get_raw(),"test")
        
        childobj["foo"] = "different"
        self.assertEquals(parentobj["foo"].get_raw(),"test")
        self.assertEquals(childobj["foo"].get_raw(),"different")
        
 
def getTestNames():
    return [ 'attribTest.attribTest' ] 

if __name__ == '__main__':
    unittest.main()

