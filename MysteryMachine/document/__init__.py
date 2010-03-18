#!/usr/bin/env python
#   			document/__init__.py - Copyright R Gammans
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

import docutils.utils
from docutils.frontend import OptionParser
from docutils.parsers.rst import Parser

from MysteryMachine.parsetools.MMParser import MMParser

import pieces 

def generate_doctree(pattern,home):
    """
    Generate a document from tree the pattern object using home as 
    the master object.

    A pattern object should consist of a order attribute, and 
    and a set of pattern pieces.
    """
    order = pattern[".order"]
    
    parser = home.get_parser()
    settings = OptionParser(components=(Parser,)).get_default_values()
    #FIXME _ Get mystery machine settings and merge.
    doc = docutils.utils.new_document(repr(home),settings)    

    section_stack = [ doc ]
    for pos , attrib in order:
        element = attrib.getSelf()
        #We have a problem here - 
        #  an element can impose a section push/pop
        elenodes = parser.ProcessRawRst(element.get_raw())
        section_stack[-1] += elenodes
        # We check the existance of needs_push & needs_pop
        # as this means we can have standard attributes in the
        # pattern.
        if hasattr(element,"needs_push") and element.needs_push() is not None:
           section_stack += [ elenodes[ element.needs_push() ] ] 

        if hasattr(element,"needs_pop") and  element.needs_pop(): 
           section_stack = section_stack[:-1]        

    return doc
