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
Tests for the MysteryMachine.Schema AttributeValue module
"""

from MysteryMachine.schema.MMAttributeValue import * 
from MysteryMachine.schema.MMObject import MMObject
import unittest
from MysteryMachine import * 


class ObjectProxy(MMObject):
    def __init__(self,*args,**kwargs):
        l = [ "" ,"" ]
        if len(args)<2:
            if len(args)<1:
                pass
            else:
                l[0] = args[0]
        else:
            l[0] =args[0]
            l[1] =args[1]
        super(ObjectProxy,self).__init__(l[0] + ":" + l[1] , None )
        for key in kwargs:
           self.__dict__[key] = kwargs[key] 
    def __str__(self):
        return self.id
    def get_root(self):
        return SystemProxy()
    def __eq__(self,other):
        #Fake - equals as required for this test.
        return self.id == other.id

class SystemProxy: 
    def get_object(self,cat,id):
        return ObjectProxy(cat , id)
    
class DummyPart:
    def __init__(self,x):
        self.x=x
    def get_value(self):
        return self.x

class attribValTest(unittest.TestCase):
    def setUp(self):
       StartApp(["--cfgengine=pyConfigDict", "--cfgfile=test.cfg", "--testmode"]) 
       self.objA=ObjectProxy("Proxy", "1", name="TestName",title="A Title")
       self.objB=ObjectProxy("Proxy", "2", name="WrongName",title="A Title")
    
    def testCreate(self):
       val=MMAttributeValue([DummyPart("test"),DummyPart("this")])
       self.assertEqual(val.get_raw_rst(),"test\nthis")
       self.assertEqual(len(val.get_parts()),2)

    def testObjRef(self):
        self.makeRef()
        self.assertEqual(self.objrefA.get_object(self.objA) , self.objA )
        self.assertEqual(self.objrefB.get_object(self.objA) , self.objB )


    def makeRef(self):
        self.objrefA = MMAttributeValue_MMObjectRef( [ MMAttributePart("",self.objA) ] )
        self.objrefB = MMAttributeValue_MMObjectRef( [ MMAttributePart("",self.objB) ] )        
  
    # TODO
    # Test handling of parse errors.      
def getTestNames():
	return [ 'attribValueTest.attribValTest' ] 

if __name__ == '__main__':
    unittest.main()

