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

from mock.schema_top import *


class DummyPart(object):
    def __init__(self,x):
        self.x=x
    def get_value(self):
        return self.x

class container(MMAttributeContainer):
    def __init__(self,*args,**kwargs):
        super(MMAttributeContainer,self).__init__(*args,**kwargs)
        self.parent = kwargs.get('parent',None)
        self.items  = { }
        self.store = mock_store()
        self.tm = TransactionManager(mock_lockman(),self.store)
        self.owner = None

    def get_nodeid(self,): return ""
    def get_root(self,):
        return self

    def get_encoding(self):
        return "ascii"

    def __getitem__(self,i):
        if i not in self.cache: 
            if self.parent:
                pattr = self.parent[i]
                return  MMAttribute(i,ShadowAttributeValue(self,attrname=i,object=self),
                                self,copy = False) 
            else: raise KeyError(i)
        return self._get_item(i,NoneType)
    def __setitem__(self,k,v):
        self.items[k] = self._set_attr_item(k,v)
        return self.items[k]

    def __delitem__(self,i):
        try:
            del self.items[i]
        except KeyError: pass
        self._invalidate_item(i)

    def __iter__(self):
        for k in self.cache.keys():
            yield k
    def get_parent(self):
        return self.parent

    def get_tm(self,):
        return self.tm 


class attribTest(unittest.TestCase):
    def setUp(self):
        self.ctx = StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"])    
      
    def tearDown(self,):
        self.ctx.close()
 
    def testCreate(self):
       p = fakeParent()
       attr=MMAttribute("document","test\n----\n\n\nA Message",p)
       #sys.stderr.write(unicode(attr.get_raw_rst))
       self.assertEqual(attr.get_raw_rst(),"test\n----\n\n\nA Message")
       attr2 =MMAttribute("otherdoc",attr.get_value(),p)
       self.assertEqual(attr.get_value(),attr2.get_value())
       self.assertFalse(attr.get_value() is attr2.get_value())
       attr3 =MMAttribute("otherdoc",attr.get_value(),p ,copy = False)
       self.assertEqual(attr.get_value(),attr3.get_value())
       self.assertTrue(attr.get_value() is attr3.get_value())
 

    # TODO
    # Test MMObject fetching
    # Test handling of parse errors.
    # Test AttributeValue export resolution.
    def testAttrValExport(self):
       attr=MMAttribute("document","test\n----\n\n\nA Message",None)
       self.assertEqual("test\n----\n\n\nA Message",attr.get_raw())

    def testAttrValType(self):
       p = fakeParent()
       attr=MMAttribute("document","test\n----\n\n\nA Message",p)
       self.assertEqual(attr.get_type(),"simple")


#  XXX Commented out as I don't believe this test 
#      makes sense since we've added transactions. 
#     as Attribute no handle saving themselves to the store
#    and don't rely on the owners (or parents in the old nomenclature)
#
#    I've left this code to jog memories in case I'm wrong.
#
#    def testAttrParentStuff(self):
#       p = fakeParent()
#       attr=MMAttribute("document","test\n----\n\n\nA Message",p)
#
#       attr.set_value("diff")
#       self.assertTrue(p.Updated())
#       v1 = attr.get_value()
#       self.assertEqual("diff",unicode(v1))


    def testNotify(self):
       def testexpect(obj):
            self.exception = None
            try:
                self.assertEqual(unicode(obj) , self.val)
            except Exception as e:
                self.exception =e


       def update(obj):
            update.count+=1
       update.count = 0

       p = fakeParent()
       attr=MMAttribute("document","test\n----\n\n\nA Message",p)
       attr.register_notify(update)
       attr.register_notify(testexpect)
       self.assertEqual(update.count,0)

       self.val = "diff"
       attr.set_value(self.val)
       self.assertEqual(update.count,1)
       if self.exception: raise self.exception

       self.val = "diff"
       attr.unregister_notify(update)
       self.val ="baz" 
       attr.set_value(self.val)
       self.assertEqual(update.count,1)
       if self.exception: raise self.exception

    def testAttribContainer(self):
        m = container()
        #Keep the attrib around so it stays in the cache.
        a = m._set_attr_item("name","str")
        self.assertEqual(type( a ) , MMAttribute )
        self.assertEqual(type( m._get_item("name",DummyPart,"Crap")) , MMAttribute )
        self.assertEqual(unicode(a),"str")
        self.assertEqual( m._get_item("name",DummyPart,"Crap") , a )
        b = m._set_attr_item("name","no string")
        self.assertEqual(a,b)
        c = m._set_attr_item("notname","foo")
        self.assertNotEquals(b,c)
        b = m._set_attr_item("name",c)
        self.assertEqual(unicode(a),"foo")
    
    def testInheritance(self):
        parentobj = container()
        childobj  = container(parent = parentobj )

        parentobj["foo"] = "test"
        self.assertEqual(parentobj["foo"].get_raw(),"test")
        self.assertEqual(childobj["foo"].get_raw(),"test")
        
        childobj["foo"] = "different"
        self.assertEqual(parentobj["foo"].get_raw(),"test")
        self.assertEqual(childobj["foo"].get_raw(),"different")
        
    def testEncoding(self):
        m = container()
        m["encoded"] = "String"
        self.assertRaises(UnicodeDecodeError,m._set_attr_item,"fake","Not ascii\xa5")
        self.assertEqual(unicode(m["encoded"]),"String")
        self.assertRaises(KeyError,m.__getitem__,"fake")
        self.assertEqual(unicode(m["encoded"]),"String")

    def testUnstorableCreate(self):
       m = container()
       attr=MMUnstorableAttribute("document","test\n----\n\n\nA Message",m)
       self.assertRaises(KeyError,m.__getitem__,"document")
       #sys.stderr.write(unicode(attr.get_raw_rst))
       self.assertEqual(attr.get_raw_rst(),"test\n----\n\n\nA Message")
       attr2 =MMUnstorableAttribute("otherdoc",attr.get_value(),m)
       self.assertRaises(KeyError,m.__getitem__,"otherdoc")
       self.assertEqual(attr.get_value(),attr2.get_value())
       self.assertFalse(attr.get_value() is attr2.get_value())
       attr3 =MMUnstorableAttribute("otherdoc",attr.get_value(),m ,copy = False)
       self.assertRaises(KeyError,m.__getitem__,"otherdoc")
       self.assertEqual(attr.get_value(),attr3.get_value())
       self.assertTrue(attr.get_value() is attr3.get_value())
 

    def testUnstoredAttribContainer(self):
        obj = container()
        #Create a string attribute and check it doesn't get written back
        # but can be evaluated.
        a = MMUnstorableAttribute("name","str",obj)
        self.assertRaises(KeyError,obj.__getitem__,"name" )
        self.assertEqual(unicode(a),"str")
        

        #Check set_value changes our attribute without modify it's claimed container.
        a.set_value("a different string")
        self.assertRaises(KeyError,obj.__getitem__,"name" )
        self.assertEqual(unicode(a),"a different string")


def getTestNames():
    return [ 'attribTest.attribTest' ] 

if __name__ == '__main__':
    unittest.main()

