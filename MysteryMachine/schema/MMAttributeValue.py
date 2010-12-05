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

from __future__ import with_statement

import sys

from MMBase import *
from MysteryMachine.parsetools.grammar import Grammar

import logging
import exceptions
import sys
import types
import operator
import copy as _copy


AttrTypes = dict()
TypeLookup = dict()

modlogger = logging.getLogger("MysteryMachine.schema.MMAttributeValue")

ATTRIBUTE_MMTYPE_EXPOINTNAME= "AttributeValueMMType"
ATTRIBUTE_PYTYPE_EXPOINTNAME= "AttributeValuePyType"

#FIXME make a __new__ method.
def CreateAttributeValue(val, copy = True):
    """
    Create an appropriate MMAttributeValue to store val.


    This searches through the registered types to find the most preferred
    MMAttributeValue class to store and value of type(val).

    If a MMAttributeClass is pass as val a copy is created and returned,
    unless copy=False , in which case val is returned.
    """
    if not isinstance(val,MMAttributeValue):
        #Decide on type to use and create object.
        vtype = FindBestValueType(type(val))
        val = vtype(value =val)
    else:
        modlogger.debug( "CAV2:type:%s" % val.__class__.typename)
        modlogger.debug( "CAV2:parts:%s" % val.parts)
        if copy: val= _copy.copy(val)
        modlogger.debug( "CAV2:newparts:%s" % val.parts)

    return val


def GetClassForType(typename):
    if not hasattr(AttrTypes,typename):
        from MysteryMachine import StartApp
        with StartApp() as ctx:
            possible_plugins = ctx.GetExtLib().findPluginByFeature(ATTRIBUTE_MMTYPE_EXPOINTNAME,typename)
            ##TODO Sort plugins by preference
            for plugin in possible_plugins:
                ctx.GetExtLib().loadPlugin(plugin)
                #Just load one module to handle the type.
                if hasattr(AttrTypes,typename): break
              
    return AttrTypes[typename]

def MakeAttributeValue(type,parts):
   cls = GetClassForType(type)
   return cls(parts = parts)
                              
 
def register_value_type(name,acls,nativelist):
    """
    """
    global AttrTypes    
    AttrTypes[name]=acls
    modlogger.debug("native types %s -> %s",str( nativelist ),acls)
    for typenm in nativelist.keys():
        priority=nativelist[typenm]
        if typenm not in TypeLookup:
            TypeLookup[typenm] = list()
        TypeLookup[typenm].append( (acls, priority) )


def FindBestValueType(atype):
    """
    """
    #Handle base class and more sets in the key get a list 
    # of classes to use for candidate handlers. 
    candidates = list()
    try:
        typelist = atype.__mro__
    except:
        typelist = list(atype)


    #Collect the handlers for the functions.
    for t in typelist:
        if t in TypeLookup:
            candidates += TypeLookup[t]
   

    if len(candidates) == 0:
        from MysteryMachine import StartApp
        with StartApp() as ctx:
            possible_plugins = ctx.GetExtLib().findPluginByFeature(ATTRIBUTE_PYTYPE_EXPOINTNAME,atype.__name__)
            for plugin in possible_plugins:
                ctx.GetExtLib().loadPlugin(plugin)

                #Just load one module to handle the type.
 
        #Collect the handlers for the functions (again).
        for t in typelist:
            if t in TypeLookup:
                candidates += TypeLookup[t]

    modlogger.debug("candiate attrval's %s" % candidates)
    rlist = sorted(candidates,key=operator.itemgetter(1),
                    reverse= True )
    
    if len(rlist) == 0: raise TypeError("No schema type for %s" % atype)
    return rlist[0][0]


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

   An attribute value must consist of one or more string parts, each part should
   have a unique name in the MysteryMachine namespace.

  :version:
  :author:
  """

  """ ATTRIBUTES
  base  (private)
  attr  (private)
  """
    
  __metaclass__ = _AttrMeta

  def __init__(self,*args, **kwargs):
    self.parts = {} 
    self.value = None
    if 'parts' in kwargs:
        self.parts=kwargs['parts']
        partsmap = { }
        for k in self.parts.iterkeys():
            #Check k is valid - will throw if not.
            newk = self.canonicalise(k)
            if k != newk:
                partsmap[k] = self.canonicalise(k)
                if newk in self.parts: raise ValueError("%s and %s conflict" % (k ,newk))
            
        for oldkey , newkey in partsmap.iteritems():
            self.parts[newkey] = self.parts[oldkey]
            del self.parts[oldkey]
  
    if 'value' in kwargs:
        self.value=kwargs['value']

    self.exports=[ "get_raw", "get_raw_rst" ]
    self.logger = logging.getLogger("MysteryMachine.schema.MMAttributeValue")

  def __repr__(self):
    """

    @return string :
    @author
    """
    return str(self.__class__)+"(\""+self.get_raw()+"\")"


  def __str__(self):
    return self.get_raw()

  def get_raw(self, obj = None):
    """
    Gets unprocessed rst contents of attribute.       

    @return string :
    @author
    """
    self.logger.debug( str(self.__class__))
    self.logger.debug( self.parts)
    result = "\n".join([x[1] for x in  sorted(self.parts.items())])
    self.logger.debug( "raw-->%s<--" % result)
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
    @authorMysteryMachine/schema/MMAttribute.py:
    """
    ok = True
    #Test we can parse succesfully, and valid part naems but no more.
    try:
        for k in self.parts.iterkeys():
            if k != self.canonicalise(k):
                ok = False
                #exit early
                return ok

        if attr is None:
            grammar.parse(self.get_raw_rst())
        else:
            attr.owner.parser.ProcessRawRst(self.get_raw_rst())
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
         # setting. Raise error while unimplemented. 
         raise TypeError()
    
  def __copy__(self):
     self.logger.debug( "AV_c:Entered")
     return self.__class__(parts = _copy.copy(self.parts))


  def __eq__(self,other):
     if not isinstance(other,MMAttributeValue): return False 
     return self.get_type() == other.get_type() and self.get_parts() == other.get_parts()

  def __hash__(self):
     #FIXME: Identical valued but distict obj return the same hash
     return hash(["MMAttributeVal" , self.get_type() , self.get_parts()])

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
        #Get passed in value.
        if self.value is not None:
            self.parts["txt"] = str(self.value)


class MMAttributeValue_MMRef(MMAttributeValue):
    """
    This Value typeobjct store reference to other
    attributes or objects insidea MMObject system.
    """
    typename = "ref"
    contain_prefs = { MMBase: 50 }

    def __init__(self,*args,**kwargs):
        super(MMAttributeValue_MMRef, self).__init__(*args,**kwargs)
        if isinstance(self.value,MMBase):
            #Get string represenation of the object.
            #TODO Store object here so it cached.
            self.parts['obj'] = repr(self.value)
            
            self.logger.debug( "MMA-O:init->%s<--" % self.parts['obj'])
        if not self._validate(): raise Error()    
        #All ok.
        self.exports += [ "get_object" ]

    def _validate(self, obj = None):
        objref = None
        #try:
        objref = self.get_object( obj )
        #except exceptions.Exception , e:
        #    logging.warn(e.msg())
        #    objref = None
        return not objref is None

    def get_object(self, obj = None ):
        """
        This method may raise and exception if the
        own_obj is not valid or the value will not validate.
        """
        ##TODO Consider caching the return result.
  #      self.logger.debug( "refobj->%s<--" % attr)
        pstr = self.get_raw(obj)
        self.logger.debug( "MMA-O:go:pstr  ->%s<--" % pstr)
        objref = Grammar(obj).parseString(pstr)[0]
  #      self.logger.debug( "ret = %s, class = %s" % (objref , objref.__class__ ))
        return objref

    def get_raw_rst(self,obj = None):
        return ":mm:`"+ self.get_raw(obj) + "`"




class ShadowAttributeValue(MMAttributeValue):
    
    """
    This class is a place holder value for inherited attributes.

    We need to create an MMAttribute object for those object so that 
    they are always evaluated in the correct context , however they cannot
    share the value object as that has a hard to fix failure mode when
    the inherited value is updated. If the update creates a new value object
    any inherited attributes do not piclk up the new value as they are still
    pointing at the old value.

    This class is designed to fix that problem by handling the forwarding directly.

    Note that the class only hold a reference to it's owning object as that
    means it doens't impact on the GC at all.
    """

    typename = ".inhertitance_shadow"
    contain_prefs = { }

    def __init__(self,*args,**kwargs):
        super(ShadowAttributeValue, self).__init__(*args,**kwargs)
        self.obj       = kwargs.get("object",None)
        self.attrname  = kwargs.get("attrname","")
        self.exports   = self._get_target().exports
        self.logger    = logging.getLogger("MysteryMachine.schema.MMAttributeValue.ShadowAV")
        #self.logger.setLevel(logging.DEBUG)
        self.logger.debug("Created forward for %s[%s] " % ( repr(self.obj), self.attrname) )

    def __getattr__(self,attrname):
        self.logger.debug(attrname)
        fwd_to = getattr(self._get_target(),attrname)
        return fwd_to

    def _get_target(self):
        p = self._get_parent()
        t = p[self.attrname]
        return t.get_value()

    def _get_parent(self):
        p = self.obj.get_parent()
        return p 
        

    def __copy__(self):
        #return a copy of the object we are proxying - it want you really want 
        #anyway
        return _copy.copy(self._get_target())

    def __str__(self):
        return self._get_target().__str__()
        
    def get_raw_rst(self, obj = None):
        self.logger.debug("%s[%s].raw_rst ( obj = %s ) "% (  repr(self.obj), self.attrname , repr(obj) ))
        return self._get_target().get_raw_rst(obj)


    def get_raw(self, obj = None):
        return self._get_target().get_raw(obj)

    def get_parts(self):
        return self._get_target().get_parts()

    def get_type(self):
        return self._get_target().get_type()
