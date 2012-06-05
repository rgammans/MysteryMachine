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
from MysteryMachine.schema.MMObject import * 
import unittest
from MysteryMachine import * 
from functools import partial


from mock.schema_top import *

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
        super(ObjectProxy,self).__init__(l[0] + ":" + l[1] , SystemProxy() ,None )
        self.items = {}
        for key in kwargs:
           self.items[key] = kwargs[key] 
    def __str__(self):
        return self.name
    def get_root(self):
        return SystemProxy()
    def __eq__(self,other):
        #Fake - equals as required for this test.
        return self.name


class SystemProxy(fakeParent): 
    """A slight more advanced mock system"""
    def get_object(self,cat,id):
        return ObjectProxy(cat , id)
    def getSelf(self):
        return self

    
class attribValTest(unittest.TestCase):
    def setUp(self):
       StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"]) 
       self.objA=ObjectProxy("Proxy", "1", name="TestName",title="A Title")
       self.objB=ObjectProxy("Proxy", "2", name="WrongName",title="A Title")
    
    def testUnderInit(self):
       val=MMAttributeValue(parts = {"1":"test","2":"this"})
       self.assertEqual(val.get_raw_rst(),"test\nthis")
       self.assertEqual(len(val.get_parts()),2)




    def testObjRef(self):
        self.makeRef()
        self.assertEqual(self.objrefA.get_object(self.objA) , self.objA )
        self.assertEqual(self.objrefB.get_object(self.objA) , self.objB )

    def makeRef(self):
        self.objrefA = MMAttributeValue_MMRef( value = self.objA )
        self.objrefB = MMAttributeValue_MMRef( value = self.objB )        
 

    def testCreate(self):
        """
        Test CreateAttributeValue entry point
        """
        notsillycalled =  [0]
        dummy  = [0]
        dummy2  = [0]
        def sillym(sillycalled,**kwargs):
            sillycalled[0]=1
            return kwargs['value']

        class NotSilly(str):
            pass

        #Test type lookup etc.
        register_value_type("nsilly",partial(sillym,notsillycalled) , { NotSilly:200, str:50  })
        register_value_type("silly",partial(sillym,dummy) , { NotSilly:100  })
        register_value_type("silly2",partial(sillym,dummy2) , { NotSilly:150  })
        self.assertEquals(CreateAttributeValue(NotSilly("xyzzy")),NotSilly("xyzzy"))
        self.assertNotEquals(dummy[0],1)
        self.assertNotEquals(dummy2[0],1)
        self.assertEquals(notsillycalled[0],1)
 
        #Value copy operation
        val=MMAttributeValue_BasicText(value = "test")
        val2 = CreateAttributeValue(val)
        self.assertEquals(val, val2)
        self.assertFalse(val is val2)
        
        #ValueCreate with copy=false
        val3 = CreateAttributeValue(val,copy = False)
        self.assertEquals(val, val3)
        self.assertTrue(val is val3)



    def testMake(self):
        """
        Test Make AttributeValue entry point
        """        
        
        sillycalled =  [0]
        def sillym(sillycalled,**kwargs):
            sillycalled[0]=1
            return kwargs['parts']
        register_value_type("silly",partial(sillym,sillycalled) , { })
        self.assertEquals(MakeAttributeValue("silly","xyzzy"),"xyzzy")
        self.assertEquals(sillycalled[0],1)


    def testUnicode(self):
        text = u"Some unicode text"
        attr = CreateAttributeValue(text)
        self.assertEquals(attr.get_type(),"simple_utf8")
        self.assertEquals(str(attr),text)


    def testGetAttributeTypes(self):
        attrtypeslist = GetAttributeTypeList()
        self.assertTrue("simple" in attrtypeslist)
        self.assertTrue("ref" in attrtypeslist)
        self.assertTrue(".inheritance_shadow" not in attrtypeslist)
        self.assertTrue("faketype" in attrtypeslist)

    def testNullAttributeType(self):
       attr =  MakeAttributeValue("null",{})
       self.assertEquals(attr.get_object(),None)
       attr =  MakeAttributeValue("null",{'value':""})
       self.assertEquals(attr.get_object(),None)
       attr =  MakeAttributeValue("null",{'value':"sdkasjdlk", 'ref':"more stuff"})
       self.assertEquals(attr.get_object(),None)



 
def getTestNames():
	return [ 'attribValueTest.attribValTest' ] 

if __name__ == '__main__':
    if "--debug" in sys.argv:
        sys.argv.remove("--debug")
        logging.getLogger("MysteryMachine.schema.MMAttributeValue").setLevel(logging.DEBUG)
    unittest.main()

