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
Tests for the MysteryMachine.ExtensionInfo class
"""

from MysteryMachine.PluginManager import PluginManager
from MysteryMachine.ExtensionInfo import ExtensionInfo
from MysteryMachine.ExtensionSecureID import ExtensionSecureID
import os
import unittest
import logging

#logging.basicConfig(level=logging.DEBUG)

class ExtInfoTest(unittest.TestCase):
	def setUp(self):
		# create the plugin manager - use the base plugin manager to
		# remove any unecessary dependencies
		self.simplePluginManager = PluginManager([
				os.path.join(
					os.path.dirname(os.path.abspath(__file__)),"Plugins")
			       ])

		# load the plugins that may be found
		self.simplePluginManager.locate()
		for plugin in self.simplePluginManager.candidates():
			self.simplePluginManager.load(plugin)
		# Will be used later
		self.plugin_info = None


	def loading_check(self):
		"""
		Test the plugins load.
		"""
		if self.plugin_info is None:
			# check the number of plugins
			self.plugin_info = self.simplePluginManager.loaded()
			self.assertEqual(len(self.plugin_info),2)
			# test that the name of the plugin has been correctly defined
			self.assertTrue("FirstPlugin" in [x.name for x in  self.plugin_info])
			for plugin in self.plugin_info:
				self.assertIsInstance(plugin,ExtensionInfo)
				self.assertTrue(plugin.isLoaded())


	def testBasic(self):
		self.loading_check()

	def testKnownHash(self):
		"""
		Test hash can be fetched thru ExtensionInfo
                """
		self.loading_check()
		hash1=ExtensionSecureID.fromPathName(self.plugin_info[0].path+".py")
		self.assertEqual(hash1,self.plugin_info[0].getSecureID())
		self.assertNotEqual(self.plugin_info[0].getSecureID(),self.plugin_info[1].getSecureID())

def getTestNames():
	return [ 'ExtInfoTest.ExtInfoTest' ] 

if __name__ == '__main__':
    unittest.main()

