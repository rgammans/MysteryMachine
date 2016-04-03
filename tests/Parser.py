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
import re

class ParsersTests(unittest.TestCase):
    def setUp(self):
        self.ctx = StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"]) 
        self.sys=MMSystem.Create("dict:test")
        self.sys.NewCategory("template")
        self.p=self.sys.NewObject("template")
        self.p[".defname"] = ":mm:`:name`"
        self.p["name"] = "Dummy"
        self.sys.NewCategory("Item")
        self.i=self.sys.NewObject("Item")
        self.i["name"]="The one ring"
        self.i["not_a_cycle"]="hovercraft"
        self.i["bike"]       =":mm:`:not_a_cycle`"
        self.i.set_parent(self.p)
        self.sys.NewCategory("Character")
        self.c=self.sys.NewObject("Character")
        self.c2=self.sys.NewObject("Character")
        self.c["name"]="Frodo"
        self.c["carries"]=self.i
        self.c.set_parent(self.p)
        self.c2.set_parent(self.p)
        self.c2["name"]=u"Frodo"
        #modlogger   = logging.getLogger("MysteryMachine.parsetools.MMParser")
        #logging.getLogger("MysteryMachine.parsetools.grammar").setLevel(logging.DEBUG)
        #modlogger.setLevel(logging.DEBUG)

        
    def tearDown(self,):
        self.ctx.close()

    def testParser(self):
        self.assertEquals(self.c["carries"].GetFullExpansion(),"The one ring")
        self.assertEquals(unicode(self.c),"Frodo")
        self.p['.defname'] =  ":mm:`:name` :mm:`:lname`"
        self.p['lname'] = ""
        self.c['lname'] = "Baggins"
        self.assertEquals(unicode(self.c),"Frodo Baggins")
        self.assertEquals(unicode(self.i),"The one ring ")
        #Test Invalid syntax
        self.c['foo'] = ':mm:`not_a_macro`'
        #We shouldn't raise but will have docutils XML reporting a ParseException
        foo_str = self.c['foo'].GetFullExpansion()
        self.assertTrue(re.search("<error",foo_str))
        self.assertTrue(re.search("ParseException",foo_str))
        #Test settings
        self.assertEquals(unicode(self.i['bike'].GetFullExpansion()),"hovercraft")
        self.c['test']=":mm:`:carries:bike`"
        self.assertEquals(unicode(self.c['test'].GetFullExpansion()),"hovercraft")
        #Test mm roel state after recursion - eg state is restored on stack pop.
        self.c['test2']=":mm:`:carries:bike` :mm:`:name`" 
        self.assertEquals( unicode(self.c['test2'].GetFullExpansion()),"hovercraft Frodo")
        #test literal values are handled
        self.c['test3']=":mm:`\"A Literal value\"`" 
        self.assertEquals( unicode(self.c['test3'].GetFullExpansion()),"A Literal value")


    def testUnicode(self):
        self.assertEquals(unicode(self.c2),u"Frodo")
        

    def testCycle(self):
        self.c["cycle"]=":mm:`:cycle`"
        #Trigger a cycle and check we don't raise an exception.
        a=self.c["cycle"].GetFullExpansion()
        #Set up something that might look like a cycle but isn't.
        self.c["not_a_cycle"]=":mm:`"+repr(self.i)+":bike`"
        self.assertEquals(unicode(self.c["not_a_cycle"].GetFullExpansion()),"hovercraft")

def getTestNames():
    	return [ 'Parser.ParserTests' ] 

if __name__ == '__main__':
    unittest.main()

