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
        return "MMAttributePart(\""+self.value+"\")"
    def get_name(self):
        return self.partname
    def get_value(self):
        return self.value
    def set_value(self,val):
        self.value=val

   
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
    
  AttrTypes = dict() 
  @classmethod
  def register_value_type(cls,name,acls):
    cls.AttrTypes[name]=acls

  def __init__(self,name,type,parts,parent):
    self.name=name
    self.valueobj=self.AttrTypes[type](parts)
    self.parent=parent

  def __str__(self):
    """

    @return string :
    @author
    """
    return self.get_raw_rst() 

  def __repr__(self):
    """

    @return string :
    @author
    """
    return self.parent.__repr__()+":"+self.name

  #Special case to override the definiton in Base.
  def _validate(self):
    """

    @return bool :
    @author
    """
    self.valueobj._validate()
 
  def get_value(self):
    return self.valueobj

  def set_value(self,val):
    self.valueobj=val

  #This is intend for method lookup
  def __getattr__(self,name):
      if name in self.valueobj.exports:
        return getattr(self.valueobj,name)

