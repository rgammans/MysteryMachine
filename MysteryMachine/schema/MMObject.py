#!/usr/bin/env python
#   			MMObject.py - Copyright roger
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
# The original location of this file is /home/roger/sources/MysteryMachine/generated/MMObject.py
#
#

from MMBase import *
from MysteryMachine.parsetools.MMParser import MMParser , Grammar
from MysteryMachine.schema.MMAttribute import * 
from MysteryMachine.schema.MMAttributeValue import  * 

import weakref
import logging

class MMObject (MMBase):

  """
   This class represents an object in an MMSystem, each object exists in a category
   which reflects it base prototype. An object has a parent from which it inherits
   default values.

  :version:
  :author:
  "schema"

  ATTRIBUTES


  AttribCache  (private)

   A pointer to the base location for this object in the backing store.

  store_uri  (private)


  system  (private)

  """

  def __init__(self, id,parent,store):
    """
     Get an object handle on an existing object with id.

    @param string id : 
    @return  :
    @author
    """
    MMBase.__init__(self)
#    self.logger.debug( "Creating %s" % id)
    self.id = id
    #Ensure strong ref to parent.
    self.parent = parent.getSelf()
    self.store = store
    self.parser = MMParser(self)
    self.cache = weakref.WeakValueDictionary()    
    self.logger = logging.getLogger("MysteryMachine.schema.MMObject")

  def _get_mm_attribute(self,attrn):
     try:
         a = self.cache[attrn]
     except KeyError: 
         attrval = self.store.GetAttribute(attrn)
         if attrval is None:
            raise KeyError(attrn)
         else:
            t,p = attrval
         a = MMAttribute(attrn,MakeAttributeValue(t,p),self)
         self.cache[attrn]= a
     return a
    
  def __getitem__(self, attrname):
    """
    Basic get item handling. Returns 'attribute' of attrname.
    ( I mean MMAttribute here not python attribute). 

    @param string attribute : 
    @return MMAttribute :
    @author
    """
    #TODO Detect deleted attributes?
    if self.store.HasAttribute(attrname):
        return self._get_mm_attribute(attrname) 
    else:
        try:
            parent = self.get_parent()
        except KeyError:
            #No Parent so reraise as no attrname.
            raise KeyError(attrname)
        return parent[attrname]

    #Haven't found looked for attribute.
    #raise KeyError()

  def __setitem__(self, attrname, attrvalue):
    """
    Implements the basic setting ode for attributes.

    @param string attribute : 
    @param MMAttribute value : 
    @return  :
    @author
    """

    #Don't store None values.
    if attrvalue is None:
        del self[attrname] 
        return

    #Deal only with any value part of an existing attribute.
    # TODO - decide if this is really what want to do - or would
    # this create a reference.
    if isinstance(attrvalue,MMAttribute):
        attrvalue=attrvalue.get_value()

    #Fetch exists attribute if any to preserve value type.
    if attrname in self:
        val=self[attrname]
        if val is not None:
            if val.get_owner() is not self:
                val=val.copy(self,attrname)
            val.set_value(attrvalue)
    else:
        #No existing attr create a new one
        val = MMAttribute(attrname,attrvalue,self)
    
    #Get AttributeValue type object - so it is ready for the storage engine.
    attrvalue = val.get_value()
    #Write back to store engine
    self.cache[attrname] = val
    self.store.SetAttribute(attrname,attrvalue.get_type(),attrvalue.get_parts())    

  def __delitem__(self, attrname):
    """
    Ovveride this if you've overridden setattr

    @param string attribute : 
    @return  :
    @author
    """
    #
    #FIXME - Mark as destoryed in case references exist.
    # - we can do this by pulling the ref out of the cache.
    
    #Remove from cache - ignore not finding it.
    try:
        del self.cache[attrname]
    except KeyError: pass
    #Remove from backing store. 
    if self.store.HasAttribute(attrname):
        self.store.DelAttribute(attrname)    
  
  def __iter__(self):
        for a in self.store.EnumAttributes():
            if a[0] != '.': yield a

  def __contains__(self,name):
       a = self.store.HasAttribute(name) 
       self.logger.debug( "** %s does %s exist** ", name , ("" if a else "not"))
       return a

  def _validate(self):
    """

    @return bool :
    @author
    """
    pass

  def get_parent(self):
    """

    @param string attribute : 
    @return string[*] :
    @author
    """
    #Bypass inheritance lookup.
    parent = self._get_mm_attribute(".parent") 
    self.logger.debug( "parent type is %s " %type(parent))
    self.logger.debug( "Parent = %r" % parent)
    if parent != None:
        parent = parent.get_object()
    return parent

  def set_parent(self,parent):
    #We can safely use the basic code to set the parent as it
    #  only uses any inheirted values as a type hint.
    self[".parent"]=parent

  def __str__(self):
    # def name attribute contains the instructions for a human
    # readable interpreation of this object. Normally "mm:`:name`"
    name = str(self[".defname"])
    return self.parser.GetString(name,repr(self))

  def __repr__(self):
    """
    Return the internal object name
    """
    return self.id


class MMAttributeValue_MMObjectRef(MMAttributeValue):
    """
    """
    typename = "objectref"
    contain_prefs = { MMObject: 100 }

    def __init__(self,*args,**kwargs):
        super(MMAttributeValue_MMObjectRef, self).__init__(*args,**kwargs)
        if isinstance(self.value,MMObject):
            #Get string represenation of the object.
            #TODO Store object here so it cached.
            self.parts['obj'] = repr(self.value)
        
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
  #      self.logger.debug( "refobj->%s<--" % attr)
        pstr = self.get_raw(attr)
        self.logger.debug( "MMA-O:go:pstr  ->%s<--" % pstr)
        objref = Grammar(attr).parseString(pstr)[0]
  #      self.logger.debug( "ret = %s, class = %s" % (objref , objref.__class__ ))
        return objref

    def get_raw_rst(self,obj = None):
        return ":mm:`"+ self.get_raw(obj) + "`"
