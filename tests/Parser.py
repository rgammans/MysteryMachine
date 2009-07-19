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

import MysteryMachine.schema.MMAttributeValue
import unittest


class SystemProxy(dict_store):
    def __init__(self,name):
        dict_store.__init__(self,self)
        self.objmap = dict()
        LoadSystem(name,self)
        self.name = name

    def get_object(self,cat,id,**kwargs):
        path = cat +":"+id
        if not self.HasCategory(cat):
            self.NewCategory(cat,None)
        if not path in self.objmap:
            self.objmap[path]=self.NewObject(cat,None)
        obj =  self.GetObject(cat+":"+self.objmap[path])
        for k,v in kwargs.items():
            obj[k]=v
        return obj

    def __repr__(self):
        return self.name

class ParsersTests(unittest.TestCase):
    def setUp(self):
        StartApp(["--cfgengine=pyConfigDict", "--cfgfile=test.cfg", "--testmode"]) 
        self.sys=SystemProxy("test")
        self.p=self.sys.get_object("template","1")
        self.p[".defname"] = ":mm:`:name`"
        self.i=self.sys.get_object("Item","1", name="The one ring")
        self.i.set_parent(self.p)
        self.c=self.sys.get_object("Character","1", name="Frodo", carries=self.i)
        self.c.set_parent(self.p)
        
 
    def testParser(self):
        print "attr -> %s" % self.c["carries"]
        self.assertEquals(self.c["carries"].GetFullExpansion(),"The one ring")

def getTestNames():
    	return [ 'Parser.ParserTests' ] 

if __name__ == '__main__':
    unittest.main()

