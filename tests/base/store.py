#!/usr/bin/env python
#   			storeTest.py - Copyright Roger Gammans
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
Tests for the MysteryMachine dictstore  module
"""

from MysteryMachine import * 
from MysteryMachine.Exceptions import * 

import sys

def listHelper(seq):
    result = []
    for i in seq:
        result.append(i)
    return result

class storeTests(object):
    """
    These test are intended to be generic store tests so that this test suite
    can be updated to help form a basic test suite for MysteryMachine store modules
    """
    def setUp(self):  
        self.mySetUp()

    def myTearDown(self,): pass

    def tearDown(self,):
        self.myTearDown()
        self.store.lock()
        self.store.close()

    def testCreate(self):
        myclass = type(self.store)
        self.store.start_store_transaction()
        self.store.NewCategory("Test")
        self.store.commit_store_transaction()
        from MysteryMachine.store import CreateStore
        try:
            #This must create an empty store or raise an exception
            differentStore = CreateStore(self.store.getUri())
            self.assertEqual(list(differentStore.EnumCategories()),[])
        except Exception:
            pass

    def testCategories(self):
        cats=list(self.store.EnumCategories())
        self.assertEqual(len(cats),0)
        self.store.start_store_transaction()
        self.store.NewCategory("One")
        self.store.NewCategory("Two")
        self.store.NewCategory(".Three")
        self.store.commit_store_transaction()
        cats=list(self.store.EnumCategories())
        self.assertEqual(set(cats),set(['One','Two','.Three'] ))

        self.store.start_store_transaction()
        self.store.DeleteCategory("One")
        self.store.commit_store_transaction()
        cats=list(self.store.EnumCategories())
        self.assertEqual(set(cats), set(['Two','.Three'] ))

        #Create and delete in the same txn.
        self.store.start_store_transaction()
        self.store.NewCategory("Four")
        self.store.DeleteCategory("Four")
        self.store.commit_store_transaction()
        self.assertEqual(set(cats),set(['Two','.Three'] ))
        self.assertFalse(self.store.HasCategory("Four"))

        if False:
            #This behaviour is currently undefined, but below
            # is a test snippet for a some error handling
            # which I might not be part of the store spec.

            # Ideally I'd like schema to guarantee never
            # to generate call tracess like the below.
 
            self.store.start_store_transaction()
            self.store.NewCategory("Four")
            self.store.commit_store_transaction()
 
            self.store.start_store_transaction()
            self.store.DeleteCategory("Four")
            self.assertRaises(Exception,self.store.DeleteCategory,"Four")
            self.store.abort_store_transaction()


    def testObjects(self):
        #Check empty categories are..
        self.store.start_store_transaction()
        self.store.NewCategory("One")
        self.store.NewCategory("Two")
        self.store.commit_store_transaction()
        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(len(objs1),0)
        self.assertEqual(len(objs2),0)
        
        self.store.start_store_transaction()
        self.store.NewObject("One:1")
        self.store.NewObject("One:2")
        self.store.NewObject("Two:1")

        o11,o12, o21 ="1", "2", "1"

        self.store.commit_store_transaction()
        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(set(objs1),set([o11,o12]))
        self.assertEqual(set(objs2),set([o21]))
   
        #Recreate cateogory - should have no effect.
        self.store.start_store_transaction()
        self.store.NewCategory("Two")
        self.store.commit_store_transaction()
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(set(objs2),set([o21]))
       
        #Test deletion 
        self.store.start_store_transaction()
        self.store.DeleteObject("One"+":"+o12)

        # - Commented out next 4 lines as currently we don't
        #   require this to work.
        ##Test deletion if an attribute is applied.
        ##Set an attribute.
        #attrtuple = ( "simple",{ "a":"fred" }  )
        #self.store.SetAttribute("Two"+":"+o21+":name",*attrtuple)

        self.store.DeleteObject("Two"+":"+o21)

        self.store.commit_store_transaction()
        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(set(objs1),set([o11]))
        self.assertEqual(len(objs2),0)

        #Create and delete in the same txn.
        self.store.start_store_transaction()
        o2 = "3" 
        self.store.NewObject("Two:" + o2)
        self.store.DeleteObject("Two:" + o2 )
        self.store.commit_store_transaction()
        self.assertEqual(len(list(self.store.EnumObjects("Two"))),0)
        self.assertFalse(self.store.HasObject("Two:"+o2)) 

    #TODO Seperate out the bits which use the internal if.
    def testAttribute(self):
        #Create some cats and objs.
        self.store.start_store_transaction()
        self.store.NewCategory("One")
        self.store.NewCategory(".Two")

        self.store.NewObject("One:1")
        self.store.NewObject("One:2")
        self.store.NewObject(".Two:1")

        o11,o12, o21 ="1", "2", "1"

        #Set an attribute.
        attrtuple = ( "simple",{ "a":"fred" }  )
        self.store.SetAttribute("One"+":"+o12+":name",*attrtuple)
    
        #Set an another attribute - with a leading dot!
        attrtupled = ( "simple",{ "a":"tom cobbley" }  )
        self.store.SetAttribute("One"+":"+o12+":.dotfile",*attrtupled)

        #Set Attribute in a category
        self.store.SetAttribute("One"+":"+".dummyattr",*attrtuple)

        self.store.commit_store_transaction()

        #Count attributes.
        objs1=list(self.store.EnumAttributes("One:"+o12))
        cat1=list(self.store.EnumAttributes("One"))
        objs2=list(self.store.EnumAttributes(".Two:"+o21))
        ##Cast to set as order is not part of the API.
        self.assertEqual(set(objs1),set(['name', '.dotfile']))
        self.assertEqual(set(cat1),set(['.dummyattr']))
        self.assertEqual(len(objs2),0)

        #Count objects to check that attributes aren't included
        objs1=list(self.store.EnumObjects("One"))
        self.assertEqual(set(objs1),set([ o11,o12])) 

       #Test presence
        self.assertTrue(self.store.HasAttribute("One:"+o12+":name"))
        self.assertTrue(self.store.HasAttribute("One:.dummyattr"))
        self.assertFalse(self.store.HasAttribute("One:.foo"))
        self.assertFalse(self.store.HasAttribute("One:"+o11+":name"))
        self.assertFalse(self.store.HasAttribute("One:"+o12+":notname"))

        #Retrieve attribute.
        self.assertEqual(self.store.GetAttribute("One:"+o12+":name"),attrtuple)
        self.assertEqual(self.store.GetAttribute("One:"+o12+":.dotfile"),attrtupled)
        self.assertEqual(self.store.GetAttribute("One:.dummyattr"),attrtuple)
        
        #Delete it.
        self.store.start_store_transaction()
        self.store.DelAttribute("One:"+o12+":name")
        self.store.DelAttribute("One:"+o12+":.dotfile")
        self.store.DelAttribute("One:.dummyattr")
        self.store.commit_store_transaction()
 
        #Count attributes.
        objs1=list(self.store.EnumAttributes("One:"+o12))
        objs2=list(self.store.EnumAttributes(".Two:"+o21))
        cat1=list(self.store.EnumAttributes("One"))
        self.assertEqual(len(objs1),0)
        self.assertEqual(len(objs2),0)
        self.assertEqual(len(cat1),0)
        
        #Set an attribute - leave attribut set for SCM Interagtion tests
        self.store.start_store_transaction()
        attrtuple = ( "simple",{ "a":"fred" }  )
        self.store.SetAttribute("One"+":"+o12+":name",*attrtuple)
        self.attrnames =  { "One:"+o12+":name": attrtuple }
           
        #Check that removed parts get removed from the store
        self.store.SetAttribute("One"+":"+o12+":overwrite", "test1", { 'first':"this should dissappear" })
        self.store.SetAttribute("One"+":"+o12+":overwrite", "test1", { 'second':"this should be all thats left"})
        self.store.commit_store_transaction()

        self.assertEqual(len(self.store.GetAttribute("One:"+o12+":overwrite")[1]),1)

        #Test again in a seperate txn
        self.store.start_store_transaction()
        self.store.SetAttribute("One"+":"+o12+":overwrite", "test2", { 'third':"this should be all thats left"})
        self.store.commit_store_transaction()

        self.assertEqual(self.store.GetAttribute("One:"+o12+":overwrite")[0],"test2")
        self.assertEqual(len(self.store.GetAttribute("One:"+o12+":overwrite")[1]),1)
    
        ##Check that type not realted to a string raise an Api Violation.
        self.assertRaises(StoreApiViolation,self.store.SetAttribute,"One:"+o12+":broked", "test3", {'integer':1})
 
    def testProxyObjAttr(self):
        """
        Test the Object proxy used in MMObjects.
        
        this prolly requires an overridable method to get the obj to
        start with  
        """
        #Create some cats and objs.
        self.store.start_store_transaction()
        self.store.NewCategory("One")
        self.store.NewCategory("Two")
        self.store.NewObject("One:1")
        self.store.NewObject("One:2")
        self.store.NewObject("Two:1")

        o11,o12, o21 ="1", "2", "1"
    
        o12store = self.store.GetObjStore("One:"+o12)
        o21store = self.store.GetObjStore("Two:"+o21)

        #Set an attribute.
        attrtuple = ( "simple",{ "a":"fred" })
        o12store.SetAttribute("name",*attrtuple)
        self.store.commit_store_transaction()

        #Count attributes.
        objs1=list(o12store.EnumAttributes())
        objs2=list(o21store.EnumAttributes())
        self.assertEqual(set(objs1) , set(['name']))
        self.assertEqual(len(objs2),0)
        
        #Test presence
        self.assertTrue(o12store.HasAttribute("name"))
        self.assertFalse(o21store.HasAttribute("name"))
        self.assertFalse(o12store.HasAttribute("notname"))

        #Retrieve attribute.
        self.assertEqual(o12store.GetAttribute("name"),attrtuple)
        
        #Delete it.
        self.store.start_store_transaction()
        o12store.DelAttribute("name")
        self.store.commit_store_transaction()
 
        #Count attributes.
        objs1=list(o12store.EnumAttributes())
        objs2=list(o21store.EnumAttributes())
        self.assertEqual(len(objs1),0)
        self.assertEqual(len(objs2),0)

    def testSCMIntegration(self):
        #Repeat a previous setup.
        if self.has_scm:
            self.testAttribute()
            self.store.commit("First")
            self.doCleanTst()
            self.store.revert(self.store.getChangeLog().next())
            for k,v in self.attrnames.iteritems():
                self.assertEqual(self.store.GetAttribute(k),v)


    def test_should_be_able_tell_the_difference_between_objects_categories_and_attribs(self):
        #Check empty categories are..
        self.store.start_store_transaction()
        self.store.NewCategory("One")
        self.store.NewCategory("Two")
        self.store.NewCategory("Two:Three")
        attrtuple = ( "simple",{ "a":"fred" }  )
        self.store.SetAttribute("Five",*attrtuple)
        self.store.commit_store_transaction()

        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(len(objs1),0)
        self.assertEqual(len(objs2),0)
        
        self.store.start_store_transaction()
        self.store.NewObject("One:1")
        self.store.NewObject("One:2")
        self.store.NewObject("Two:1")

        o11,o12, o21 ="1", "2", "1"
        self.store.commit_store_transaction()
        
        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(set(objs1),set([o11,o12]))
        self.assertEqual(set(objs2),set(o21))
  
        self.assertTrue(self.store.HasCategory("One"))
        self.assertTrue(self.store.HasCategory("Two"))
        self.assertTrue(self.store.HasCategory("Two:Three"))
        self.assertFalse(self.store.HasObject("Two:Three"))
        self.assertFalse(self.store.HasCategory("Five"))
        self.assertFalse(self.store.HasObject("Five"))
        self.assertTrue(self.store.HasAttribute("Five"))
        self.assertFalse(self.store.HasObject("One"))
        self.assertFalse(self.store.HasAttribute("One"))

        #Recreate cateogory - should have no effect.
        self.store.start_store_transaction()
        self.store.NewCategory("Two")
        self.store.commit_store_transaction()
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(set(objs2),set([o21]))
       
        #Test deletion 
        self.store.start_store_transaction()
        self.store.DeleteObject("One"+":"+o12)

        # - Commented out next 4 lines as currently we don't
        #   require this to work.
        ##Test deletion if an attriibute is applied.
        ##Set an attribute.
        attrtuple = ( "simple",{ "a":"fred" }  )
        #self.store.SetAttribute("Two"+":"+o21+":name",*attrtuple)

    
        self.store.DeleteObject("Two"+":"+o21)
        self.store.commit_store_transaction()
        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(set(objs1),set([o11]))
        self.assertEqual(len(objs2),0)

    def test_rollback(self,):   
        if self.store.supports_txn:
            
                self.store.start_store_transaction()
                self.store.NewCategory("One")
                self.store.NewCategory("Two")
                self.store.NewCategory("Two:Three")
                attrtuple = ( "simple",{ "a":"fred" }  )
                self.store.SetAttribute("Five",*attrtuple)
                self.store.commit_store_transaction()

                objs1=list(self.store.EnumObjects("One"))
                objs2=list(self.store.EnumObjects("Two"))
                self.assertEqual(len(objs1),0)
                self.assertEqual(len(objs2),0)
                
                self.store.start_store_transaction()
                self.store.NewObject("One:1")
                self.store.NewObject("One:2")
                self.store.NewObject("Two:1")

                o11,o12, o21 ="1", "2", "1"
                self.store.abort_store_transaction()
 
                objs1=list(self.store.EnumObjects("One"))
                objs2=list(self.store.EnumObjects("Two"))
                self.assertEqual(len(objs1),0)
                self.assertEqual(len(objs2),0)
                               
                self.store.start_store_transaction()
                self.store.NewObject("One:10")
                self.store.NewObject("One:20")
                self.store.NewObject("Two:10")

                o11,o12, o21 ="10", "20", "10" 
                self.store.commit_store_transaction()
                
                objs1=list(self.store.EnumObjects("One"))
                objs2=list(self.store.EnumObjects("Two"))
                self.assertEqual(set(objs1),set([o11,o12]))
                self.assertEqual(set(objs2),set([o21]))
