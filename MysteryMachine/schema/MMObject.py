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
from MysteryMachine.parsetools.MMParser import MMParser
from MysteryMachine.schema.MMAttribute import * 
#from Cache import *

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

  def __init__(self, id,parent):
    """
     Get an object handle on an existing object with id.

    @param string id : 
    @return  :
    @author
    """
    MMBase.__init__(self)
#    print "Creating %s" % id
    self.id = id
    self.parent = parent
    self.parser = MMParser(self) 


  def __getitem__(self, attrname):
    """
    Override the method, but call pass the call
    instead of raising attribute error.

    @param string attribute : 
    @return MMAttribute :
    @author
    """
    #Overriding method has not found a attribute,
    # check the objects (MMsytem) parent.
    parent =self.get_parent()
    return parent[attrname]    

  def __setitem__(self, attrname, attrvalue):
    """
    Overide this to allow local attributes.

    @param string attribute : 
    @param MMAttribute value : 
    @return  :
    @author
    """
    pass

  def __delitem__(self, attrname):
    """
    Ovveride this if you've overridden setattr

    @param string attribute : 
    @return  :
    @author
    """
    pass

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
    return self[".parent"].get_object()

  def set_parent(self,parent):
#    print "-->",parent.__class__,repr(parent)
    if not isinstance(parent,MMAttribute):
#        print "not mmatrr"
        #try:
        parentval = MMAttribute ( ".parent", CreateAttributeValue("objectref" , [ MMAttributePart("obj",parent) ] )  , self )
        parent = parentval
        #except:
            #TODO: Log error
        #    pass
#    print "attr->",parent.__class__,repr(parent)
    self[".parent"]=parent

  def __str__(self):
    # def name attribute contains the instructions for a human
    # readable interpreation of this object. Normally "mm:`:name`"
    name = self[".defname"]
    return self.parser.ProcessRawRst(name)

  def __repr__(self):
    """
    Return the internal object name
    """
    return self.id
