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

    def testCreate(self):
        myclass = type(self.store)
        self.store.NewCategory("Test")
        from MysteryMachine.store import CreateStore
        try:
            #This must create an empty store or raise an exception
            differentStore = CreateStore(self.store.getUri())
            self.assertEquals(list(differentStore.EnumCategories()),[])
        except:
            pass

    def testCategories(self):
        cats=list(self.store.EnumCategories())
        self.assertEqual(len(cats),0)
        self.store.NewCategory("One")
        self.store.NewCategory("Two")
        self.store.NewCategory(".Three")
        cats=list(self.store.EnumCategories())
        self.assertEqual(len(cats),2)
        self.store.DeleteCategory("One")
        cats=list(self.store.EnumCategories())
        self.assertEqual(len(cats),1)

    def testObjects(self):
        #Check empty categories are..
        self.store.NewCategory("One")
        self.store.NewCategory("Two")
        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(len(objs1),0)
        self.assertEqual(len(objs2),0)
        
        o11=self.store.NewObject("One")
        o12=self.store.NewObject("One")
        o21=self.store.NewObject("Two")

        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(len(objs1),2)
        self.assertEqual(len(objs2),1)
   
        #Recreate cateogory - should have no effect.
        self.store.NewCategory("Two")
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(len(objs2),1)
       
        #Test deletion 
        self.store.DeleteObject("One"+":"+o12)

        # - Commented out next 4 lines as currently we don't
        #   require this to work.
        ##Test deletion if an attribute is applied.
        ##Set an attribute.
        #attrtuple = ( "simple",{ "":"fred" }  )
        #self.store.SetAttribute("Two"+":"+o21+":name",*attrtuple)

        self.store.DeleteObject("Two"+":"+o21)

        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(len(objs1),1)
        self.assertEqual(len(objs2),0)

    #TODO Seperate out the bits which use the internal if.
    def testAttribute(self):
        #Create some cats and objs.
        self.store.NewCategory("One")
        self.store.NewCategory(".Two")

        o11=self.store.NewObject("One")
        o12=self.store.NewObject("One")
        o21=self.store.NewObject(".Two")

        #Set an attribute.
        attrtuple = ( "simple",{ "":"fred" }  )
        self.store.SetAttribute("One"+":"+o12+":name",*attrtuple)
    
        #Set an another attribute - with a leading dot!
        attrtupled = ( "simple",{ "":"tom cobbley" }  )
        self.store.SetAttribute("One"+":"+o12+":.dotfile",*attrtupled)

        #Set Attribute in a category
        self.store.SetAttribute("One"+":"+".dummyattr",*attrtuple)

        #Count attributes.
        objs1=list(self.store.EnumAttributes("One:"+o12))
        cat1=list(self.store.EnumAttributes("One"))
        objs2=list(self.store.EnumAttributes(".Two:"+o21))
        self.assertEqual(len(objs1),1)
        self.assertEqual(len(cat1),0)
        self.assertEqual(len(objs2),0)

        #Count objects to check that attributes aren't included
        objs1=list(self.store.EnumObjects("One"))
        self.assertEqual(len(objs1),2)      

       #Test presence
        self.assertTrue(self.store.HasAttribute("One:"+o12+":name"))
        self.assertTrue(self.store.HasAttribute("One:.dummyattr"))
        self.assertFalse(self.store.HasAttribute("One:.foo"))
        self.assertFalse(self.store.HasAttribute("One:"+o11+":name"))
        self.assertFalse(self.store.HasAttribute("One:"+o12+":notname"))

        #Retrieve attribute.
        self.assertEquals(self.store.GetAttribute("One:"+o12+":name"),attrtuple)
        self.assertEquals(self.store.GetAttribute("One:"+o12+":.dotfile"),attrtupled)
        self.assertEquals(self.store.GetAttribute("One:.dummyattr"),attrtuple)
        
        #Delete it.
        self.store.DelAttribute("One:"+o12+":name")
        self.store.DelAttribute("One:"+o12+":.dotfile")
        self.store.DelAttribute("One:.dummyattr")
 
        #Count attributes.
        objs1=list(self.store.EnumAttributes("One:"+o12))
        objs2=list(self.store.EnumAttributes(".Two:"+o21))
        cat1=list(self.store.EnumAttributes("One"))
        self.assertEqual(len(objs1),0)
        self.assertEqual(len(objs2),0)
        self.assertEqual(len(cat1),0)
        
        #Set an attribute - leave attribut set for SCM Interagtion tests
        attrtuple = ( "simple",{ "":"fred" }  )
        self.store.SetAttribute("One"+":"+o12+":name",*attrtuple)
        self.attrnames =  { "One:"+o12+":name": attrtuple }
           
        #Check that removed parts get removed from the store
        self.store.SetAttribute("One"+":"+o12+":overwrite", "test1", { 'first':"this should dissappear" })
        self.store.SetAttribute("One"+":"+o12+":overwrite", "test1", { 'second':"this should be all thats left"})
        self.assertEquals(len(self.store.GetAttribute("One:"+o12+":overwrite")[1]),1)

        self.store.SetAttribute("One"+":"+o12+":overwrite", "test2", { 'third':"this should be all thats left"})
        self.assertEquals(self.store.GetAttribute("One:"+o12+":overwrite")[0],"test2")
        self.assertEquals(len(self.store.GetAttribute("One:"+o12+":overwrite")[1]),1)
     
    def testProxyObjAttr(self):
        """
        Test the Object proxy used in MMObjects.
        
        this prolly requires an overridable method to get the obj to
        start with  
        """
        #Create some cats and objs.
        self.store.NewCategory("One")
        self.store.NewCategory("Two")
        o11=self.store.NewObject("One")
        o12=self.store.NewObject("One")
        o21=self.store.NewObject("Two")
    
        o12store = self.store.GetObjStore("One:"+o12)
        o21store = self.store.GetObjStore("Two:"+o21)

        #Set an attribute.
        attrtuple = ( "simple",{ "":"fred" })
        o12store.SetAttribute("name",*attrtuple)

        #Count attributes.
        objs1=list(o12store.EnumAttributes())
        objs2=list(o21store.EnumAttributes())
        self.assertEqual(len(objs1),1)
        self.assertEqual(len(objs2),0)
        
        #Test presence
        self.assertTrue(o12store.HasAttribute("name"))
        self.assertFalse(o21store.HasAttribute("name"))
        self.assertFalse(o12store.HasAttribute("notname"))

        #Retrieve attribute.
        self.assertEquals(o12store.GetAttribute("name"),attrtuple)
        
        #Delete it.
        o12store.DelAttribute("name")
 
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
                self.assertEquals(self.store.GetAttribute(k),v)
