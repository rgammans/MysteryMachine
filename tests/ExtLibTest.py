#!/usr/bin/env python
#               ExtLibTest.py - Copyright Roger Gammans
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
# This file was generated on Tue Dec 30 2008 at 15:39:18
# The original location of this file is /home/roger/sources/MysteryMachine/generated/VersionNr.py
#


"""
Tests for the MysteryMachine.ExtensionLib class
"""

from __future__ import with_statement


from MysteryMachine import *
import unittest
import os
import logging

def foo(object):  
    return object()

class ExtensionLibTest(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("")
        
    def gettrustedlist(self):
      with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"])  as g:
        self.extlib = g.GetExtLib()
        plugins = []
        for p in self.extlib.get_extension_list():
            if self.extlib.IsTrusted(p):
                plugins +=  [ p ]
        return plugins
          
    def testTrusted(self):
      with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"])  as g:
        self.extlib = g.GetExtLib()
        # check the number of plugins
        plugins = self.gettrustedlist()

        self.assertEqual(len(plugins),1)
        self.assertEqual(plugins[0].name,"FirstPlugin")

    def testRejected(self):
      with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"])  as g:
        self.extlib = g.GetExtLib()
        #Check plugins accestp/reject are the ones we expect.
        rejects = []
        for r in self.extlib.get_extension_list():
            if not self.extlib.IsTrusted(r):
                rejects.append(r)
        #Check correct number of rejects
        self.assertEqual(len(rejects) , 1)
        self.assertEqual(rejects[0].name,"SecondPlugin")


    def testAddTrust(self):
      with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"])  as g:
        self.extlib = g.GetExtLib()
        #Add second to trust list
        self.logger.debug("starting addtrust======")
        to_trust = []
        for reject in self.extlib.get_extension_list():
            if not self.extlib.IsTrusted(reject):
                self.extlib.SetTrust(reject,True)

        #FIXME - test the worng thing`
        plugins = self.gettrustedlist()  
        self.assertEqual(len(plugins),2)

    def testHelpers(self):
      with StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"])  as g:
        self.extlib = g.GetExtLib()
        self.extlib.register_helper("bar",foo);
        self.assertEqual(len(self.extlib.get_helpers_for("bar")),1)
        self.extlib.unregister_helper("bar",foo);
        self.assertEqual(len(self.extlib.get_helpers_for("bar")),0)
 
    def testUntrust(self):
        pass
       # REemove all from trustlist.
#        for reject in self.extlib.get_extension_list():
#            print reject
#            self.extlib.SetTrust(reject,False)

#       plugins = self.gettrustedlist()  
#        self.assertEqual(len(plugins),0)

def getTestNames():
    return [ 'ExtLibTest.ExtensionLibTest' ] 

if __name__ == '__main__':
    unittest.main()

