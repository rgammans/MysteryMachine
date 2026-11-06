#!/usr/bin/env python
#               VersionNr.py - Copyright Roger Gammans
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
Tests for the MysteryMachine.TrustedPluginManager class
"""

from MysteryMachine.ExtensionSecureID import ExtensionSecureID
from MysteryMachine.PluginManager import TrustedPluginManager, PluginLoadError
import unittest
import os

class TrustExtManTest(unittest.TestCase):
    def setUp(self):
        #1. Get First.py, make hash and add to 
        #   config object.
        extpath=os.path.join( os.path.dirname(os.path.abspath(__file__)),"Plugins")
        trustedp=ExtensionSecureID.fromPathName(os.path.join(extpath,"First.py"))
        self.config = { "FirstPlugin" : trustedp }        
    
        #2. Create Trustmanager class and collect plugins.
        self.myPluginManager = TrustedPluginManager([ extpath ], [ self.config ])

        self.myPluginManager.locate()
        # Will be used later
        self.plugin_info = None

    def testTrusted(self):
        plugins = list(self.myPluginManager.candidates())
        self.assertEqual(len(plugins),1)
        for plugin_info in plugins:
            self.plugin_info = plugin_info
            self.assertTrue(self.plugin_info)
            self.assertEqual(self.plugin_info.name,"FirstPlugin")

    def testRejected(self):
        #Check plugins accestp/reject are the ones we expect.
        rejects = []
        for r in self.myPluginManager.rejected():
            rejects.append(r)
        #Check correct number of rejects
        self.assertEqual(len(rejects) , 1)
        self.assertEqual(rejects[0].name,"SecondPlugin")


    def testAddTrust(self):
        #Add second to trust list.
        orig=len(self.config)
        for reject in self.myPluginManager.rejected():
            self.myPluginManager.trust(reject)

        plugins = list(self.myPluginManager.candidates())
        self.assertEqual(len(plugins),2)
        self.assertEqual(len(self.config),2)

    def testUntrust(self):
        # check the number of plugins
        plugins = list(self.myPluginManager.candidates())
        self.assertEqual(len(plugins),1)
        rejects = list( self.myPluginManager.rejected())
        self.assertEqual(len(rejects),1)
        self.myPluginManager.untrust(plugins[0])
        plugins = list(self.myPluginManager.candidates())
        rejects = list( self.myPluginManager.rejected())
        self.assertEqual(len(rejects),2)
        self.assertEqual(len(plugins),0)

    def testCantLoadRejected(self):
        reject = list(self.myPluginManager.rejected())[0]
        self.assertRaises(PluginLoadError,self.myPluginManager.load,reject)
        self.assertFalse(reject.isLoaded())

    def testUntrustUnloads(self):
        plugin = list(self.myPluginManager.candidates())[0]
        self.myPluginManager.load(plugin)
        self.assertIs(self.myPluginManager.get_by_name(plugin.name),plugin)
        self.myPluginManager.untrust(plugin)
        self.assertIsNone(self.myPluginManager.get_by_name(plugin.name))
 

def getTestNames():
    return [ 'TrustExtManTest.TrustExtManTest' ] 

if __name__ == '__main__':
    unittest.main()

