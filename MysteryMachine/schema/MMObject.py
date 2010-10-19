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

class MMObject (MMAttributeContainer):

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

  def __init__(self, id,owner,store):
    """
     Get an object handle on an existing object with id.

    @param string id : 
    @return  :
    @author
    """
    super(MMObject,self).__init__(self)
#    self.logger.debug( "Creating %s" % id)
    self.name = id
    #Ensure strong ref to owner.
    self.owner = owner.getSelf()
    self.store = store
    self.parser = MMParser(self)
    self.logger = logging.getLogger("MysteryMachine.schema.MMObject")

  def _make_attr(self,name):
      attrval = self.store.GetAttribute(name)
      t,p = attrval
      a = MMAttribute(name,MakeAttributeValue(t,p),self,copy = False )
      return a 
 
  def __getitem__(self, attrname):
    """
    Basic get item handling. Returns 'attribute' of attrname.
    ( I mean MMAttribute here not python attribute). 

    @param string attribute : 
    @return MMAttribute :
    @author
    """
    attrname = self.canonicalise(attrname)

    try:
        return self.cache[attrname]
    except KeyError: pass

    if self.store.HasAttribute(attrname):
        return self._get_item(attrname,self._make_attr,attrname) 
    else:
        parent = self.get_parent()
        if not parent:
           #No Parent so raise no attrname.
           raise KeyError(attrname)
        
        #Ensure the attribute can be fetched - if not parent will
        # raise an exception.
        pattr = parent[attrname]
        attr  = MMAttribute(attrname,ShadowAttributeValue(self,attrname=attrname,object=self),
                            self,copy = False) 
        self.cache[attrname] = attr
        return attr        

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

    attrname = self.canonicalise(attrname)
    #Don't store None values.
    if attrvalue is None:
        del self[attrname] 
        return
    
    attrobj = self._set_item(attrname,attrvalue)
    #Get AttributeValue type object - so it is ready for the storage engine.
    attrvalue = attrobj.get_value()
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
   
    attrname = self.canonicalise(attrname) 
    #Remove from cache 
    self._invalidate_item(attrname)
    #Remove from backing store. 
    if self.store.HasAttribute(attrname):
        self.store.DelAttribute(attrname)    
 
  def iteritems(self):
        for a in self.store.EnumAttributes():
            if a[0] != '.': yield (a ,self[a])  

  def iterkeys(self):
        for a in self.store.EnumAttributes():
            if a[0] != '.': yield a  

  def __iter__(self):
        for a in self.store.EnumAttributes():
            if a[0] != '.': yield self[a]

  itervalues = __iter__

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
    if self.store.HasAttribute(".parent"):
        parent = self._get_item(".parent",self._make_attr,".parent") 
    else: #TODO Get parent from object's category 
        idpath = self.name.split(":")[:-1]
        category = self.owner[idpath[-1]]
        try:
            parent = category[".parent"]
        except KeyError:
            parent = None
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
    return self.name

   
  def get_parser(self):
    return self.parser

