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
Tests for the MysteryMachine.VersionNr class
"""

from MysteryMachine.VersionNr import VersionNr
import unittest

class VernoTest(unittest.TestCase):
	def testLessThan(self):
		self.assert_( VersionNr(3,1) < VersionNr(4,1) )
		self.assert_( VersionNr(3)   < VersionNr(3,1))
		self.assert_( VersionNr(3,1) < VersionNr(4,1))
		self.assert_( VersionNr(3)   < VersionNr(3,1))
		self.assert_( VersionNr(1) < VersionNr(3) )
		self.assert_( VersionNr(0) < VersionNr(3) )
	
	def testGreaterThanOrEquals(self):
		self.assert_( VersionNr(4,1) >= VersionNr(3,1) )
		self.assert_( VersionNr(3,1) >= VersionNr(3) )
		self.assert_( VersionNr(3) >= VersionNr(3) )
		self.assert_( VersionNr(3,1) >= VersionNr("3.1") )


	def testGreaterThan(self):
		self.assert_( VersionNr(4,1) > VersionNr(3,1) )
		self.assert_( VersionNr(3,1) > VersionNr(3) )

	def testEquals(self):
		self.assert_( VersionNr(3) == VersionNr(3) )
		self.assert_( VersionNr(3,1) == VersionNr("3.1") )
		self.assertFalse( VersionNr(3) == VersionNr("3.1") )

	def testCopy(self):
		a=VersionNr(3,1)
		b=VersionNr(a)
		self.assertEqual( a , b )


def getTestNames():
	return [ 'VernoTest.VernoTest' ] 

if __name__ == '__main__':
    unittest.main()

