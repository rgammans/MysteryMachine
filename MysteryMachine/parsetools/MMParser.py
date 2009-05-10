#!/usr/bin/env python
#   			MMParser.py - Copyright roger
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
# This file was generated on Mon Feb 2 2009 at 20:18:08
# The original location of this file is /home/roger/sources/MysteryMachine/generated/MMParser.py
#
#

from docutils.core import  publish_doctree, default_description 
from docutils.parsers.rst import roles
from grammar import Grammar

    
class MMParser (object):

  """
   This class handles the macro language which allows references between attributes
   and objects within a MMsystems. The parser resovle references to objects and
   attributes.

  :version:
  :author:
  """

  du_defaults = {'file_insertion_enabled': 0,
              'raw_enabled': 0,
              '_disable_config': 1,
              'doctitle_xform': False}

  def __init__(self,obj):
        self.myobject = obj
        self.grammar  = Grammar(obj)
#        self.publisher= MMPublisher(obj)

  def evaluate(expr):
        print "\n--evaling--\n%s\n----\n" % expr
        value=self.grammar.ExprText.parseString(expr) 
        value=reduce(lambda x,y:x+y,value)
        return value

  def ProcessRawRst(rst_string,src="unknown",src_stack=[]):
    #Define the options and content for the role
    # this defines the system context and expansion stack
    # used to detect cycles.
    #
    # This is a bit ugly and slow - but it is a re-entrant way of
    #  passing context etc, to our interpreted role.
    role_def = ".. role: mm(mm)\n :SystemCntxt:%s\n\n" % src
    role_def+= "\n".join(map(lambda x: " "+x,src_stack))
    role_def+= "\n\n"
    print "\n--Parsing--\n%s\n---\n" % (role_def+rst)
    result =   publish_doctree(role_def+rst,source_path=src,
                               settings_overrides=du_defaults
                               )
    source =   result.source
    #Strip  document header and leading paragraph.
    result =   result.children[1:]
    result =  result[1:]
    if len(result) ==1:
        if str(result[0].__class__)  == "docutils.nodes.paragraph":
             sys.stderr.write("eating para\n")        
             result = result[0].children
    #Update source attrib in node.
    for docnode in result:
        if not source in docnode:
           docnode.source=source
    return result
   

def role_handler(role, rawtext, text, lineno, inliner,
           options={}, content=[] ):
    msg   = []
    nodes = []

    mainobj = options['SystemCntxt']
    if mainobj == None:
        msg += "Parser cannot find context for role"
    else:
        #Check for cycles in expansion
        if not text in content:
             try:
                rst    = mainobj.parser.evalute(text)
                nodes += mainobj.parser.ProcessRawRst(rst,src=text,src_stack=content)
             except (e):
                msg.append(e.msg())
        else:
            msg.append("Cycle detected in macro expansion via:-%s\n" % content.join("\n"))
    return nodes ,msg


#Convert Full object name into actual object.
def ObjectOptionHandler(argument):
    items = argument.split(":")
    sys=GetLoadedSystemByName(items[0])
    if sys != None:
        sys = sys.get_object(items[1]+":"+items[2])     
    return sys

role_handler.options = { 'SystemCntxt' : ObjectOptionHandler,
                        }

role_handler.content = True
roles.register_canonical_role('mm',role_handler)

