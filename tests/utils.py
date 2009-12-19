#!/usr/bin/env python
#   			tests/utils.py - Copyright Roger Gammans
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
This is a combined test fro the MysteryMachine utils modules
"""

from MysteryMachine.utils import *
#Use our own hash class to test for modification.
import unittest

import os

class UtilsTest(unittest.TestCase):
    def testPath_make_rel(self):
        path1 = [ "etc" , "something" , "else" , "somewhere", "else" ]
        path2 = [ "home" , "user" , "etc" , "something" ]

        self.assertEqual(path.make_rel(os.path.join(*path1),os.path.join(*path1)),[ "." ])
        self.assertEqual(path.make_rel(os.path.join(os.sep,*path1),os.sep),[ os.sep ])
        self.assertEqual(path.make_rel(os.sep,os.path.join(os.sep,*path1)), [ os.path.join(*path1) ])
        self.assertEqual(path.make_rel(os.path.join(*path2),os.path.join(*path1)),[ os.path.join(*path1) ])
        
        self.assertEqual(path.make_rel(os.path.join(*path2),os.path.join(*path1),os.path.join(*path2)),[ os.path.join(*path1) ,"." ])

    


def getTestNames():
	return [ 'utils.UtilsTest' ] 

if __name__ == '__main__':
    unittest.main()

