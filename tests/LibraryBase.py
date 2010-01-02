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

    def testLoadSave(self):
        with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"]) as g:
            #Load example pack file and test attributes

            test1 = g.OpenPackFile("examples/test1.mmpack")
            self.assertTrue(isinstance(test1,MMSystem))
            self.assertEqual(len(list(test1.EnumObjects("Items"))),2)
            self.assertEqual(len(list(test1.getChangeLog())),1)

            g.SavePackFile(test1,"/tmp/test1.mmpack")

            #Open new and old pack files up and compare.
            newpack = zipfile.ZipFile("/tmp/test1.mmpack","r")
            oldpack = zipfile.ZipFile("examples/test1.mmpack","r")

            newinflist = []
            for f in newpack.infolist():
                #We can ignore this file as it is a mercurial repo file
                # which is new in mercurial 1.4    
                if f.filename != '.hg/tags.cache': newinflist += [ f ]

            oldinflist = [ x for x  in oldpack.infolist() if x.filename[-1] != os.sep ]
            self.assertEqual(len(newinflist),len(oldinflist))
            for newinf in newinflist:
                #Don't check dirstate file
                # Opening a file call hg.revert which can touch this. 
                if newinf.filename == ".hg/dirstate": continue
                oldinf = oldpack.getinfo(newinf.filename)
                self.assertEqual(oldinf.CRC,newinf.CRC)
                if newinf.filename == ".formatver":
                    #Check permission on the file are at least owner read/write.
                    pass
            oldpack.close()
            newpack.close()

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

