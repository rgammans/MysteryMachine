#!/usr/bin/env python
#   			mmsystemTest.py - Copyright Roger Gammans
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
Tests for the MysteryMachine MMSystem  module
"""

from MysteryMachine import * 
from MysteryMachine.schema.MMSystem import *

import MysteryMachine.store.dict_store

import unittest
import itertools

class sysTests(unittest.TestCase):
    def setUp(self):
        self.appctx = StartApp(["--cfgengine=ConfigYaml", "--logtarget=logging.StreamHandler", "--cfgfile=tests/test.yaml", "--testmode"]) 
        self.sys=MMSystem.Create("dict:test")

    def testCategory(self):
        cats=list(self.sys.EnumCategories())
        self.assertEqual(len(cats),0)
        self.sys.NewCategory("One",None)
        self.sys.NewCategory("Two",None)
        cats=list(self.sys.EnumCategories())
        self.assertEqual(len(cats),2)
        self.sys.DeleteCategory("One")
        cats=list(self.sys.EnumCategories())
        self.assertEqual(len(cats),1)

    def testCatObject(self):
        self.sys.NewCategory("One",None)
        self.sys.NewCategory("Two",None)
        self.assertEqual(type(self.sys["One"]),MMCategory)
        cat = self.sys["One"]
        def setObj(cat):
            cat["obj"] = ""
        self.assertRaises(LookupError,setObj,cat) 
        cat[".dummy"] = "data"
        self.assertEqual(type(cat[".dummy"]) , MMAttribute)
        self.assertEqual(str(cat[".dummy"]),"data")
        o12=self.sys.NewObject("One",None)
        o12id = repr(o12).split(":")[-1]
        self.assertEquals(cat[o12id],o12)
        del cat[".dummy"]
        self.assertRaises(KeyError,cat.__getitem__,".dummy")
        self.assertRaises(KeyError,self.sys["One"].__getitem__,".dummy")

        objs=list(cat.__iter__())
        self.assertEqual(len(objs),1)
        objkeys=list(cat.iterkeys())
        self.assertEqual(len(objkeys),1)
        for k,v in itertools.izip(objkeys,objs):
            self.assertEquals(cat[k],v)




        del cat[o12id]
        self.assertRaises(KeyError,cat.__getitem__,o12id)
        self.assertRaises(KeyError,self.sys["One"].__getitem__,o12id)
        self.assertRaises(KeyError,self.sys.get_object,"One",o12id)
        self.assertEquals(cat.get_root(),self.sys)
        
        #Cat object name.
        self.assertEquals(str(cat),"one")
        self.assertEquals(repr(cat),"one")
        cat[".defname"] = "Test"
        self.assertEquals(repr(cat),"one")
        self.assertEquals(str(cat),"Test")

    def testObjects(self):
        #Check empty categories are..
        self.sys.NewCategory("One",None)
        self.sys.NewCategory("Two",None)
        objs1=list(self.sys.EnumObjects("One"))
        objs2=list(self.sys.EnumObjects("Two"))
        self.assertEqual(len(objs1),0)
        self.assertEqual(len(objs2),0)
        
        o11=self.sys.NewObject("One",None)
        o12=self.sys.NewObject("One",None)
        o21=self.sys.NewObject("Two",None)
  
        #Check instance behaviour
        self.assertTrue(isinstance(o11,MMObject))
        self.assertTrue(self.sys.get_object("One",repr(o12).split(":")[1]) is o12)
        self.assertFalse(self.sys.get_object("One",repr(o12).split(":")[1]) is o11)
      
        objs1=list(self.sys.EnumObjects("One"))
        objs2=list(self.sys.EnumObjects("Two"))
        objs2a=list(self.sys.EnumObjects("TWo"))
        self.assertEqual(len(objs1),2)
        self.assertEqual(len(objs2),1)
        self.assertEqual(len(objs2a),1)

        allobjs = list(self.sys.EnumContents())
        self.assertEqual(len(allobjs),3)
        self.assertEquals(len(list(iter(self.sys))),3)
        for o in allobjs:
            self.assertNotEquals(type(self.sys[o]),type(None))
        
   
        self.sys.DeleteObject(repr(o12))
        del self.sys[repr(o21)]

        objs1=list(self.sys.EnumObjects("One"))
        objs2=list(self.sys.EnumObjects("Two"))
        self.assertEqual(len(objs1),1)
        self.assertEqual(len(objs2),0)
   
        o21=self.sys.NewObject("Two",None)
    
        names = list(self.sys.EnumContents()) 
        fndNames= []
        for k,v in self.sys.iteritems():
            self.assertTrue(k in names)
            self.assertFalse(k in fndNames)
            fndNames += [ k ]
            self.assertTrue(isinstance( v, MMObject))
            self.assertEquals(v,self.sys[k])  

        objs=list(self.sys.__iter__())
        self.assertEqual(len(objs),2)
        objkeys=list(self.sys.iterkeys())
        self.assertEqual(len(objkeys),2)
        for k,v in itertools.izip(objkeys,objs):
            self.assertEquals(self.sys[k],v)

        cat = self.sys["one"]
        objs=list(cat.__iter__())
        self.assertEqual(len(objs),1)
        objkeys=list(cat.iterkeys())
        self.assertEqual(len(objkeys),1)
        for k,v in itertools.izip(objkeys,objs):
            self.assertEqual(cat[k],v)


        #Test parent.
        self.assertEquals(o11.get_parent(),None)
        cat[".parent"] = o21
        self.assertEquals(cat.get_parent(),o21)

        o12=self.sys.NewObject("One")
        cat.set_parent(o12)
        self.assertEquals(cat.get_parent(),o12)
        #Check we can't create objects which are their own parents.
        self.assertEquals(o12.get_parent(),o21)
 
        o12["attr"] = "text"
        self.assertRaises(Error.InvalidParent,cat.set_parent,o12["attr"])



    def testLoaded(self):

        # __init__ del calls them ok.
        # Test open / create semanitcs.
        self.assertEquals(UnEscapeSystemUri(EscapeSystemUri("dict:test")),"dict:test")
        self.assertEquals(EscapeSystemUri("dict:test"),str(self.sys))
        self.assertTrue(GetLoadedSystemByName(str(self.sys)) is self.sys)
      
     

    def testEncoding(self):
        #Check default encoding
        self.assertEquals(self.sys.get_encoding(),"ascii" )
        #Set and readback encoding
        self.sys.set_encoding("utf-8")
        self.assertEquals(self.sys.get_encoding(),"utf-8" )
        #Black box test - to enusre we get fetch in from the store
        self.assertEquals(self.sys._get_encoding(),"utf-8" )
        self.assertRaises(LookupError,self.sys.set_encoding,"xyyzzy")


    def testNaming(self):
        self.assertEquals(repr(self.sys),str(self.sys))
        rname=repr(self.sys)
        testname= u"A test name"
        self.sys.set_name(testname)
        self.assertEquals(self.sys.get_name(),testname)
        self.assertEquals(str(self.sys),testname)
        self.assertEquals(repr(self.sys),rname)
        self.assertEquals(str(self.sys[".defname"]),testname)


    def testNotify(self):
       def testexpected_cats(obj):
            self.exception = None
            try:
                attr = list( obj.EnumCategories())
                for k in self.cats:
                    self.assertTrue(k in attr,"%s not in categories"%k)
            except Exception, e:
                self.exception =e

       def update(obj):
            update.count+=1
       update.count = 0
       lastcount = update.count

       cats=list(self.sys.EnumCategories())
       self.assertEqual(len(cats),0)
       self.sys.register_notify(update)
       self.sys.register_notify(testexpected_cats)
       self.cats = ["one","two"]
       self.sys.NewCategory("one",None)
       self.sys.NewCategory("two",None)
       self.assertTrue(update.count > lastcount, "Update not detected")
       if self.exception: raise self.exception
       lastcount = update.count
       #Notify are guaranteed to be preserved if we don't keep
       # reference to the schema node. So lets inc it refcount.
       c=self.sys["one"]  
       self.sys["one"].register_notify(update)
       o11=self.sys.NewObject("One")
       self.assertTrue(update.count > lastcount, "Update not detected")
       lastcount = update.count

       o21=self.sys.NewObject("Two")
       self.assertEqual(update.count , lastcount, "Update  detected")


def getTestNames():
    	return [ 'mmsystemTest.sysTests' ] 

if __name__ == '__main__':
    unittest.main()
    

