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
from MysteryMachine.schema.MMAttribute import * 
from MysteryMachine.schema.MMBase import * 
import unittest
from MysteryMachine import * 
import six
import copy

#Get izip longest from itertools, or make it up with map
# if too early a python
try:
    izip_longest = itertools.izip_longest
except AttributeError:
    izip_longest = functools.partial(map,None)

from mock.schema_top import *

SystemProxy = fakeParent

class DummyParser:
    def GetString(self,string,node):
        return string

system = None
class ObjectProxy(MMAttributeContainer):
    def __init__(self):
        global system
        super(ObjectProxy,self).__init__(self)
        self.d = {}
        self.owner = system 
        self.name = "MockObject"
    
    def get_nodedid(self,): return ":MockObject"   
    def get_parser(self):
       return DummyParser() 
    def __setitem__(self,k,v):
        attr = self._set_attr_item(k,v)
        val = attr.get_value()
        self.d[k] = (val.get_type(), val.get_parts())

    def __getitem__(self,k):
        return self._get_item(k,self.__getitem,k)
    def __getitem(self,k):
        return MMAttribute(k,MakeAttributeValue(self.d[k][0],self.d[k][1]),self)
    def __delitem__(self,k):
        del self.d[k]
        self._invalidate_item(k)

    
class ListValTest(unittest.TestCase):
    def setUp(self):
       global system
       self.ctx = StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"]) 
       system = SystemProxy()

    def tearDown(self,):
        self.ctx.close()

    def testList(self):
        val  = MMListAttribute(value =  [ "first" , "second" , "third" ] )
        self.assertEqual(six.text_type(val[0] )  , "first")      
        self.assertEqual(six.text_type(val[1] )  , "second")      
        self.assertEqual(six.text_type(val[2] )  , "third")      
        val.append("fourth")
        val._compose(None)
        self.assertEqual(val.count(),4)
        self.assertEqual(six.text_type(val[3])  , "fourth")
        val.insert(2,"2 and half'th")
        val._compose(None)
        self.assertEqual(six.text_type(val[0] )  , "first")      
        self.assertEqual(six.text_type(val[1] )  , "second")      
        self.assertEqual(six.text_type(val[2])  ,  "2 and half'th")
        self.assertEqual(six.text_type(val[3])   , "third")      
        self.assertEqual(six.text_type(val[4])   , "fourth")      
        self.assertEqual(val.count(),5)
        self.assertTrue("third" in val)
        self.assertEqual(len(list(iter(val))),5)
        self.assertEqual(len(val),5)
        val.insert(0,"zeroth")
        val._compose(None)
        self.assertEqual(six.text_type(val[0] )  , "zeroth")      
        self.assertEqual(six.text_type(val[1] )  , "first")      
        self.assertEqual(six.text_type(val[2] )  , "second")      
        self.assertEqual(six.text_type(val[3] ) ,  "2 and half'th")
        self.assertEqual(six.text_type(val[4] )  , "third")      
        self.assertEqual(six.text_type(val[5] )  , "fourth")  
        self.assertTrue("third" in val)
        self.assertTrue("zeroth" in val)
        self.assertEqual(val.count(),6)
        self.assertEqual(len(list(iter(val))),6)
        del val[4]
        self.assertEqual(six.text_type(val[0] )  , "zeroth")      
        self.assertEqual(six.text_type(val[1] )  , "first")      
        self.assertEqual(six.text_type(val[2] )  , "second")      
        self.assertEqual(six.text_type(val[3])  ,  "2 and half'th")
        self.assertEqual(six.text_type(val[4])   , "fourth")  
        self.assertFalse("third" in val)
        self.assertEqual(val.count(),5)
        val[3]="third" 
        val._compose(None)
        self.assertEqual(six.text_type(val[0] )  , "zeroth")      
        self.assertEqual(six.text_type(val[1] )  , "first")      
        self.assertEqual(six.text_type(val[2] )  , "second")      
        self.assertEqual(six.text_type(val[3] )  ,  "third")
        self.assertEqual(six.text_type(val[4])   , "fourth")  
        self.assertEqual(val.count(),5)
        self.assertEqual(len(list(iter(val))),5)

    def testAttributeForward(self):
        val  = MMListAttribute(value =  [ "first" , "second" , "third" ] )
        obj  = ObjectProxy()
        #attr = MMAttribute("test",val,obj)
        obj["test"] = val
        attr = obj["test"]
        #Check values from initialisation
        self.assertEqual(attr.count() ,3 )        
        self.assertEqual(six.text_type(attr.__getitem__(1)) , "second" )        
        self.assertEqual(six.text_type(attr[1]) ,"second" )        
        self.assertEqual(six.text_type(attr["1"]) ,"second" )        
        self.assertTrue("second" in attr )
        self.assertEqual(six.text_type(attr["-1"]) ,"third" )
        #Delete and item.
        del attr["1"]
        #Check whats moved.
        # - array should be  ["first", "third"].
        self.assertEqual(attr.count() ,2 )        
        self.assertEqual(len(list(iter(attr))),2)
        self.assertEqual(len(attr),2)
        self.assertFalse("second" in attr )
        self.assertEqual(six.text_type(attr["1"]) ,"third" )
        #Check writeback occurred.
        #XXX
        #obj["test"]=attr
        val = attr.get_value()
        attr_id = attr.get_nodeid()
        #attr = None
        self.assertEqual(system.store.attrs[attr_id],(val.get_type(),val.get_parts()))
        #Test read from store!.
        #attr = obj["test"]
        valo = CreateAttributeValue("primary")
        attr["0"] = valo
        
        # - array should be  ["primary", "third"].
        self.assertEqual(attr.count() ,2 )        
        self.assertEqual(attr[0].get_value(),valo) 
 
        
        #Test Stable key behaviour.
        skey = repr(attr[0]).split(":")[-1]
        self.assertNotEquals(skey,"0")
        self.assertNotEquals(skey,0)
        self.assertEqual(attr[0],attr["0"])
        self.assertEqual(attr[skey],attr[0],msg=("attr[\"%s\"] != attr[0]" % skey))
        skey = repr(attr["1"]).split(":")[-1]
        self.assertNotEquals(skey,"1")
        self.assertNotEquals(skey,1)
        self.assertEqual(attr[skey],attr[1])


        
        
        # Check writeback again
        # - array should be  ["primary", "third"].
        val = copy.copy(obj["test"].get_value())
        # - array should be  ["primary", "second"].
        attr[1]="second"
        val[1]="second"
        self.assertEqual(six.text_type(attr["1"]) ,"second" )        
        self.assertEqual(system.store.attrs[attr_id],(val.get_type(),val.get_parts()))
        #Check walk back thru and find a parser
        self.assertEqual(attr[1].GetFullExpansion(),"second")

        val = copy.copy( obj["test"].get_value())
        # - array should be  ["primary", "second" , "some fate"].
        attr.append("some fate")
        val.append("some fate")
        val._compose(None)
        self.assertEqual(system.store.attrs[attr_id],(val.get_type(),val.get_parts()))
        self.assertEqual(six.text_type(attr["2"]) ,"some fate" )        

        val = copy.copy( obj["test"].get_value())
        attr.insert(2,"some date")
        val.insert(2,"some date")
        val._compose(None)
        # - array should be  ["primary", "second" ,"some date" ,"some fate"].
        self.assertEqual(system.store.attrs[attr_id],(val.get_type(),val.get_parts()))
        self.assertEqual(six.text_type(attr["2"]) ,"some date" )        
        self.assertEqual(six.text_type(attr["3"]) ,"some fate" )        


        #Check trying insert an invalid class.
        class dummy (MMAttributeValue):
            typename = "dummy"
            contain_prefs = {}
         
        def test(a):
            a[2] = dummy(parts = {'f':"testing", 'g':"123"})
                   
        self.assertRaises(TypeError,test,attr)

        ###Test itertation..
        # - note we get back the long term stable keys - not the
        #   numeric indices - so our test needs be different
        # - note we also test return order s correct here,
        names = [ 0,1,2,3 ]
        fndNames= []
        for i,(k,v) in izip_longest(names,attr.iteritems()):
            self.assertEqual(attr[i] , attr[k])
            self.assertEqual(attr[i] ,  v)
            self.assertFalse(k in fndNames)
            fndNames += [ k ]
            self.assertTrue(isinstance( v, MMAttribute))
            self.assertEqual(v,attr[k])

        attrv = list(attr.__iter__())
        self.assertEqual(len(attrv),4)
        attrk = list(attr.iterkeys())
        self.assertEqual(len(attrk),4)

        for k,v in zip(attrk,attrv):
            self.assertEqual(attr[k],v)



    def testNotify(self):
       def testexpect(obj):
            self.exception = None
            try:
                self.assertEqual(six.text_type(obj[-1]) , self.val)
            except Exception as e:
                self.exception =e


       def update(obj):
            update.count+=1
       update.count = 0

       attr  = MMListAttribute(value =  [ "first" , "second" , "third" ] )
       obj  = ObjectProxy()
       obj["list"] = attr
       #keep mandantory ref
       attrobj = obj["list"]
       obj["list"].register_notify(update)
       obj["list"].register_notify(testexpect)
       self.assertEqual(update.count,0)
       count = update.count

       self.val = "diff"
       attrobj.append(self.val)
       self.assertTrue(update.count > count )
       count = update.count
       if self.exception: raise self.exception
        
       self.val ="third" 
       del attrobj[-1]
       self.assertTrue(update.count > count )
       count = update.count
#       self.assertEqual(update.count,3)
       if self.exception: raise self.exception

       attrobj.unregister_notify(update)
       self.val ="baz" 
       attrobj.append(self.val)
       self.assertEqual(update.count,count)
       if self.exception: raise self.exception
       attrobj.unregister_notify(testexpect)


    def testValueCopy(self):
        #Test appending to a non-emptylist
        val  = MMListAttribute(value =  [ "first" , "second" , "third" ] )
        obj  = ObjectProxy()
        obj["list"] = val
        obj["text"] = "some text"
        #Check values from initialisation
        self.assertEqual(obj["list"].count() ,3 )   
        obj["list"][2] = obj["text"]
        obj["list"].append( obj["text"])
        self.assertEqual(six.text_type(obj["list"][0]) ,"first" )   
        self.assertEqual(six.text_type(obj["list"][1]) , "second" )   
        self.assertEqual(six.text_type(obj["list"][2]) , "some text" )   
        self.assertEqual(six.text_type(obj["list"][3]) , "some text" )   

        #Test appending to an empty list
        val2  = MMListAttribute(value =  [ ] )
        obj["l2"] = val2
        obj["l2"].append(obj["text"])
        self.assertEqual(six.text_type(obj["l2"][0]) ,"some text" )   
        

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
        for i in range(3):
            a = b
            while len(str(a)) >= len(str(b)):
                c = b
                b = b.next()
                vallist.append(b)
                self.assertTrue(str(b) > str(c))
        
        ## Check between creates useful values.
        for ele1,ele2 in zip(vallist,vallist[1:]):
            b = ele2
            a = ele1
            for i in range(4):
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

