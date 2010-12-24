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
from MMAttributeValue import MMAttributeValue , CreateAttributeValue , MMAttributeValue_MMRef , ShadowAttributeValue

import operator
import functools
import sys
 
import logging
import copy as _copy
 

recurse_count = 0

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
        global recurse_count

        ## Get current status so we can rollback in case of an exeception
        attrobj  = None
        oldvalue = None
        overwrite = False

        if attrvalue is None: raise ValueError("Cannot store none")
        objname = "unknown" 

        try:
            attrobj = self[attrname]
        except KeyError:
            pass
        else:
            objname = repr(attrobj)
            avobj = attrobj.get_value()
            self.logger.debug("Staring with %r",avobj.get_parts())
            #Don't take a copy of ShadowAttributes, as just deleting their
            # local instance has the correct effect.
            if not isinstance(avobj,ShadowAttributeValue):
                oldvalue = _copy.copy(avobj)
     
        #Deal only with any value part of an existing attribute.
        #  to create a reference caller should use getRef()
        if isinstance(attrvalue,MMAttribute):
            attrvalue=attrvalue.get_value()

        #dispvalue is only used for debugging - but the early exit is important        
        dispvalue = repr(attrvalue)
        if isinstance(attrvalue ,MMAttributeValue):
            dispvalue = "parts-%r" % attrvalue.get_parts() 
            if attrvalue == oldvalue:
                 #It's all ok, but we need to ensure compose is called.
                 # (I'm pretty sure the only way this can be a no-op and raise is
                 #  if we are a sub-call from inside ourselves)
                 self.logger.debug("compose_only(%i) %s" % (recurse_count+1, dispvalue ))
                 attrobj._compose()
                 return attrobj 


        #Recurse count is only used to make the debug tracking more readable
        recurse_count = recurse_count+1
        self.logger.debug( "setting(%i) %s  from %r to %s" % (recurse_count, objname , oldvalue and oldvalue.get_parts()  ,dispvalue ))
       
 
        try:
          
            if  attrobj  is None:
                self.logger.debug("Creating new value object")
                attrobj = MMAttribute(attrname,attrvalue,self)
            elif isinstance(avobj,ShadowAttributeValue):
            #elif attrobj.get_owner() is not self:
                #Check the attribute didn't come from a parent.
                self.logger.debug("Creating copy of shadow value object")
                attrobj  = MMAttribute(attrname,avobj._get_target(),self, copy = True ) 
                attrobj.set_value(attrvalue ,writeback = False )
            else:
                self.logger.debug("basic set_value")
                attrobj.set_value(attrvalue )
            
            #Write back to the cache
            super(MMAttributeContainer,self)._set_item(attrname,attrobj) 
            
            #Now the value is in the cache it (and referenced here)
            #so it won't expire - we can do any final fixup that the 
            #value object might require - most value objects probably don't
            #need this but DLink very much does!. This fixup should then occur
            #before anythini is written to the store.
            attrobj._compose()
            
            return attrobj
        except:
            #Roll back any have complete changes
            (t1, e1, tb1 ) =sys.exc_info()
            self.logger.warn("Exception - rollingback %s"%e1)
            try: 
                if oldvalue is None:
                    del self[attrname]
                else:
                    #self._invalidate_item(attrname)
                    if attrobj is not None:
                        if attrobj.get_value() != oldvalue:
                            self._set_item(attrname,oldvalue)
                        else: self.logger.warn( "rollback skipped! - nothing to do")
            except:
                 (t2, e2, tb2 ) =sys.exc_info()
                 self.logger.warn("Exception during rollback %s,%s"%(t2,e2))
                 import traceback
                 self.logger.debug(traceback.format_tb(tb2))
            finally:
                #Re raise orginally exceptions.
                raise t1,e1,tb1
        finally:
            self.logger.debug( "completing (%i)"%recurse_count)
            recurse_count = recurse_count-1
            
    def _get_item(self,key,func,*args):
        item = super(MMAttributeContainer,self)._get_item(key,func,*args)
        item._compose()
        return item





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

  def _compose(self):
    """
    Do the second initialisation phase for the associated value object.

    Value object support a two phase initialisation, for those values
    which have a referential integrity requirement which is dependent
    on their location within the schema. 

    _compose is called on the value object with the attribute object as
    an argument - in the same manner that exports are called.    

    Calls _compose(self) on the value object.
    """
    if hasattr(self.valueobj,"_compose"):
        self.valueobj._compose(self)

  #Special case to override the definiton in Base.
  def _validate(self):
     """

     @return bool :
     @author
     """
     self.valueobj._validate(self)
 
  def get_value(self):
     return self.valueobj

  def set_value(self,val, copy = True , writeback = True ):
     #Quit early in case of No-Op - triggered by _writeback.
     if val is self.valueobj: 
        return

     try:
        self.valueobj.assign(val)
     except Exception, e:
        self.logger.warn(e)
        self.valueobj = CreateAttributeValue(val,copy)
     if writeback: self._writeback()

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

  def __len__(self):
     if '__len__' not in self.valueobj.exports:
       raise TypeError("object of type %s has no len (MM)" % self.valueobj.__class__.__name__)
     
     return self.valueobj.__len__(obj = self)

  def __iter__(self):
     if '__iter__' not in self.valueobj.exports:
       raise TypeError("%s is not iterable (MM)" % self.valueobj.__class__)
     
     for name in self.valueobj.__iter__(obj = self):
       yield self._get_item(self._keymap(name),self._makeattr,self._keymap(name)) 

  def _keymap(self,key):
    if hasattr(self.valueobj,"GetStableIndex"):
        return self.valueobj.GetStableIndex(key)
    else: return key


  def iteritems(self):
     if '__iter__' not in self.valueobj.exports:
       raise TypeError("%s is not iterable (MM)" % self.valueobj.__class__)
     
     for name in self.valueobj.__iter__(obj = self):
       yield (self._keymap(name) , self._get_item(self._keymap(name),self._makeattr,self._keymap(name)) )
  
  def iterkeys(self):
     if '__iter__' not in self.valueobj.exports:
       raise TypeError("%s is not iterable (MM)" % self.valueobj.__class__)
     
     for name in self.valueobj.__iter__(obj = self):
       yield self._keymap(name) 
  
  itervalues = __iter__ 
