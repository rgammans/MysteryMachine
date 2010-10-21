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
Tests for the MysteryMachine.parsetools.gramar file
"""

from MysteryMachine.parsetools.grammar import Grammar
from MysteryMachine.Exceptions import NullReference,NoAttribute
 
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
        return SystemProxy(self.items["test"])
    def __repr__(self):
        return self.id
    def __getitem__(self,name):
        return self.items[name]

ObjectProxy = MMObject
class SystemProxy: 
    def __init__(self,test):
        self.test = test
    def get_object(self,cat,id):
        if cat == "Test":
            return getattr(self.test,id)
        return MMObject(cat + ":" +id)
    

def helper(parser,input):
    inlist = parser.parseString(input)
    rv = inlist[0]
    for item in inlist[1:]:
        rv += item 
    return rv

class DummyAttribute(object):
    def getSelf(self): return None

class GraamarTest(unittest.TestCase):
    def setUp(self):
        self.C = ( ObjectProxy( name="AnotherName",  test=self, title="A Title", yes="YEAH!", no="Nope") )
        self.A = ( ObjectProxy( name="TestName",    test=self, nullRef = None, nullAttr=DummyAttribute() , obj=self.C, title="A Title", yes="YEAH!", no="Nope") )
        self.parserA=Grammar( self.A )
        self.parserB=Grammar( ObjectProxy( test=self, name="WrongName", title="A Title", a=self.A) )

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
        self.assertEqual("TestName", helper(self.parserB,":a:name") )
        self.assertEqual("AnotherName", helper(self.parserB,":a:obj:name") )
        self.assertEqual("AnotherName", helper(self.parserB,"Test:C:name") )
        self.assertEqual("TestName", helper(self.parserB,"Test:A:name") )
        self.assertEqual("AnotherName", helper(self.parserB,"Test:A:obj:name") )
   
    def testInvalidSyntax(self):
        import pyparsing
        self.assertRaises(pyparsing.ParseException,helper,self.parserA,"NothingMeaningfull")    
        self.assertRaises(NoAttribute,self.parserA.parseString,":not_here")
        self.assertRaises(NullReference,self.parserA.parseString,":nullRef:foo")
        self.assertRaises(NullReference,self.parserA.parseString,":nullAttr:foo")
 
    def testObjectFetch(self):
        self.assertEqual(helper(self.parserA,"Object:1").__class__ ,    MMObject)
        self.assertEqual(repr(helper(self.parserA,"Object:1")) , "Object:1" )

    def testQueryOp(self):
        self.assertEqual(helper(self.parserA,":name=\"TestName\"?\"Yes\"/\"No\""),"Yes")
        self.assertEqual(helper(self.parserA,":name=\"WrongName\"?\":Yes\"/\"No\""),"No")
        #Now check with different lvalues..
        self.assertEqual(helper(self.parserA,":name=\"TestName\"?:yes/:no"),"YEAH!")
        self.assertEqual(helper(self.parserA,":name=\"WrongName\"?:yes/:no"),"Nope")
        self.assertEqual(helper(self.parserA,":name=:title?:yes/:no"),"Nope")
        #Check Not equals
        self.assertEqual(helper(self.parserA,":name!=\"WrongName\"?:yes/:no"),"YEAH!")


    # Test handling of parse errors.
def getTestNames():
	return [ 'grammarTest.GrammarTest' ] 

if __name__ == '__main__':
    unittest.main()
