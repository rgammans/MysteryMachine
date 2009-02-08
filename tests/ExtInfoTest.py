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

from yapsy.PluginManager import PluginManager
from MysteryMachine.ExtensionInfo import ExtensionInfo
from MysteryMachine.ExtensionSecureID import ExtensionSecureID
import os
import unittest
import logging

#logging.basicConfig(level=logging.DEBUG)

class ExtInfoTest(unittest.TestCase):
	def setUp(self):
		# create the plugin manager
		self.simplePluginManager = PluginManager(directories_list=[
				os.path.join(
					os.path.dirname(os.path.abspath(__file__)),"Plugins")
			       ], 
                              plugin_info_ext="mm-plugin",
			)
    		#Set mode to test info class
		self.simplePluginManager.setPluginInfoClass(ExtensionInfo)

		# load the plugins that may be found
		self.simplePluginManager.collectPlugins()
		# Will be used later
		self.plugin_info = None


	def loading_check(self):
		"""
		Test the plugins load.
		"""
		if self.plugin_info is None:
			# check nb of categories
			self.assertEqual(len(self.simplePluginManager.getCategories()),1)
			sole_category = self.simplePluginManager.getCategories()[0]
			# check the number of plugins
			self.assertEqual(len(self.simplePluginManager.getPluginsOfCategory(sole_category)),2)
			self.plugin_info = [ None , None ]
			self.plugin_info[0] = self.simplePluginManager.getPluginsOfCategory(sole_category)[0]
			self.plugin_info[1] = self.simplePluginManager.getPluginsOfCategory(sole_category)[1]
			# test that the name of the plugin has been correctly defined
			self.assertEqual(self.plugin_info[0].name,"FirstPlugin")
			self.assertEqual(sole_category,self.plugin_info[0].category)
		else:
			self.assert_(True)

		
        def testBasic(self):
		self.loading_check()

	def testKnownHash(self):
		"""
		Test hash can be fetched thru ExtensionInfo
                """
		self.loading_check()
		hash1=ExtensionSecureID.fromPathName(self.plugin_info[0].path+".py")
		self.assertEquals(hash1,self.plugin_info[0].getSecureID())
		self.assertNotEquals(self.plugin_info[0].getSecureID(),self.plugin_info[1].getSecureID())

def getTestNames():
	return [ 'ExtInfoTest.ExtInfoTest' ] 

if __name__ == '__main__':
    unittest.main()

