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
from MysteryMachine.schema.MMAttributeValue import MMAttributeValue 
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

  def __init__(self, id,parent,store):
    """
     Get an object handle on an existing object with id.

    @param string id : 
    @return  :
    @author
    """
    MMBase.__init__(self)
#    print "Creating %s" % id
    self.id = id
    #Ensure strong ref to parent.
    self.parent = parent.getSelf()
    self.store = store
    self.parser = MMParser(self)


  def __getitem__(self, attrname):
    """
    Basic get item handling. Returns 'attribute' of attrname.
    ( I mean MMAttribute here not python attribute). 

    @param string attribute : 
    @return MMAttribute :
    @author
    """
    #TODO detect 'private attributes' which require special handling
    if self.store.HasAttribute(attrname):    
        return self.store.GetAttribute(attrname)
    else:
        return self.get_parent()[attrname]

  def __setitem__(self, attrname, attrvalue):
    """
    Implements the basic setting ode for attributes.

    @param string attribute : 
    @param MMAttribute value : 
    @return  :
    @author
    """

    #Deal only with any value part of an existing attribute.
    # TODO - decide if this is really what want to do - or would
    # this create a reference.
    if isinstance(attrvalue,MMAttribute):
        attrvalue=attrvalue.get_value()

    #Fetch exists attribute if any to preserve value type.
    if attrname in self:
        val=self[attrname]
        if val.get_owner() is not self:
            val=val.copy(self,attrname)
        val.set_value(attrvalue)
    else:
        #No existing attr create a new one
        val = MMAttribute(attrname,attrvalue,self)
    #Write back to store engine
    self.store.SetAttribute(attrname,val)    

  def __delitem__(self, attrname):
    """
    Ovveride this if you've overridden setattr

    @param string attribute : 
    @return  :
    @author
    """
    self.store.DelAttribute(attrname,val)    
  
  def __iter__(self):
        for a in self.store.EnumAttributes():
            yield a

  def __contains__(self,name):
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
    #Bypass inheritance lookup.
    return self.store.GetAttribute(".parent").get_object()

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

    def __init__(self,parts):
        super(MMAttributeValue_MMObjectRef, self).__init__(parts)
        if len(self.parts) != 1 : raise Error()
        part = parts[0]
        #Decompose part and then recombine 
        if isinstance(part,MMAttributePart):
            part = part.get_value()
        if isinstance(part,MMObject):
            #Get string represenation of the object.
            #TODO Store object here so it cached.
            self.parts[0] = MMAttributePart("",repr(part))
        else:
            #TODO handle this case - str is ok anyway
            self.parts[0] = MMAttributePart("",part)
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
  #      print "refobj->%s<--" % attr
        pstr = self.get_raw(attr)
        print "pstr  ->%s<--" % pstr
        objref = Grammar(attr).parseString(pstr)[0]
  #      print "ret = %s, class = %s" % (objref , objref.__class__ )
        return objref

    def get_raw_rst(self,obj = None):
        return ":mm:`"+ self.get_raw(obj) + "`"
