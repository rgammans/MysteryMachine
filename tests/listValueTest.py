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

from MysteryMachine.schema.MMListAttribute import * 
from MysteryMachine.schema.MMListAttribute import _Key as ListKey 
from MysteryMachine.schema.MMAttributeValue import * 
from MysteryMachine.schema.MMAttribute import * 
import unittest
from MysteryMachine import * 
from itertools import izip

class SystemProxy: 
    def get_object(self,cat,id):
        return ObjectProxy(cat , id)
    def getSelf(self):
        return self

class DummyParser:
    def GetString(self,string,node):
        return string

class ObjectProxy(dict):
    def get_parser(self):
       return DummyParser() 


    
class ListValTest(unittest.TestCase):
    def setUp(self):
       StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"]) 
    
    def testList(self):
        val  = MMListAttribute(value =  [ "first" , "second" , "third" ] )
        self.assertEquals(str(val[0] )  , "first")      
        self.assertEquals(str(val[1] )  , "second")      
        self.assertEquals(str(val[2] )  , "third")      
        val.append("fourth")
        self.assertEquals(val.count(),4)
        self.assertEquals(str(val[3])  , "fourth")
        val.insert(2,"2 and half'th")
        self.assertEquals(str(val[0] )  , "first")      
        self.assertEquals(str(val[1] )  , "second")      
        self.assertEquals(str(val[2])  ,  "2 and half'th")
        self.assertEquals(str(val[3])   , "third")      
        self.assertEquals(str(val[4])   , "fourth")      
        self.assertEquals(val.count(),5)
        self.assertTrue("third" in val)
        self.assertEquals(len(list(iter(val))),5)
        val.insert(0,"zeroth")
        self.assertEquals(str(val[0] )  , "zeroth")      
        self.assertEquals(str(val[1] )  , "first")      
        self.assertEquals(str(val[2] )  , "second")      
        self.assertEquals(str(val[3] ) ,  "2 and half'th")
        self.assertEquals(str(val[4] )  , "third")      
        self.assertEquals(str(val[5] )  , "fourth")  
        self.assertTrue("third" in val)
        self.assertTrue("zeroth" in val)
        self.assertEquals(val.count(),6)
        self.assertEquals(len(list(iter(val))),6)
        del val[4]
        self.assertEquals(str(val[0] )  , "zeroth")      
        self.assertEquals(str(val[1] )  , "first")      
        self.assertEquals(str(val[2] )  , "second")      
        self.assertEquals(str(val[3])  ,  "2 and half'th")
        self.assertEquals(str(val[4])   , "fourth")  
        self.assertFalse("third" in val)
        self.assertEquals(val.count(),5)
        val[3]="third" 
        self.assertEquals(str(val[0] )  , "zeroth")      
        self.assertEquals(str(val[1] )  , "first")      
        self.assertEquals(str(val[2] )  , "second")      
        self.assertEquals(str(val[3] )  ,  "third")
        self.assertEquals(str(val[4])   , "fourth")  
        self.assertEquals(val.count(),5)
        self.assertEquals(len(list(iter(val))),5)

    def testAttributeForward(self):
        val  = MMListAttribute(value =  [ "first" , "second" , "third" ] )
        obj  = ObjectProxy()
        attr = MMAttribute("test",val,obj)
        self.assertEquals(attr.count() ,3 )        
        self.assertEquals(str(attr.__getitem__(1)) , "second" )        
        self.assertEquals(str(attr[1]) ,"second" )        
        self.assertEquals(str(attr["1"]) ,"second" )        
        self.assertTrue("second" in attr )
        self.assertEquals(str(attr["-1"]) ,"third" )        
        del attr["1"]
        self.assertEquals(attr.count() ,2 )        
        self.assertEquals(len(list(iter(attr))),2)
        self.assertFalse("second" in attr )
        self.assertEquals(str(attr["1"]) ,"third" )        
        #Check writeback occurred.
        self.assertEquals(obj["test"],val)
        valo = CreateAttributeValue("primary")
        attr["0"] = valo
        self.assertEquals(attr[0].get_value(),valo) 
 
        
        #Test Stable key behaviour.
        skey = repr(attr[0]).split(":")[-1]
        self.assertNotEquals(skey,"0")
        self.assertNotEquals(skey,0)
        self.assertEquals(attr[0],attr["0"])
        self.assertEquals(attr[skey],attr[0],msg=("attr[\"%s\"] != attr[0]" % skey))
        skey = repr(attr["1"]).split(":")[-1]
        self.assertNotEquals(skey,"1")
        self.assertNotEquals(skey,1)
        self.assertEquals(attr[skey],attr[1])


        
        
        #Clear dict so can check writeback again
        del obj["test"]
        attr[1]="second"
        self.assertEquals(str(attr["1"]) ,"second" )        
        self.assertEquals(obj["test"],val)
        #Check walk back thru and find a parser
        self.assertEquals(attr[1].GetFullExpansion(),"second")

        del obj["test"]
        attr.append("some fate")
        self.assertEquals(obj["test"],val)
        self.assertEquals(str(attr["2"]) ,"some fate" )        

        del obj["test"]
        attr.insert(2,"some date")
        self.assertEquals(obj["test"],val)
        self.assertEquals(str(attr["2"]) ,"some date" )        
        self.assertEquals(str(attr["3"]) ,"some fate" )        


        #Check trying insert an invalid class.
        class dummy (MMAttributeValue):
            typename = "dummy"
            contain_prefs = {}
         
        def test(a):
            a[2] = dummy(parts = {'f':"testing", 'g':"123"})
                   
        self.assertRaises(TypeError,test,attr)

        ###Test itertation..
        names = [ 0,1,2,3 ]
        fndNames= []
        for k,v in attr:
            self.assertTrue(k in names)
            self.assertFalse(k in fndNames)
            fndNames += [ k ]
            self.assertTrue(isinstance( v, MMAttribute))
            self.assertEquals(v,attr[k])




    def testKey(self):
        a = ListKey()
        self.assertFalse(a is None)
        #FIXME Add asserion about the empty/null position.

        ## Now test next generates increasing values..
        a = a.next()
        b = a
        
        #Val list to use to test insertion too!.
        vallist = [ ListKey() , a ]
        
        # Check  string as length increases too..
        for i in xrange(3):
            a = b
            while len(str(a)) >= len(str(b)):
                c = b
                b = b.next()
                vallist.append(b)
                self.assertTrue(str(b) > str(c))
        
        ## Check between creates useful values.
        for ele1,ele2 in izip(vallist,vallist[1:]):
            b = ele2
            a = ele1
            for i in xrange(4):
                a = b
                while len(str(a)) >= len(str(b)):
                    c = b
                    b = ele1.between(str(c))
                    self.assertTrue(str(b) > str(ele1))
                    self.assertTrue(str(c) > str(b))
 
def getTestNames():
	return [ 'listValueTest.ListValTest' ] 

if __name__ == '__main__':
    unittest.main()

