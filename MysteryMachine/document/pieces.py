#!/usr/bin/env python
#               sections.py - Copyright Roger Gammans
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
#
#

"""
This module contains AtttributeValue class for document pattern pieces.

"""

from MysteryMachine.schema.MMAttributeValue import MMAttributeValue
import re
import six

class piece(MMAttributeValue):
    typename = "piecebase"
    contain_prefs = {}
    def __init__(self,*args,**kwargs):
        super(piece,self).__init__(*args,**kwargs)
        self.exports += [ "needs_pop" , "needs_push"  ]

    def needs_pop(self, obj = None):
        return False

    def needs_push(self, obj= None ):
        """
        Return the index of the result node to be used on the stack
        """
        return None 

    def _encode_raw(self, txt, obj = None):
        encoding = 'utf-8'
        if obj is not None:
            encoding = obj.get_root().get_encoding()

        return six.text_type(txt,encoding)

    def get_raw_rst(self,obj = None):
        return self._encode_raw(self.get_raw(obj))


_rst_lvl_adorns = [ '=', '-' ,'#' , '\'' , '"' ]
def _maketitle(txt,lvl = 0):
    """
    Make an RST Title of level lvl withthe title txt
    """
    return "\n\n%s\n%s\n\n" % ( txt , len(txt) * _rst_lvl_adorns[lvl] )

class title(piece):
    """
    This is a document piece which creates a title from it's content.
    it should leave the document in a new section.
    """
    typename = "doctitle"
    contain_prefs = { str: 0}
    def get_raw(self,obj = None):
        content  = b" ".join(self.parts.values())
        return content

    def get_raw_rst(self, obj = None):
        content = super(title,self).get_raw_rst()
        # Replace newlines with spaces (title in rst
        # can't span lines).
        newln=re.compile("\n")
        content=re.sub(newln," ",content)
        content=content.rstrip()

        content= _maketitle(content) 
        return content

    def needs_push(self,obj = None):
        return 0 


class section_end(piece):
    contain_prefs = { str: 0 , None: 0}
    typename = "docpop"
    def needs_pop(self,obj = None):    
        return True


class section(piece):
    contain_prefs = { str: 0 , None: 0}
    typename = "docsection"
    
    def get_raw_rst(self ,obj = None):
        txt = _maketitle(self._encode_raw(self.parts["title"], obj))
        txt += self._encode_raw(self.parts["body"],obj)
        return txt

