#!/usr/bin/env python
#   			MMSystem.py - Copyright Roger Gammans
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
# The original location of this file is /home/roger/sources/MysteryMachine/generated/MMSystem.py
#
#

from .Globals import DocsLoaded

from MysteryMachine.schema.Locker import Reader,Writer
from MysteryMachine.schema.MMObject import *
from MysteryMachine.schema.MMAttributeValue import CreateAttributeValue, MakeAttributeValue
from MysteryMachine.schema.MMBase import *
from MysteryMachine.schema.TransactionManager import TransactionManager
from MysteryMachine.store import *
#from MMSystemDiff import *
#from Controller import *
import MysteryMachine.policies
import MysteryMachine.Exceptions as Error

import MysteryMachine.store.locallock

from .Globals import *
import six
import re
import time
import weakref
import binascii

import logging


##FIXME - Make a per-system configurable
policy = MysteryMachine.policies
 

def find_n_ancestor(obj,dist):
    for i in range(dist): obj = obj.get_ancestor()
    return obj 

@six.python_2_unicode_compatible
class MMSystem (MMAttributeContainer):

  """
   This class represents all the data within a single related set of MMObjects,
   which can create a linked set of MMDocuments. Such as a single Game or Products
   documentation.

  :version:
  :author:
  """

  """ ATTRIBUTES


  repo  (private)`
  store_uri  (private)
  working_uri  (private)
    obj = MMSystem(None , new = true)
  controllers  (private)
  objCache  (private)

  """

 
  def __init__(self, store , new = False , flags = { } ):
    """
     Creates an object refering to an existing system on the OS fielstore.

    @param string filename : Filename to load from


    @return  :
    @author
    """
    super(MMSystem,self).__init__(self,store,new)
    self.store  = store
    self.policies = None #FIXME: what should this be?
    #Add back link to store - call as set in store.Base?
    self.uri = store.getUri()
    self.name = EscapeSystemUri(self.uri)
    self.loadflags = flags
    DocsLoaded[self.name] = self
    store.set_owner(self)
    self.encoding = self._get_encoding()
    self.old_encoding = self.encoding
    self.logger = logging.getLogger("MysteryMachine.schema.MMSystem")
    self.lm  = MysteryMachine.store.locallock.LocalLocks()
    self.tm  = TransactionManager(self.lm,self.store)   
    
  def __repr__(self):
    return self.name


  def __str__(self):
    try:
       name = self[".defname"].get_raw_rst()
    except Exception as e:
       self.logger.debug(str(e))
       name = repr(self)
    return name

  def getUri(self):
    return self.uri

  def get_root(self,):
    return self

  def get_tm(self,):
    return self.tm
 
   
  def get_nodeid(self,):
    return ""
  
  @Reader   
  def EnumCategories(self, **kwargs):
    """
     This lists all the existing categories in the MysteryMachine system.

    @return  : Iterable list of categories in the system
    @author
    """
    return self._EnumX(self.store.EnumCategories, val_guard = lambda o:isinstance(o,MMCategory) , **kwargs)


  @Writer
  def _DeleteCategory(self,cat):
    """
    This deletes an existing empty category in the MysteryMachine system.

    @return  : Iterable list of caterogies in the system
    @author
    """

    cat = self.canonicalise(cat)
    objlist = list(self.EnumObjects(cat))
    if len(objlist) == 0:
        self.store.DeleteCategory(cat)
        self._do_notify()
    else: raise "Can't delete non-empty category"
 

 
  @Writer
  def DeleteCategory(self,cat):
     cat = self.canonicalise(cat)
     item = self._del_item(cat,MMCategory.delete_callback(self,cat))
  
  @Writer
  def DeleteObject(self,object):
    names = object.split(":")
    cat = self.canonicalise(names[0])
    parent = self._find_node(self,names[:-1])
    return parent.DeleteObject(names[-1])

  @Reader
  def EnumObjects(self, category):
    """
     Returns a list of all the objects in the specified category.

    @param string category : The category to enumerate the object from
    @return  :
    @author
    """
    return self.store.EnumObjects(self.canonicalise(category))
  
 
  def get_object(self, cat , id):
    """
     Returns the specified object.

    @param string ObjectId : 
    @return MMObject :
    @author
    """

    return self[cat][id]

  def Commit(self, msg):
    """
     Stores the current set of changes to the chnage log.

    @param string msg : 
    @return bool :
    @author
    """
    self.store.commit(msg )
    
  def Rollback(self):
    """
     Reverts any uncommited changes.

    @return  :
    @author
    """
    return self.store.rollback()

  def Revert(self, revid):
    """
     Reverts the system to specified point in the changelog

    @param string revid : 
    @return bool :
    @author
    """
    return self.store.revert(revid)

  def getChangeLog(self):
    """
     Returns a list of revisions in the changelog

    @return  :
    @author
    """
    return self.store.getChangeLog()

  @Writer
  def _NewCategory(self, CategoryName, formathelper = None , defaultparent = None):
    CategoryName = self.canonicalise(CategoryName)
    self.store.NewCategory(CategoryName)
    self[CategoryName][".parent"] = defaultparent
    self._do_notify()

  @Writer
  def NewCategory(self, CategoryName, formathelper = None , defaultparent = None):
    """
     Creates a new category

    @param string CategoryName : 
  xdefaultobjref : Basic template to use for new objects in this category
    @return bool :
    @author
    """
    name = self.canonicalise(CategoryName)
    cat = MMCategory(self,name ,create = True)
    if defaultparent is not None:
        cat[".parent"] = defaultparent
    self._new_item(name,cat)
  
  #System New object is not a writer - because it modifies a child
  #node of system
  def NewObject(self, category, parent = None , formathelper = None):
    """
     Creates a new object in the system.

    @param string category : Category in which to create new object
    @return MMOBject: Created object. 
    @author
    """ 
    cat = self[category]
    obj = cat.NewObject(parent,formathelper)
    return obj

  @Writer
  def _NewObject(self, category, parent = None , formathelper = None):
    """
     Creates a new object in the system.

    @param string category : Category in which to create new object
    @return MMOBject: Created object. 
    @author
    """
    category_name = self.canonicalise(category)
    #Get Category obj and ensure category exists,
    # don't depend on the store to check it's existence for us.
    category = self[category_name]

    id = self.store.NewObject(category_name)
    obj = self.get_object(category_name,id)
    
    if parent is None:
        #Get parent from category
        try:
            parent = self[category_name][".parent"]
            parent = parent.getSelf()
        except KeyError: pass
        
    if parent is not None: obj.set_parent(parent)
    category._do_notify()
    return obj

  
  def getUtilFunctions(self):
    """
     Returns list of available utility functions

    @return string[*] :
    @author
    """
    pass

  def InvokeUtil(self, UtilName):
    """
     Call a utility function

    @param string UtilName : 
    @return  :
    @author
    """
    pass
    
  @staticmethod
  def Create(uri):
    """
    Create a backing store for a new blank MMSystem

    @param string uri : 
    @return MMSystem :
    @author
    """
    store = CreateStore(uri) 
    return MMSystem(store)

  @staticmethod
  def OpenUri(uri,flags =  None):
    """
    Create a backing store for a new blank MMSystem

    @param string uri : 
    @return MMSystem :
    @author
    """
    store = GetStore(uri) 
    return MMSystem(store,flags = flags)


  
  def DoValidate(self):
    """

    @return bool :
    @author
    """
    pass

  def clone(self, revid, new_workingdir):
    """

    @param string revid : 
    @param string new_workingdir : 
    @return MMSystem :
    @author
    """
    pass

  def diff(self, revid):
    """

    @param string revid : 
    @return MMSystemDiff :
    @author
    """
    pass

  @Writer
  def set_name(self,name):
    """Set a user friendly name for the system.

    This would probably be the name for the project the system is used to store
    """
    nm = self._set_attr_item(".defname",name)

  @Reader
  def get_name(self):
    """Return a userfriendly for the system.

    returns None if one isn't set.
    """
    if self.store.HasAttribute(".defname"):
        attribute = MakeAttributeValue(*(self.store.GetAttribute(".defname")))
        if hasattr(attribute,"_compose"):
            attribute._compose(self)
        return six.text_type(attribute)
    return None

  def _make_encoding(encoding):
        "_raw",{'txt':encoding}

  @Writer
  def set_encoding(self,encoding):
    """Define default character set encoding for non-unicode data in thi system


    Encoding names must be ascii.

    Raises LookupError if the codec is unknown
    """

    import codecs
    codecs.lookup(encoding) #Check encoding is known

    self.old_encoding = self.encoding
    self.encoding = encoding

    #We don't use the full attribute type schema here as the encoding
    #must be treated as simply as possibly because all string interpolation
    #depends on it. So we can't run the parser for this value - as the parser

    #may need this value for it's input
    enc_value =  MMAttributeValue_Raw(parts = {'txt':self.encoding.encode('utf-8')})
    self._set_attr_item('.encoding',enc_value)

  def _get_encoding(self):
    if self.store.HasAttribute(".encoding"):
        attrtype, parts = self.store.GetAttribute(".encoding")
        if attrtype != "_raw":
            raise Error
        return parts["txt"].decode('utf-8')
    else: return "ascii"


  @Reader 
  def get_encoding(self):
    return self.encoding

  @Reader
  def EnumContents(self):
    for cat in self.EnumCategories():
        for obj in self.EnumObjects(cat):
            yield cat + ":" + obj

  iterkeys = EnumContents

  def _find_node(self,root, path, lastpath = ""):
      node = root
      for element in path:
          element = self.canonicalise(element)

          if node is None: 
              raise Error.NullReference(lastpath)

          lastpath = repr(node) + ":" + element
          if element != "":
              node = node[element]
      return node


  def __getitem__(self,obj): 
    self.logger.debug("System asked for %s"%obj)

    fullid = ""
    len = 0
    elements = obj.split(":")
    el1 = self.canonicalise(elements[0])
    #Get the first node in the path and then walk it, to find
    # the target object 
    node = self._get_item(el1,self._do_get_item,el1)
    if node.is_deleted:
        raise KeyError(el1)

    node = self._find_node(node, elements[1:] , lastpath = el1)
    return node
    

  def _do_get_item(self, fullid ):
    if self.store.HasCategory(fullid):
         return MMCategory(self,fullid)
    elif self.store.HasObject(fullid): 
        return MMObject(fullid,self,self.store.GetObjStore(fullid))
    elif self.store.HasAttribute(fullid):
        val = MakeAttributeValue(*(self.store.GetAttribute(fullid)))
        return MMAttribute(fullid,val,self,copy = False )


    raise KeyError(fullid)
      

  def __delitem__(self,obj):
      path = obj.split(":")
      if len(path) !=  2: raise KeyError(obj)       
      self.DeleteObject(obj)
      

  def Lock(self):
    """
    Wait for the backing to to be in a stable state and prevent
    further updates until Unlock()'d
    """
    self.store.lock()

  def Unlock(self):
    """
    Release a lock granted by Lock()
    """
    self.store.unlock() 

  def SaveAsPackFile(self,*args,**kwargs):
    import MysteryMachine.Packfile
    kwargs['flags'] = self.loadflags

    MysteryMachine.Packfile.SavePackFile(self,*args,**kwargs)

  def discard(self,):
    #Encoding is the only special thing.
    # = and we don't awnt to trigger base as wee are not contained/
    self.encoding = self.old_encoding

  def writeback(self,):
    self.old_encoding = self.encoding

#  def start_write(self,*args):
#    super(MMSystem,self).start_write(*args)

  def close(self,):
        """Call this if you've finished using the system.

        This call isn't protected against other threads. And
        leaves the object in an inconsistent state.
        """
        self._invalidate_cache()
        if self.store is not None:
            self.store.close()
        self.store = None
        self.tm = None

@six.python_2_unicode_compatible
class MMCategory(MMAttributeContainer):

    def __init__(self,owner,name,**kwargs):
        super(MMCategory,self).__init__(self,owner,name,**kwargs)
        self.owner = owner
        self.name   = name
        self.logger = logging.getLogger("MysteryMachine.schema.MMCategory")

    def get_owner(self,):
        return self.owner

    def __repr__(self):
        return self.name

    def __str__(self):
        try:
            name = self[".defname"].get_raw_rst()
        except Exception as e:
            self.logger.debug(str(e))
            name = repr(self)
        return name

    @Reader
    def __getitem__(self,item):
        if item[0] == ".":
            item = "." + self.canonicalise(item[1:])
        node = self._get_item(item,self._do_get_item,item)
        if node.is_deleted: raise KeyError(item)
        return node

    def _do_get_item(self, key ):
      fullid = self.name + ":" + key
      if self.owner.store.HasCategory(fullid):
           return MMCategory(self,fullid)
      elif self.owner.store.HasObject(fullid): 
          return MMObject(key,self,self.owner.store.GetObjStore(fullid))
      elif self.owner.store.HasAttribute(fullid):
          val = MakeAttributeValue(*(self.owner.store.GetAttribute(fullid)))
          return MMAttribute(key,val,self,copy = False )


      raise KeyError(fullid)

    @Reader
    def EnumObjects(self,):
        for x in self.owner.EnumObjects(self.name):
            yield x

    @Writer
    def __setitem__(self,item,value):
        if item[0] ==".":
            itemname =  self.canonicalise(item)
            #Process set to None.
            if value is None:
                del self[item] 
                return

            itm = self._set_attr_item(itemname,value)
            val = itm.get_value()

        else: raise LookupError("Cannot directly set objects")

    @Writer
    def __delitem__(self, attrname):
        if attrname[0] ==".":
            name = self.canonicalise(attrname) 
            item = self._del_item(name,MMAttribute.delete_callback(self.owner,self.name + ":" + name))
        else:
            name = self.canonicalise(attrname)
            item = self._del_item(name,MMObject.delete_callback(self,self.name + ":" + name))
 



    def _getAttribute(self,name):
      if not self.owner.store.HasAttribute(self.name+":"+name):
            raise KeyError(name)
      attrval = self.owner.store.GetAttribute(self.name+":"+name)
      t,p = attrval
      a = MMAttribute(name,MakeAttributeValue(t,p),self,copy = False )
      return a 

    def __iter__(self):
        for objkey in self.EnumObjects():
            yield  self[objkey]

    itervalues = __iter__

    @Writer
    def NewObject(self,  parent = None , formathelper = None):
       objs = list(self.iterkeys())
       Id = self.canonicalise(policy.NewId(objs))
       fullId = self.name + ":" + Id
       obj = MMObject(Id,self,self.owner.store.GetObjStore(fullId),create =True)
       self._new_item(Id,obj)
       if parent is None:
          #Get parent from category
          try:
              parent = self[".parent"]
              parent = parent.getSelf()
          except KeyError: pass
          
       if parent is not None: obj.set_parent(parent)
       return obj

    @Writer
    def DeleteObject(self,name):
        name = self.canonicalise(name)
        item = self._del_item(name,MMObject.delete_callback(self,self.name + ":" + name))
  

    def iteritems(self):
       for objkey in self.EnumObjects():
            yield  objkey , self[objkey] 

    def iterkeys(self):
       for objkey in self.EnumObjects():
           yield objkey 

    def get_parent(self):
        return self['.parent'].getSelf()


    def set_parent(self,newparent):
        if type(newparent) is not MMObject: raise Error.InvalidParent()

        self['.parent'] = newparent


    def writeback(self,):
        if self.is_modified:
            self.owner.store.NewCategory(repr(self))
        if self.is_deleted:
            self.owner.store.DeleteCategory(repr(self))

        super(MMCategory,self).writeback()

    @staticmethod
    def delete_callback(system,name):
        def callback():
            system.store.DeleteCategory(name)
        return callback
