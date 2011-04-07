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
Tests for the MysteryMachine MMSystem Schema node - specifically tests
in here handle things which interact more completey with the
Global environment.
"""

from __future__ import with_statement

from MysteryMachine.schema.MMSystem import MMSystem
from MysteryMachine import *
from MysteryMachine.Exceptions import *
import unittest

import MysteryMachine.utils.path as path
import tempfile
import zipfile
import shutil


class SystGlobalTest(unittest.TestCase):


    def testSavewith_defaultname(self):
        with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/libtest.yaml", "--testmode"]) as g:

            packfname = tempfile.NamedTemporaryFile()
            packfname = packfname.name
            #Create copy of an mmpack file to load.
            shutil.copy("examples/format1.mmpack",packfname)
            
            #Load example pack file and test attributes
            test1 = g.OpenPackFile(packfname)
          
            #Delete the file 
            os.unlink(packfname)
            #Do default save which should save it with the orignal filename
            test1.SaveAsPackFile()
            # - check file is recreated.
            self.assertTrue(os.path.exists(packfname))

    def test_should_raise_if_doesnt_have_a_filename_to_save_with(self):
        with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/libtest.yaml", "--testmode"]) as g:
            sys = g.CreateNew(scheme="dict")
            self.assertRaises(NoPackFileName,sys.SaveAsPackFile)
            

    def testSavewith_altname(self):
        with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/libtest.yaml", "--testmode"]) as g:

            packfname = tempfile.NamedTemporaryFile()
            packfname = packfname.name
            packfname2 = tempfile.NamedTemporaryFile()
            packfname2 = packfname2.name 
            #Create copy of an mmpack file to load.
            shutil.copy("examples/format1.mmpack",packfname)
            
            
            #Load example pack file and test attributes
            test1 = g.OpenPackFile(packfname)
          
            #Delete the file 
            os.unlink(packfname)
            #Do default save which should save it with the orignal filename
            test1.SaveAsPackFile()
            # - check file is recreated.
            self.assertTrue(os.path.exists(packfname))

            test1.SaveAsPackFile(packfname2)
            self.assertTrue(os.path.exists(packfname2))

           ## This is commented out until I decide it is
           # correct behaviour..

           # #Check if the new filename is used now..
           # #Delete the file 
           # os.unlink(packfname2.name)
           # #Do default save which should save it with the orignal filename
           # test1.SaveAsPackFile()
           # ## - check file is recreated.
           # self.assertTrue(os.path.exists(packfname2.name))




if __name__ == '__main__':
    import sys
    if "--debug" in sys.argv:
        import logging

        logging.getLogger("MysteryMachine").setLevel(logging.DEBUG)
        sys.argv.remove("--debug")
    unittest.main()

