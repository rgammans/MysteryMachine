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
from MysteryMachine.schema.Locker import Reader,Writer
from MysteryMachine.parsetools.MMParser import MMParser , Grammar
from MysteryMachine.schema.MMAttribute import * 
from MysteryMachine.schema.MMAttributeValue import  * 

import MysteryMachine.Exceptions as Error

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

  def __init__(self, id,owner,store,**kwargs):
    """
     Get an object handle on an existing object with id.

    @param string id : 
    @return  :
    @author
    """
    super(MMObject,self).__init__(self,**kwargs)
#    self.logger.debug( "Creating %s" % id)
    self.name = id
    #Ensure strong ref to owner.
    self.owner = owner.getSelf()
    self.store = store
    self.parser = MMParser(self)
    self.logger = logging.getLogger("MysteryMachine.schema.MMObject")
    if kwargs.get('create',False):
        self._mark_for_update()


#  def get_ancestor(self):
#    """Return the object category node
#
#    Technically objects are 'owned' by the system, but category
#    nodes are their ancestor.
#    """
#    category, id = self.name.split(":")
#    return self.owner[category]

  def _make_attr(self,name):
      attrval = self.store.GetAttribute(name)
      t,p = attrval
      a = MMAttribute(name,MakeAttributeValue(t,p),self,copy = False )
      return a 

  @Reader 
  def __getitem__(self, attrname):
    """
    Basic get item handling. Returns 'attribute' of attrname.
    ( I mean MMAttribute here not python attribute). 

    @param string attribute : 
    @return MMAttribute :
    @author
    """
    attrname = self.canonicalise(attrname)
    parent = self.get_parent()

    attr = self._get_item(attrname , self._do_getitem , attrname, parent)
    if attr.is_deleted:
        raise KeyError(attrname)

    if type(attr.get_value()) is ShadowAttributeValue:
        if not parent or not parent.has(attrname):
             del self.cache[attrname]
             # We can raise here without checking the store
             # hasn't miracliously found a value,
             # - without going thorought the std set path.
             raise KeyError(attrname)
    
    return attr

  def _do_getitem(self,attrname,parent):
    if self.store.HasAttribute(attrname):
        return self._make_attr(attrname) 
    else:
        if parent is None:
           #No Parent so raise no attrname.
           raise KeyError(attrname)
        
        #Ensure the attribute can be fetched - if not parent will
        # raise an exception.
        pattr = parent[attrname]
        attr  = MMAttribute(attrname,ShadowAttributeValue(self,attrname=attrname,object=self),
                            self,copy = False) 
        return attr        


  @Writer
  def __setitem__(self, attrname, attrvalue):
    """
    Implements the basic setting code for attributes.

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
    attrobj = self._set_attr_item(attrname,attrvalue)
    #Get AttributeValue type object - so it is ready for the storage engine.
    attrvalue = attrobj.get_value()
    #self.store.SetAttribute(attrname,attrvalue.get_type(),attrvalue.get_parts())    
    #self._do_notify()

  @Writer
  def __delitem__(self, attrname):
    """
    Ovveride this if you've overridden setattr

    @param string attribute : 
    @return  :
    @author
    """
    #
    attrname = self.canonicalise(attrname) 
    self._del_item(attrname,MMAttribute.delete_callback(self,attrname))


  def iterkeys(self):
        return self._iterhelper(lambda x:x[0] != '.',self._iter,
                               self.store.EnumAttributes)


  @Reader 
  def EnumAttributes(self):
        for key in self.iterkeys():
            yield key
        parent = self.get_parent()
        if parent is not None:
            for key in self.get_parent().iterkeys():
                yield key

  @Reader
  def __contains__(self,name):
       a = self.store.HasAttribute(name) 
       self.logger.debug( "** %s does %s exist** ", name , ("" if a else "not"))
       return a

  def has(self,name):
       parent = self.get_parent()
       a = self.store.HasAttribute(name)
       if not a and parent:
            parent = parent.has(name)
       return a or parent


  def _validate(self):
    """

    @return bool :
    @author
    """
    pass

  @Reader
  def get_parent(self):
    """

    @param string attribute : 
    @return string[*] :
    @author
    """
    parent = None
    #Bypass inheritance lookup.
    if self.store.HasAttribute(".parent"):
        parent = self._get_item(".parent",self._make_attr,".parent") 
    else:
        self.logger.debug("no defined parent attr\n")
    #We don't try to get the parent from the category - the 
    # category only store a default parent to be used at creation
    #
    #By limiting the inheritance in this manner we reduce the 
    # amount of confusing 'action at a distance' and make the
    # checking required to stop inheritance loops reasonable.
    
    self.logger.debug( "parent type is %s " %type(parent))
    self.logger.debug( "Parent = %r" % parent)
    if parent != None:
        parent = parent.get_object()

    #If the categories parent is ourselves this can occur
    # Null the parent to prevent endless recursion.
    if parent is self: parent = None
    return parent

  @Writer
  def set_parent(self,parent):
    #We can safely use the basic code to set the parent as it
    #  only uses any inheirted values as a type hint.
    #parent = parent.getSelf()
    if type(parent) not in (MMObject, MMNullReferenceValue): 
        raise Error.InvalidParent("%s is not an MMObject"%type(parent))

    parent_walk = parent.getSelf()
    while parent_walk is not None:
        if parent_walk is self: raise Error.InvalidParent("would create a loop: %r is a parent of %r"%(self,parent))
        parent_walk = parent_walk.get_parent()

    self[".parent"]=parent


  @Reader
  def __str__(self):
    # def name attribute contains the instructions for a human
    # readable interpreation of this object. Normally "mm:`:name`"
    #
    # Fall back to Schema ID if defname attribute doesnot exist
    try:
        name = str(self[".defname"])
    except KeyError: name=self.get_nodeid()
    return self.parser.GetString(name,repr(self))

  def __repr__(self):
    """
    Return the internal object name
    """
    return self.get_nodeid()

   
  def get_parser(self):
    return self.parser


  def writeback(self,):
      if self.is_modified:
          self.get_root().store.NewObject(self.get_nodeid())
      if self.is_deleted:
          self.get_root().store.DeleteObject(self.get_nodeid())

      super(MMObject,self).writeback()

  @staticmethod
  def delete_callback(system,name):
      def callback():
          system.store.DeleteObject(name)
      return callback

  @Writer
  def _mark_for_update(self,): pass
