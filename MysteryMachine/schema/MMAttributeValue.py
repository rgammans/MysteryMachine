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
from MysteryMachine.parsetools.grammar import Grammar

import logging
import exceptions
import sys
import types
import operator
import copy

AttrTypes = dict()
TypeLookup = dict()

#FIXME make a __new__ method.
def CreateAttributeValue(val):
    """
    """
    global AttrTypes
       
    
    if not isinstance(val,MMAttributeValue):
        #Decide on type to use and create object.
        vtype = FindBestValueType(type(val))
        val = vtype([val])
    else:
        print "CAV2:type:%s\n" % val.__class__.typename
        print "CAV2:parts:%s\n" % val.parts
        val= copy.copy(val)

    return val


def MakeAttributeValue(type,parts):
   cls = AttrTypes[type]
   return cls(parts)
                              
 
def register_value_type(name,acls,nativelist):
    """
    """
    global AttrTypes    
    AttrTypes[name]=acls
    sys.stderr.write("natvie typs->"+str( nativelist )+"\n")
    for typenm in nativelist.keys():
        priority=nativelist[typenm]
        if typenm not in TypeLookup:
            TypeLookup[typenm] = list()
        TypeLookup[typenm].append( (acls, priority) )


def FindBestValueType(atype):
    """
    """
    #Handle base class and more sets in the key. 
    return (sorted(TypeLookup[atype],key=operator.itemgetter(1)))[0][0]


class _AttrMeta(type):
   def __init__( self, name , bases, ns):
        super( _AttrMeta , self).__init__(name,bases,ns)
        if name != "MMAttributeValue":
            register_value_type(self.typename,self,self.contain_prefs)
    
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
    print "raw-->%s<--" % result
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
        if isinstance(other,MMAttributeValue):
            if self.__class__ is other.__class__:
                self.parts =  other.parts        
            else:
                raise TypeError()
        else:
            #TODO Clever code here to handle appropriate value
            # setting.
            pass
    
    def __copy__(self):
        return self.__class__(self.parts)




class MMAttributePart (object):
    """
    Simple implementation of attribute parts. Uses incore storage
    only.

    This is sufficent to create and handle parts and attributes which
    haven't been 'seved' or set on an object. But it must commonly
    used for overidding in different storage models
    """
    def __init__(self,pname,value):
        self.value=value
        self.partname=pname
    def __repr__(self):
        return "MMAttributePart(\""+repr(self.value)+"\")"
    def get_name(self):
        return self.partname
    def get_value(self):
        return self.value
    def set_value(self,val):
        self.value=val
    def __eq__(self,other):
        return self.value == other.value and self.partname == other.partname


class MMAttributeValue_BasicText(MMAttributeValue):
    """
    A single Macro part value type.

    This type is appropriate for String values less than approximately
    one line in size.
    """
    typename      = "simple"
    #Should be basestring really - but that needs baseclass support.
    contain_prefs = { str: 100 }


    def __init__(self,*args,**kwargs):
        MMAttributeValue.__init__(self,*args,**kwargs)
        part=self.parts[0]
        if not isinstance(part,MMAttributePart):
            part = MMAttributePart("",part)
        self.parts = [ part ] 
