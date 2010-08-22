#!/usr/bin/env python
#   			tests/LibraryBase.py - Copyright Roger Gammans
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
Tests for the MysteryMachine base module.
"""

from __future__ import with_statement

from MysteryMachine.schema.MMSystem import MMSystem
from MysteryMachine import *
import unittest

import MysteryMachine.utils.path as path
import tempfile
import zipfile

import mercurial
import mercurial.verify 
from mercurial import hg



class MyUi(object):
    def mercurial_ui(self):
        return "MercurialUi"


class LibBaseTest(unittest.TestCase):

    def testOptParsing(self):
        #TODO
        # write option parsing tests.
        pass

    def testExtLibFns(self):
        with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"]) as g:
            #Check correct type.
            el = g.GetExtLib()
            self.assertTrue(isinstance(el,ExtensionLib))
            #Check returns a consistent instance
            self.assertTrue(el is g.GetExtLib())

    def testLoadSave0(self):
        with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"]) as g:
            #Load example pack file and test attributes

            test1 = g.OpenPackFile("examples/test1.mmpack")
            for rev in test1.getChangeLog():
                head = rev

            self.assertTrue(isinstance(test1,MMSystem))
            self.assertEqual(len(list(test1.EnumObjects("Items"))),2)
            self.assertEqual(len(list(test1.getChangeLog())),1)
        
            
            test1.SaveAsPackFile("/tmp/test1.mmpack")

            #Open new and old pack files up and compare.
            newpack = zipfile.ZipFile("/tmp/test1.mmpack","r")
            dest = tempfile.mkdtemp()
            path.zunpack(newpack,dest) 
            # -  This following code assumes a mercurial scm based pack file.
            ##Unpack the new files...(0
            repo = hg.repository(g.GetMercurialUi() , dest ) 
            self.assertTrue(mercurial.verify.verify(repo) is None)
            #This breaks if our example file has multiple heads! So it must not.
            #If the repo verifies and the nodeid's are the same , the repo MUST
            # contain the same data . (Guarantee here are as strong or as weak as SHA1).
            self.assertEquals(repo.heads(None)[0],head.node())

    def testCreate(self):
        with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"]) as g:
            import MysteryMachine.store.dict_store
            system = g.CreateNew(scheme = "dict")
            self.assertFalse(system is None)
            import MysteryMachine.schema.MMSystem
            self.assertEquals(type(system),MysteryMachine.schema.MMSystem.MMSystem)
            self.assertEquals(system.getUri()[0:5] , "dict:")
            system = g.CreateNew(scheme = "foo", uri="dict:uritest")
            self.assertFalse(system is None)
            self.assertEquals(system.getUri() , "dict:uritest")
            import MysteryMachine.store.hgfile_class
            system = g.CreateNew(scheme = "hgafile")
            system = g.CreateNew(uri = "dict:foo")

    def testContxtMan(self):
        pass

    def testUi(self):
        MysteryMachine.MyUi = MyUi
        with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode",
                       "--ui=MyUi"]) as g:
            self.assertNotEquals(g.Ui,None)
            self.assertEquals(g.GetMercurialUi(),"MercurialUi")

def getTestNames():
	return [ 'LibraryBase.LibBaseTest' ] 

if __name__ == '__main__':
    unittest.main()

