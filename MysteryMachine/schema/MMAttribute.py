#!/usr/bin/env python
#   			MMAttribute.py - Copyright roger
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
# The original location of this file is /home/roger/sources/MysteryMachine/generated/MMAttribute.py
#
#

from MMBase import *
from MMAttributeValue import CreateAttributeValue , MMAttributeValue_MMRef

import operator
import functools
import sys
 
import logging
 



class MMAttributeContainer(MMContainer):
    """
    This is specialisation of MMContainer for objects which contain 
    MMAttributes
    """
    def _set_item(self,attrname  , attrvalue ):

        """
        Handle MMAttribute assignment.

        This needs to see if there is an existing attribute, and set it value
        or create a new Attribute object.
        """
        #Deal only with any value part of an existing attribute.
        #  to create a reference caller should use getRef()
        if isinstance(attrvalue,MMAttribute):
            attrvalue=attrvalue.get_value()
       
        overwrite = False
        attrobj   = None
        #Fetch exists attribute if any to preserve value type.
        try:
            attrobj = self[attrname]
            overwrite = True
        except KeyError:
            pass
        
        #Check the attribute didn't come from a parent.
        if  ( attrobj  is None ) or ( attrobj.get_owner() is not self ):
            attrobj  = MMAttribute(attrname,attrvalue,self)
        
        #Update Attribute if necessary
        if overwrite: attrobj.set_value(attrvalue )
        
        #Write back to the cache
        super(MMAttributeContainer,self)._set_item(attrname,attrobj) 
        return attrobj


class MMAttribute (MMAttributeContainer):

  """
   This class represents an attribute of an MMObject in a MMSystem, such attributes
   are normally single values, or paragraphs of text, but can also be relationships
   with other MMObjects

   Again this is base class to be overr

  :version:
  :author:
  """

  """ ATTRIBUTES


  raw_val  (private)


  type  (private)

  object  (private)


  isLoaded  (private)

  """
    
  def __init__(self,name,value,owner , copy = True):
     super(MMAttribute,self).__init__(self,name,value,owner,copy)
     self.name=str(name)
     self.valueobj=CreateAttributeValue(value , copy)
     self.owner=owner
     self.logger    = logging.getLogger("MysteryMachine.schema.MMAttribute")
     #self.logger.setLevel(logging.DEBUG)

  def get_owner(self):
     return self.owner

  def __str__(self):
     """

     @return string :
   
     """
     return self.get_raw_rst() 

  def __repr__(self):
     """
 
     @return string :
     @author
     """
     return repr(self.owner)+":"+self.name

  def GetFullExpansion(self):
     """
     This function returns a Fully expanded string represenation of the Attribute.

     @return string :
     """
     return self.get_parser().GetString(self.get_raw_rst(),repr(self))

  #Special case to override the definiton in Base.
  def _validate(self):
     """

     @return bool :
     @author
     """
     self.valueobj._validate(self)
 
  def get_value(self):
     return self.valueobj

  def set_value(self,val, copy = True):
     #Quit early in case of No-Op - triggered by _writeback.
     if val is self.valueobj: return

     try:
        self.valueobj.assign(val)
     except:
        self.valueobj = CreateAttributeValue(val,copy)
     self._writeback()

  #This is intend for method lookup
  def __getattr__(self,name):
      self.logger.debug("dereffing attr %s for %s" % (name , repr(self)))
      if name in self.valueobj.exports:
        return functools.partial(getattr(self.valueobj,name),obj = self)
      else: raise AttributeError("%s not in %s"% ( name,repr(self) ) )

  def _writeback(self):
     self.owner[self.name] = self.valueobj

  def getRef(self):
     """
     @returns: A reference to this attribute which can be used
              instead of the value.
     """    
     return MMAttributeValue_MMRef(value = self)

  def getSelf(self):
     """
     Override the basic get self so will find deref the attribute
     to a stored object.
     """
     
     self.logger.debug("dereffing ref %s " % repr(self))
     if "get_object" in self.valueobj.exports:
        return self.valueobj.get_object(self)
     
     return self


  def get_parser(self):
     return self.owner.get_parser()

  def _makeattr(self,name):
     return MMAttribute(name,self.valueobj.__getitem__(name,obj= self),self,False)

  def __getitem__(self,name):
     if '__getitem__' not in self.valueobj.exports:
        raise TypeError("%s is not indexable (MM)" % self.valueobj.__class__)
     
     return self._get_item(self._keymap(name),self._makeattr,self._keymap(name))
  
  def __setitem__(self,name,value):
     if '__setitem__' not in self.valueobj.exports:
        raise TypeError("%s is not indexable (MM)" % self.valueobj.__class__)
     
     attr = self._set_item(name,value)
     self.valueobj.__setitem__(name,attr.get_value(), obj = self)
     self._writeback()

  def __delitem__(self,name):
     if '__delitem__' not in self.valueobj.exports:
       raise TypeError("%s is not indexable (MM)" % self.valueobj.__class__)
     
     self._invalidate_item(name)
     self.valueobj.__delitem__(name,obj = self )
     self._writeback()

  def __contains__(self,name):
     if '__contains__' not in self.valueobj.exports:
       raise TypeError("%s is not iterable (MM)" % self.valueobj.__class__)
     
     return self.valueobj.__contains__(name,obj = self)

  def _keymap(self,key):
    if hasattr(self.valueobj,"GetStableIndex"):
        return self.valueobj.GetStableIndex(key)
    else: return key

  def __iter__(self):
     if '__iter__' not in self.valueobj.exports:
       raise TypeError("%s is not iterable (MM)" % self.valueobj.__class__)
     
     for name in self.valueobj.__iter__(obj = self):
       yield (name , self._get_item(self._keymap(name),self._makeattr,self._keymap(name)) )
  
