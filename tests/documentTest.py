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
Tests for the Mystery Machine document module
"""

from MysteryMachine import *
import MysteryMachine.schema.MMListAttribute
import MysteryMachine.store.dict_store
import MysteryMachine.document as document

import docutils.nodes

import unittest

class docTest(unittest.TestCase):
    def setUp(self):
        self.app = StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"]).__enter__()
 
        self.s=self.app.CreateNew(scheme="dict")
        self.s.NewCategory("character")
        self.s.NewCategory("docs")

    def tearDown(self,):
        self.app.close()

    def test1(self):
        c1     = self.s.NewObject("character")
        c1["name"]    = "Freddie Bloggs"
        c1[".defname"]= ":mm:`:name`"

        csheet = self.s.NewObject("docs")
        csheet["title"] = document.pieces.title(parts ={"1":":mm:`:name`"})
        csheet[".order"] = [ csheet["title"].getRef()  , ]
        #self.assertEquals(str(document.generate_doctree(csheet,c1)),
        #                 "<document source=\"character:1\">Fred Bloggs</document>")
        doc = document.generate_doctree(csheet,c1)
        #print doc
        #FIXME - Find out why this doesn't work (its a test problem not a CUT problem).
        #self.assertEquals(doc.source,repr(c1))
        self.assertEquals(len(doc),1)                           #Has one 
        self.assertEquals(type(doc[0]),docutils.nodes.section)   #section
        self.assertEquals(len(doc[0]),1)                        #which contains one
        self.assertEquals(type(doc[0][0]),docutils.nodes.title) #title
        self.assertEquals(type(doc[0][0][0]),docutils.nodes.Text) #title
        self.assertEquals(doc[0][0][0],"Freddie Bloggs") #title

        c1["background"]="""

You find life boring . You don't have a backgound. Piss about and 
have fun.

        """
        csheet["background"] = document.pieces.section(parts = { "title":"Background", "body":":mm:`:background`" })
        csheet[".order"] = [ csheet["title"].getRef()  , csheet["background"].getRef() ]
        doc = document.generate_doctree(csheet,c1)
        self.assertEquals(len(doc),1)                           #Has one 
        self.assertEquals(type(doc[0]),docutils.nodes.section)   #section
        self.assertEquals(len(doc[0]),2)                        #which contains two elements 
        self.assertEquals(type(doc[0][0]),docutils.nodes.title) #a title
        self.assertEquals(type(doc[0][0][0]),docutils.nodes.Text) #of text
        self.assertEquals(doc[0][0][0],"Freddie Bloggs") #title
        self.assertEquals(type(doc[0][1]),docutils.nodes.section) #and a section
        self.assertEquals(len(doc[0][1]),2)              # contain again 2 elements
        self.assertEquals(type(doc[0][1][0]),docutils.nodes.title) #a title
        self.assertEquals(type(doc[0][1][1]),docutils.nodes.paragraph) #and a paragraph
        self.assertEquals(len(doc[0][1][1]),1) #and a paragraph contain a single piece of
        self.assertEquals(type(doc[0][1][1][0]),docutils.nodes.Text) # Text
        self.assertEquals(str(doc[0][1][1][0]),"You find life boring . You don't have a backgound. Piss about and\nhave fun.")



if __name__ == '__main__':
    unittest.main()
    
