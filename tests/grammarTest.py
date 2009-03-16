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

from MysteryMachine.parsetools.grammar import Grammar
import unittest

class ObjectProxy:
    def __init__(self,**kwargs):
        for key in kwargs:
           self.__dict__[key] = kwargs[key] 


def helper(parser,input):
    return reduce(lambda x,y:x+y,parser.parseString(input))

class GraamarTest(unittest.TestCase):
    def setUp(self):
         self.parserA=Grammar(ObjectProxy(name="TestName",title="A Title"))
         self.parserB=Grammar(ObjectProxy(name="WrongName",title="A Title"))

    
    def testWhitespace(self):
        testString="This is a parser\n Test string\n to test whitespace  preservation"
        #We don't seem to preserve tabs.
        self.assertEqual(testString,helper(self.parserA,testString))

    def testExpansions(self):
        self.assertEqual("TestName",helper(self.parserA,"${:name}"))
        self.assertEqual("this is a TestName",helper(self.parserA,"this is a ${:name}"))
        self.assertEqual("this is a WrongName",helper(self.parserB,"this is a ${:name}"))
        

    # TODO
    # Test MMObject fetching
    # Test handling of parse errors.
def getTestNames():
	return [ 'grammarTest.GrammarTest' ] 

if __name__ == '__main__':
    unittest.main()

