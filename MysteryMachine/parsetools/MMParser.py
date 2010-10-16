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
import docutils.nodes

from grammar import Grammar

from MysteryMachine.schema.MMBase import  MMBase

import re
from exceptions import *    

import logging
modlogger   = logging.getLogger("MysteryMachine.parsetools.MMParser")

import threading
class _stack(threading.local):
	def __init__(self):
		self.stack = [ ]
	def pop(self):
		value = self.stack[0]
		self.stack = self.stack[1:]
	def push(self,value):
		self.stack = [ value ] + self.stack

	def peek(self):
		return self.stack[0]

docutils_stack = _stack()

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
        self.logger   = logging.getLogger("MysteryMachine.parsetools.MMParser")
#        self.publisher= MMPublisher(obj)

  def evaluate(self,expr):
        self.logger.debug( "\n--evaling--\n%s\n----\n" % expr)
        value=self.grammar.parseString(expr) 
        self.logger.debug( "Parsed as->%s" % repr(value))
        newval=value[0]
        for part in value[1:]:
            newval = newval + part
        self.logger.debug( "\--evalled to --\n%s\n----\n" % newval.__repr__() )
        return newval

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

    #Disabled to make source paths more readable now we
    # don't need to find the global system..
    #src = repr(self.myobject.owner)+":"+src
   
    self.logger.debug( "processed src-> %s" % src)
    self.logger.debug( "raw+IN->%s<-" % rst_string)

    docutils_stack.push( [ self.myobject ,  src_stack ] )
    result =   publish_doctree(rst_string,source_path=src,
                               settings_overrides=MMParser.du_defaults
               
                )

    docutils_stack.pop() 
    self.logger.debug( "pnodelist-->%s<-" % result)
    
    try:
        source = result[0]
        source = source.source
    except:
        self.logger.info("Can't resolve docutils to find source, using src") 
        source = src
    self.logger.debug( "source[ => %s" % source)
    
    #Strip  document header and main containing paragraph.
    # so we get a simple result.
    result =   result.children 
    #self.logger.debug( "nodelist-->%s<-" % result)
    if len(result) ==1:
        self.logger.debug( "MMP-PRST: class is %s" % str(result[0].__class__))
        if result[0].__class__  == docutils.nodes.paragraph:
             result = result[0].children
    #Update source attrib in node.
    for docnode in result:
        if not source in docnode:
           docnode.source=source
    #self.logger.debug( "nodelist-->%s<-" % str(result))
    #self.logger.debug( "String[0]->%s<" % str(result[0]))
    return result
   
  def GetString(self,rst_string,src="unknown",src_stack=[]):
    #FIXME: THis is incredibly niave - we really need to use a rst 
    #       writer here.
    nodes = self.ProcessRawRst(rst_string,src,src_stack)
    result = ""
    for n in nodes:
      result += str(n)
    self.logger.debug( "String->'%s',len %s"  % (result ,len(nodes)))
    if len(nodes) == 1:
      #Supress outer xml container.
      result =re.sub("<(\w+)>([^>]*)</\\1>","\\2",result)
    self.logger.debug( "string->%s<-" %result)
    return result
 
def role_handler(role, rawtext, text, lineno, inliner,
           options={}, content=[] ):
    msg   = []
    nodes = []

    modlogger.debug( "role handler (%s)" % text)
    modlogger.debug( "role-options:%s"%str(options))
    modlogger.debug( "role-content:%s"%str(content))

    sframe = docutils_stack.peek()
    mainobj = sframe[0]
    content = sframe[1]

    if mainobj == None:
        msg += [ inliner.reporter.error("Parser cannot find context for role") ]
    else:
        #Check for cycles in expansion
        if not text in content:
             try:
                current_parser = mainobj.parser
                rst    = current_parser.evaluate(text)

                #rst can be a string if text eval's to a literal value
                # but if it's a schema object need to use it's context
                # not our own.
                if isinstance(rst,MMBase):
                    current_parser = _findParser(rst)
                
                #Return to docutils to get docutils node representation.
                nodes += current_parser.ProcessRawRst(str(rst),src = repr(rst) ,
                                                      src_stack=content + [ text ] )
             except:
                import traceback
                import sys
                e_info = sys.exc_info()
                modlogger.debug( traceback.format_exc() )
                msg +=  docutils.nodes.error(traceback.format_exception_only(e_info[0],e_info[1]))
        else:
            msg.append(inliner.reporter.error("Cycle detected in macro expansion '%s' via:-%s\n" % 
                      (text,"\n".join(content))))
    #modlogger.debug("%s %s",  str(nodes),str(msg))
    return nodes ,msg

def _findParser(obj):
	while not hasattr(obj,"parser"):
		obj = obj.owner
	return obj.parser


roles.register_canonical_role('mm',role_handler)
roles.register_local_role('mm',role_handler)

