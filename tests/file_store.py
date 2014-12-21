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
from MysteryMachine.store.file_store import *

import unittest
from base.store import storeTests

import tempfile 
import shutil

class DummySystemClass:
    def getSelf(self):
        return self

DummySystem=DummySystemClass()

class filestoreTests(storeTests,unittest.TestCase):
    def mySetUp(self):
        self.ctx = StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"])
        self.mpath = tempfile.mkdtemp(prefix="mysmac")
        self.store=filestore("attrfile:"+self.mpath,create = False)
        self.store.set_owner(DummySystem)
        self.has_scm = False
    
    def tearDown(self):
        self.store.close()
        shutil.rmtree(self.mpath)
        if os.path.exists(self.mpath):
            os.rmdir(self.mpath)

    def testCanonicalise(self):
        import os
        self.assertEqual(self.store.GetCanonicalUri("."),os.path.normcase(os.getcwd()))
        try:
            import posix
            #Skip test on non posix OS.
            self.assertEqual(self.store.GetCanonicalUri("~"),os.getenv("HOME"))
        except ImportError:
            pass
        path= tempfile.mkdtemp()
        print "path,",path
        symname = tempfile.NamedTemporaryFile()
        symname = symname.name
        print "symname",symname
        try:
            os.remove(symname)
        except OSError:
            pass
        try:
            os.symlink(path,symname)
        except AttributeError: pass #Ignore system where os doesn't provide symlink
        else:
            parentpath = os.path.realpath(path+os.sep+"..")
            self.assertEqual(self.store.GetCanonicalUri(symname),path)
            self.assertEqual(self.store.GetCanonicalUri(symname + os.sep + ".."),parentpath)
            newpath  = path+os.path.sep+"test"
            os.mkdir(newpath)
            self.assertEqual(self.store.GetCanonicalUri(symname + os.sep + "test"),newpath)
            self.assertEqual(self.store.GetCanonicalUri(symname + os.sep + "test" + os.sep + ".."),path)
            self.assertEqual(self.store.GetCanonicalUri(symname + os.sep + ".." + os.sep + "test" + os.sep + ".."),parentpath)

        try:
            os.remove(symname)
        except OSError:
            pass

        shutil.rmtree(path)
        if os.path.exists(path):
            os.rmdir(path)
 
    def test_should_tell_the_difference_between_categories_and_random_dirs(self):
        cats=list(self.store.EnumCategories())
        self.assertEqual(len(cats),0)
        self.store.start_store_transaction()
        self.store.NewCategory("One")
        self.store.NewCategory("Two")
        self.store.NewCategory(".Three")
        self.store.commit_store_transaction()
        cats=list(self.store.EnumCategories())
        os.mkdir(os.path.expanduser(self.mpath) + os.path.sep + "Four")
        self.assertEqual(set(cats),set(['One','Two', '.Three']))
        self.store.start_store_transaction()
        self.store.DeleteCategory("One")
        self.store.commit_store_transaction()
        cats=list(self.store.EnumCategories())
        self.assertEqual(set(cats),set(['Two', '.Three']))
 
    def test_should_be_able_tell_the_difference_between_objects_categories_and_random_dirs(self):
        #Check empty categories are..
        self.store.start_store_transaction()
        self.store.NewCategory("One")
        self.store.NewCategory("Two")
        self.store.NewCategory("Two:Three")
        self.store.commit_store_transaction()
        os.mkdir(os.path.expanduser(self.mpath) + os.path.sep + "Four")
        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(len(objs1),0)
        self.assertEqual(len(objs2),0)
        
        self.store.start_store_transaction()
        self.store.NewObject("One:1")
        self.store.NewObject("One:2")
        self.store.NewObject("Two:1")
        o11="1"
        o12="2"
        o21="1"
        os.mkdir(os.path.join(os.path.expanduser(self.mpath),"One","FakeObject"))
        self.store.commit_store_transaction()

        objs1=list(self.store.EnumObjects("One"))
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(len(objs1),2)
        self.assertEqual(len(objs2),1)
   
        #Recreate cateogory - should have no effect.
        self.store.start_store_transaction()
        self.store.NewCategory("Two")
        self.store.commit_store_transaction()
        objs2=list(self.store.EnumObjects("Two"))
        self.assertEqual(len(objs2),1)
       
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
        self.assertEqual(len(objs1),1)
        self.assertEqual(len(objs2),0)



class test2(filestoreTests):
    """Try the filestore tests in a non-temporayr directory in case it behaves differently,
       and that posix symbols like '~' are handled.
    """
    def mySetUp(self):
        StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"])
        prefix = ""
        self.tmpexists = True
        try:
            import posix
            #Under possix try the same thing in a home dir.
            prefix = "~" 
        except ImportError:
            pass
        self.mpath = tempfile.mkdtemp(prefix="mysmac")
        os.rmdir(self.mpath)
        self.mpath = prefix + self.mpath
        self.parentpath = os.path.normpath(os.path.expanduser(self.mpath+os.path.sep+".."))
        print prefix, self.mpath
        print self.parentpath
        self.tmpexists = os.path.exists(self.parentpath)
        os.makedirs(os.path.expanduser(self.mpath))

        self.store=filestore("attrfile:"+self.mpath,create = False)
        self.store.set_owner(DummySystem)
        self.has_scm = False
    
    def tearDown(self):
        self.store.lock()
        self.store.close()
        self.store = None
        shutil.rmtree(os.path.expanduser(self.mpath))
        if not self.tmpexists: 
            os.rmdir(self.parentpath)

def getTestNames():
    	return [ 'file_store.filestoreTests' , 'file_store.tests2' ] 

if __name__ == '__main__':
    unittest.main()
    
