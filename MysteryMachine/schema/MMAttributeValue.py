#!/usr/bin/env python
#   			MMAttributeValue.py - Copyright roger
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
#    with this program; if not, wrobjectite to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# 
# This file was generated on Mon Feb 2 2009 at 20:18:08
# The original location of this file is /home/roger/sources/MysteryMachine/generated/MMAttributeValue.py
#
#

import sys

from MMBase import *
from MMAttribute import *
from MMObject import MMObject
from MysteryMachine.parsetools.grammar import Grammar

import logging
import exceptions

class _AttrMeta(type):
   def __init__( self, name , bases, ns):
        super( _AttrMeta , self).__init__(name,bases,ns)
        if name != "MMAttributeValue":
            register_value_type(self.typename,self)
    
#FIXME Remove and replace reference to appropriate exception class
class Error():
    pass
        
class MMAttributeValue (MMBase ):
  """
   This is the base class of MMAtributes actual value. Each 'type' of Attribure
   should have it's own speciallisation of this class. It is through this object
   that values are directly manipulated.

  :version:
  :author:
  """

  """ ATTRIBUTES
  base  (private)
  attr  (private)
  """
    
  __metaclass__ = _AttrMeta

  def __init__(self,parts):
    self.parts=parts
    self.exports=[ "get_raw", "get_raw_rst" ]

  def __repr__(self):
    """

    @return string :
    @author
    """
    return str(self.__class__)+"(\""+self.get_raw()+"\")"

  def get_raw(self, obj = None):
    """
    Gets unprocessed rst contents of attribute.       

    @return string :
    @author
    """
    print str(self.__class__)
    print self.parts
    result = "\n".join(map(lambda x:x.get_value(),self.parts))
#    print "raw-->%s<--" % result
    return result

  def get_raw_rst(self, obj = None):
    return self.get_raw(obj)

  def get_parts(self):
    return self.parts

  def get_type(self):
    return self.__class__.typename 
 
  def _validate(self,attr = None):
    """

    @return bool :
    @author
    """
    ok = True
    #Test we can parse succesfully, and no more.
    try:
        if attr is None:
            grammar.parse(self.get_raw_rst())
        else:
            attr.parent.parser.ProcessRawRst(self.get_raw_rst())
    except:
        ok = False
    return ok

    def assign(self,other):
        """
        Handle self=other calls.

        The aim of this is to allow custom cleverness as the
        value are updated. The aim is to be able to find the
        appropriate way of store the change. 
        This is important in the more advanced value types.
        
        Pre: self and other are of the same type. 
        Post:str(self) == str(other) 
        """
        if self.__class__ is other.__class__:
            self.parts =  other.parts        
        else:
            raise TypeError()
    
    def __copy__(self):
        return self.__class__(self.parts)

class MMAttributeValue_BasicText(MMAttributeValue):
    """
    A single Macro part value type.

    This type is appropriate for String values less than approximately
    one line in size.
    """
    typename = "simple"


class MMAttributeValue_MMObjectRef(MMAttributeValue):
    """
    """
    typename = "objectref"

    def __init__(self,parts):
        super(MMAttributeValue_MMObjectRef, self).__init__(parts)
        if len(self.parts) != 1 : raise Error()
        if isinstance(self.parts[0].get_value(),MMObject):
            #Get string represenation of the object.
            self.parts[0] = MMAttributePart(self.parts[0].get_name(),self.parts[0].get_value().__repr__())
        else:
            #TODO handle this case - str is ok anyway
            pass
        if not self._validate(): raise Error()    
        #All ok.
        self.exports += [ "get_object" ]

    def _validate(self, attr = None):
        objref = None
        #try:
        objref = self.get_object( attr )
        #except exceptions.Exception , e:
        #    logging.warn(e.msg())
        #    objref = None
        return not objref is None

    def get_object(self, attr = None ):
        """
        This method may raise and exception if the
        own_obj is not valid or the value will not validate.
        """
        ##TODO Consider caching the return result.
  #      print "refobj->%s<--" % attr
        pstr = self.get_raw(attr)
        print "pstr  ->%s<--" % pstr
        objref = Grammar(attr).parseString(pstr)[0]
  #      print "ret = %s, class = %s" % (objref , objref.__class__ )
        return objref

    def get_raw_rst(self,obj = None):
        return "mm:`"+ self.get_raw(obj) + "`"
