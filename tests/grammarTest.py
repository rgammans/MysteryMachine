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
Tests for the MysteryMachine.VersionNr class
"""

from MysteryMachine import * 
from MysteryMachine.parsetools.grammar import Grammar
 
import unittest
import logging

##Dummy fucntions to which use python DuckTyping to remove deps on 
# higehr level modules/class

class MMObject:
    def __init__(self,*args,**kwargs):
        self.id=""
        if len(args) > 0:
            self.id=args[0]
        self.items = {}
        for key in kwargs:
           self.items[key] = kwargs[key] 
    def get_root(self):
        return SystemProxy()
    def __repr__(self):
        return self.id
    def __getitem__(self,name):
        return self.items[name]

ObjectProxy = MMObject
class SystemProxy: 
    def get_object(self,cat,id):
        return MMObject(cat + ":" +id)
    

def helper(parser,input):
    inlist = parser.parseString(input)
    rv = inlist[0]
    for item in inlist[1:]:
        rv += item 
    return rv

class GraamarTest(unittest.TestCase):
    def setUp(self):
        StartApp(["--cfgengine=ConfigDict", "--cfgfile=test.cfg", "--testmode"]) 
        self.parserA=Grammar( ObjectProxy( name="TestName",  title="A Title") )
        self.parserB=Grammar( ObjectProxy( name="WrongName", title="A Title") )

        #self.logger = logging.getLogger("MysteryMachine.parsetools.grammar")
        #self.logger.setLevel(logging.DEBUG)
    
    def testWhitespace(self):
        #testString="This is a parser\n Test string\n to test whitespace  preservation"
        #We don't seem to preserve tabs.
        #self.assertEqual(testString,helper(self.parserA,testString))
        """
        This test is no longer pertinent now we rely on Docutils roles
        """
        pass

    def testExpansions(self):
        self.assertEqual("TestName",helper(self.parserA,":name"))
        self.assertEqual("WrongName",helper(self.parserB,":name"))
    
    def testInvalidSyntax(self):
        import pyparsing
        self.assertRaises(pyparsing.ParseException,helper,self.parserA,"NothingMeaningfull")    

    def testObjectFetch(self):
        self.assertEqual(helper(self.parserA,"Object:1").__class__ ,    MMObject)
        self.assertEqual(repr(helper(self.parserA,"Object:1")) , "Object:1" )

    def testQueryOp(self):
        self.assertEqual(helper(self.parserA,":name=\"TestName\"?\"Yes\"/\"No\""),"Yes")
        self.assertEqual(helper(self.parserA,":name=\"WrongName\"?\":Yes\"/\"No\""),"No")

    # Test handling of parse errors.
def getTestNames():
	return [ 'grammarTest.GrammarTest' ] 

if __name__ == '__main__':
    unittest.main()
