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

from MysteryMachine import *

import re
from exceptions import *    


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

  def evaluate(self,expr):
        print "\n--evaling--\n%s\n----\n" % expr
        value=self.grammar.parseString(expr) 
        print "Parsed as->%s" % repr(value)
        value=reduce(lambda x,y:x+y,value)
        print "\n--evalled to --\n%s\n----\n" % value.__repr__() 
        return value

  def ProcessRawRst(self,rst_string,src=None,src_stack=[]):
    #Define the options and content for the role
    # this defines the system context and expansion stack
    # used to detect cycles.
    #
    # This is a bit ugly and slow - but it is a re-entrant way of
    #  passing context etc, to our interpreted role.
    # First - prepent system details to src..
    if src is None:
        src =repr(self.myobject)+":unknown"
    src = repr(self.myobject.parent)+":"+src
    role_def = ".. role:: mm(mm)\n :SystemCntxt: %s\n\n" % src
    role_def+= "\n".join(map(lambda x: " "+x,src_stack))
    role_def+= "\n\n"
    print "processed srd->" , src
    print "raw+IN->%s<-" % rst_string
    print "\n--Parsing--\n%s\n---\n" % (role_def+rst_string)
    result =   publish_doctree(role_def+rst_string,source_path=src,
                               settings_overrides=MMParser.du_defaults
                               )
    source =   result[0].source
    print "pnodelist-->%s<-" % result
    print "source => %s" % source
    #Strip  document header and main containing paragraph.
    result =   result.children
    print "nodelist-->%s<-" % result
    if len(result) ==1:
        if str(result[0].__class__)  == "docutils.nodes.paragraph":
             result = result[0].children
    #Update source attrib in node.
    for docnode in result:
        if not source in docnode:
           docnode.source=source
    print "nodelist-->%s<-" % str(result)
    #print "String[0]->%s<" % str(result[0])
    return result
   
  def GetString(self,rst_string,src="unknown",src_stack=[]):
    #FIXME: THis is incredibly niave - we really need to use a rst 
    #       writer here.
    nodes = self.ProcessRawRst(rst_string,src,src_stack)
    result = ""
    for n in nodes:
      result += str(n)
    print "String->'%s',len %s"  % (result ,len(nodes))
    if len(nodes) == 1:
      #Supress outer xml container.
      result =re.sub("<(\w+)>([^>]*)</\\1>","\\2",result)
    print "string->%s<-" %result
    return result
 
def role_handler(role, rawtext, text, lineno, inliner,
           options={}, content=[] ):
    msg   = []
    nodes = []

    print "role handler (%s)" % text
    print "role-options:%s"%str(options)
    print "role-content:%s"%str(content)

    mainobj = None
    if 'systemcntxt' in options:
        mainobj = options['systemcntxt']
    if mainobj == None:
        msg += [inliner.reporter.error("Parser cannot find context for role") ]
    else:
        #Check for cycles in expansion
        if not text in content:
             #try:
                rst    = mainobj.parser.evaluate(text)
                nodes += mainobj.parser.ProcessRawRst(str(rst),src = repr(rst) ,
                                                      src_stack=content + [ text ] )
             #except Exception , e:
             #   print "Error:%s" % str(e)
             #   msg.append(str(e))
        else:
            msg.append(inliner.reporter.error("Cycle detected in macro expansion via:-%s\n" % content.join("\n")))
    print  nodes,msg
    return nodes ,msg


#Convert Full object name into actual object.
def ObjectOptionHandler(argument):
    items = argument.split(":")
    print "--SysCntxt:role<-%s" % argument
    sys=GetLoadedSystemByName(items[0])
    print repr(sys)
    if sys != None:
        print "--Fetching item (%s,%s)" % (items[1] , items[2])
        sys = sys.get_object(items[1],items[2])     
    return sys

role_handler.options = { 'systemcntxt' : ObjectOptionHandler,
                        }

role_handler.content = True
roles.register_canonical_role('mm',role_handler)
roles.register_local_role('mm',role_handler)

