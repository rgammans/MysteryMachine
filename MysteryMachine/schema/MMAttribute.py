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
 
class MMAttribute (MMBase):

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
    self.name=name
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

  def set_value(self,val):
    #Quit early in case of No-Op - triggered by _writeback.
    if val is self.valueobj: return

    try:
        self.valueobj.assign(val)
    except:
        self.valueobj = CreateAttributeValue(val)
    self._writeback()

  #This is intend for method lookup
  def __getattr__(self,name):
      self.logger.debug("dereffing %s for %s" % (name , repr(self.owner)))
      if name in self.valueobj.exports:
        return functools.partial(getattr(self.valueobj,name),self)
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
     if "get_object" in self.valueobj.exports:
        return self.valueobj.get_object(self)
     
     return self


  def get_parser(self):
    return self.owner.get_parser()
