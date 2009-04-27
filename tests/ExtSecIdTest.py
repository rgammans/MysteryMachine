#!/usr/bin/env python
#   			VersionNr.py - Copyright Roger Gammans
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
# This file was generated on Tue Dec 30 2008 at 15:39:18
# The original location of this file is /home/roger/sources/MysteryMachine/generated/VersionNr.py
#


"""
Tests for the MysteryMachine.ExtensionSecureID class
"""

from MysteryMachine.ExtensionSecureID import ExtensionSecureID
import unittest

class ExtSecIdTest(unittest.TestCase):
	def setUp(self):
		self.cfvalue= str("sha256|230550d1627270f0cf2ff8bec59679a6079266d3c68ac3e1653cd0a97276fdec" )
		self.testpath="CodingGuidelines"
	def testBasic(self):
		hash1=ExtensionSecureID.fromPathName(self.testpath)
		hash2=ExtensionSecureID.fromPathName(self.testpath)
		self.assertEquals( hash1 , hash2 )

	def testStr(self):
		a=ExtensionSecureID.fromPathName(self.testpath)
		self.assertEqual( str(a) ,self.cfvalue)

	def testKnownHash(self):
		hash1=ExtensionSecureID.fromHash(self.testpath, self.cfvalue)
		self.assertEqual( str(hash1) , self.cfvalue )
		self.assertEqual( hash1 , self.cfvalue )
		hash2=ExtensionSecureID.fromPathName(self.testpath)
		self.assertEqual(hash1 , hash2 )

	def testHashoFHash(self):
		hash1=ExtensionSecureID.fromHash(self.testpath, self.cfvalue)
		hash2=ExtensionSecureID.fromPathName(self.testpath)
		self.assertEqual(hash1.__hash__() , hash2.__hash__() )

def getTestNames():
	return [ 'ExtSecIdTest.ExtSecIdTest' ] 

if __name__ == '__main__':
    unittest.main()

