#!/usr/bin/env python
#   			grammarTest.py - Copyright Roger Gammans
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
Tests for the MysteryMachine.Schema MMObject  module
"""

from MysteryMachine import * 
from MysteryMachine.store.dict_store import *
from MysteryMachine.schema.MMSystem import MMSystem
import unittest
import pyparsing

class ParsersTests(unittest.TestCase):
    def setUp(self):
        StartApp(["--cfgengine=ConfigDict", "--cfgfile=test.cfg", "--testmode"]) 
        self.sys=MMSystem.Create("dict:test")
        self.sys.NewCategory("template")
        self.p=self.sys.NewObject("template")
        self.p[".defname"] = ":mm:`:name`"
        self.p["name"] = "Dummy"
        self.sys.NewCategory("Item")
        self.i=self.sys.NewObject("Item")
        self.i["name"]="The one ring"
        self.i.set_parent(self.p)
        self.sys.NewCategory("Character")
        self.c=self.sys.NewObject("Character")
        self.c["name"]="Frodo"
        self.c["carries"]=self.i
        self.c.set_parent(self.p)
        #modlogger   = logging.getLogger("MysteryMachine.parsetools.MMParser")
        #logging.getLogger("MysteryMachine.parsetools.grammar").setLevel(logging.DEBUG)
        #modlogger.setLevel(logging.DEBUG)

        
 
    def testParser(self):
        self.assertEquals(self.c["carries"].GetFullExpansion(),"The one ring")
        self.assertEquals(str(self.c),"Frodo")
        self.p['.defname'] =  ":mm:`:name` :mm:`:lname`"
        #self.p['lname'] = ""
        self.c['lname'] = "Baggins"
        self.assertEquals(str(self.c),"Frodo Baggins")
        self.assertEquals(str(self.i),"The one ring ")
        #Test Invalid syntax
        self.c['foo'] = ':mm:`not_a_macro`'
        #There will be and error message as well
        self.assertEquals(str(self.c['foo'].GetFullExpansion()),"")
        

    def testCycle(self):
        self.c["cycle"]=":mm:`:cycle`"
        #Trigger a cycle and check we don't raise an exception.
        a=self.c["cycle"].GetFullExpansion()
        ##TODO Set up somethin that looks like a cycle but isn't.

def getTestNames():
    	return [ 'Parser.ParserTests' ] 

if __name__ == '__main__':
    unittest.main()

