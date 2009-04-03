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
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# 
# This file was generated on Mon Feb 2 2009 at 20:18:08
# The original location of this file is /home/roger/sources/MysteryMachine/generated/MMAttributeValue.py
#
#

from MMBase import *
from MMAttribute import *


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
  def __init__(self,parts):
    self.parts=parts
    self.exports=[ "get_raw_rst"  ]

  def __repr__(self):
    """

    @return string :
    @author
    """
    return str(self.__class__)+"(\""+self.get_raw_rst()+"\")"

  def get_raw_rst(self):
    """
    Gets unprocessed rst contents of attribute.       

    @return string :
    @author
    """
    return "\n".join(map(lambda x:x.get_value(),self.parts))

  def get_parts(self):
    return self.parts

  def _validate(self):
    """

    @return bool :
    @author
    """
    pass




class MMAttributeValue_BasicText(MMAttributeValue):
    def get_type(self):
        return "simple"

#FIXME - Make both theese "simple"s come from the same place

MMAttribute.register_value_type("simple",MMAttributeValue_BasicText)

