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
            newinflist = [ x for x  in newpack.infolist() if x.filename[-1] != os.sep ]
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

    def testContxtMan(self):
        pass

def getTestNames():
	return [ 'LibraryBase.LibBaseTest' ] 

if __name__ == '__main__':
    unittest.main()

