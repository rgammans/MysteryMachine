#!/usr/bin/env python
#           MMAttribute.py - Copyright roger
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
from MysteryMachine.schema.Locker import Reader,Writer

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
    @Writer
    def _set_attr_item(self,attrname  , attrvalue ):
        attrobj  = None

        #Sanity check.
        if attrvalue is None: raise ValueError("Cannot store none")
        objname = "unknown" 

        try:
            attrobj = self[attrname]
        except KeyError:
            pass

        #Deal only with any value part of an existing attribute.
        #  to create a reference caller should use getRef()
        if isinstance(attrvalue,MMAttribute):
            attrvalue=attrvalue.get_value()

        if  attrobj  is None:
            self.logger.debug("Creating new value object")
            attrobj = MMAttribute(attrname,attrvalue,self,complete_write = True)
        else:
            self.logger.debug("basic set_value")
            attrobj.set_value(attrvalue )

        #if notify: self._do_notify()
        return attrobj
    
    def _do_compose(self,item):
       if isinstance(item,MMAttribute):
            item._compose()

    @Reader
    def EnumAttributes(self, **kwargs):
        rootstore  = self.get_root().store
        return self._EnumX(functools.partial(rootstore.EnumAttributes,self.get_nodeid()) ,
                            val_guard = lambda o:isinstance(o,MMAttribute),
                             **kwargs)



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
    
  def __init__(self,name,value,owner , copy = True ,complete_write = False):
     super(MMAttribute,self).__init__(self,name,value,owner,copy)
     self.name=str(name)
     self.valueobj=CreateAttributeValue(value , copy)
     self.owner=owner
     self.oldvalue = None
     self.logger    = logging.getLogger("MysteryMachine.schema.MMAttribute")
     #self.logger.setLevel(logging.DEBUG)
     if complete_write:
        self._complete_write()

  def get_owner(self):
     return self.owner

  @Reader
  def __unicode__(self):
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

  @Reader
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

  @Reader
  def get_value(self):
     return self.valueobj

  @Reader
  def get_type(self,):
     """return the type of value stored in the attribute"""
     if self.valueobj: return self.valueobj.get_type()
     else: return None

  @Writer
  def set_value(self,val, copy = True , writeback = True ):
     #Quit early in case of No-Op 
     if val is self.valueobj: 
        return

     try:
        self.valueobj.assign(val)
     except Exception, e:
        if str(e): self.logger.warn(e)
        val = CreateAttributeValue(val,copy)
        ##Check assignment is valid
        val.can_assign_to(self.valueobj)
        #do it
        self.valueobj = val 




     self._invalidate_cache()
     self._complete_write()


  def _complete_write(self,):

        #Write back to the cache
        self.owner._new_item(self.name,self) 

        #Now the value is in the cache it (and referenced here)
        #so it won't expire - we can do any final fixup that the 
        #value object might require - most value objects probably don't
        #need this but DLink very much does!. This fixup should then occur
        #before anythini is written to the store.
        self._compose()


  #This is intend for method lookup
  def __getattr__(self,name):
      self.logger.debug("dereffing attr %s for %s" % (name , repr(self)))
      if name in self.valueobj.exports:
        return functools.partial(getattr(self.valueobj,name),obj = self)
      else: raise AttributeError("%s not in %s"% ( name,repr(self) ) )

  @Reader
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

  @Reader
  def __getitem__(self,name):
     if '__getitem__' not in self.valueobj.exports:
        raise TypeError("%s is not indexable (MM)" % self.valueobj.__class__)
     
     return self._get_item(self._keymap(name),self._makeattr,self._keymap(name))
  
  @Writer 
  def __setitem__(self,name,value):
     if '__setitem__' not in self.valueobj.exports:
        raise TypeError("%s is not indexable (MM)" % self.valueobj.__class__)
     
     attr = self._set_attr_item(name,value)
     self.valueobj.__setitem__(name,attr.get_value(), obj = self)

  @Writer
  def __delitem__(self,name):
     if '__delitem__' not in self.valueobj.exports:
       raise TypeError("%s is not indexable (MM)" % self.valueobj.__class__)
     
     self._del_item(name,lambda :None)
     self.valueobj.__delitem__(name,obj = self )

  @Reader
  def __contains__(self,name):
     if '__contains__' not in self.valueobj.exports:
       raise TypeError("%s is not iterable (MM)" % self.valueobj.__class__)
     
     return self.valueobj.__contains__(name,obj = self)
 
  @Reader
  def __len__(self):
     if '__len__' not in self.valueobj.exports:
       raise TypeError("object of type %s has no len (MM)" % self.valueobj.__class__.__name__)
     
     return self.valueobj.__len__(obj = self)

  @Reader
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

  @staticmethod
  def delete_callback(obj,name):
      def callback():
          obj.store.DelAttribute(name)
      return callback

  #Deprecated.
  def _writeback(self,): pass
 
  def writeback(self,):
    store = self.get_root().store
    if not self.is_deleted:
        self.logger.debug("writing back a %s to %r"%(self.valueobj.get_type(),self))
        #print ("writing back a %s to %r"%(self.valueobj.get_type(),self))
        #Don't writeback if our parent is also an attribute, as then
        # it is it's resopnibility to do store stuf
        ancestor = self.get_ancestor()
        if not isinstance(ancestor,MMAttribute):
            self.logger.debug("\t(t,v)->(%r,%r)"%( self.valueobj.get_type(),self.valueobj.get_parts() ))
            store.SetAttribute(self.get_nodeid(),self.valueobj.get_type(),self.valueobj.get_parts())    
        else: 
            self.logger.debug("\tterminated writeback as contained by %r"%ancestor)
        self.oldvalue = None
    else:
        store.DelAttribute(self.get_nodeid())

  def start_write(self,*args):
        #print ("preparing write to %r"%self)
        if self.oldvalue is None:
            self.oldvalue = _copy.copy(self.valueobj)
            if self.is_shadow():
                #print "elevating shadow"
                #Swap copy and current as the Shadow wants to 
                # reinstated on rollback not a copy..
                self.valueobj,self.oldvalue = self.oldvalue,self.valueobj
                
        return super(MMAttribute,self).start_write(*args)

  def discard(self,):    
        self.oldvalue , self.valueobj = None, self.oldvalue



  def is_shadow(self,):
    """Return True if this is a shadow, or inherirted attribute"""
    return isinstance(self.valueobj,ShadowAttributeValue)

#        Since MMUnstorableAttribtes doesn't honor the owner
#        properties of MMAttributes, they shouldn't be considered
#        MMAttributes, so we might want to invert the inheritance
#        relationship later.
# 
#        However there is an argument for this way round as 
#        isinstance(MMAttribute,MMUnstorableAttribute()) should
#        probably be true -  as it is  a more readable (and obviously correct)
#        test, for both object types.

class MMUnstorableAttribute(MMAttribute):
    """A temporary attribute which is only weakly bound to it's owner.

    Specifically a MMUnstorableAttribute is never written back
    to it's owning object.

    Essentially this attribtue *lies* about having an owner.

    The value of this to allow generic editor code to set up Values
    before writing them to the schema.
    """
    #The implementation of this is trivial we just need to disable
    #the writeback method. But we also force out own compose immediately
    #after init, as that help afew types set themselves up.

    #
    # If you write a MMAttributeValue type which uses compose
    # I strongly advise in your unittests you test it as part
    # of a MMUnstorableAttribute as well.
    #
    # You may need some special hadnling in compose.

    def __init__(self,*args,**kwargs):
        super(MMUnstorableAttribute,self).__init__(*args,**kwargs)


    def writeback(self):
        pass


    def _complete_write(self,):
        #Now the value is in the cache it (and referenced here)
        #so it won't expire - we can do any final fixup that the 
        #value object might require - most value objects probably don't
        #need this but DLink very much does!. This fixup should then occur
        #before anythini is written to the store.
        self._compose()


