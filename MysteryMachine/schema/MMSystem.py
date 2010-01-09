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

import MysteryMachine
from Globals import DocsLoaded

from MysteryMachine.schema.MMObject import *
from MysteryMachine.schema.MMBase import *
from MysteryMachine.store import *
#from MMSystemDiff import *
#from Controller import *

from Globals import * 

import re
import time
import weakref
import binascii


class MMSystem (MMBase):

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

 
  def __init__(self, store , new = False ):
    """
     Creates an object refering to an existing system on the OS fielstore.

    @param string filename : Filename to load from


    @return  :
    @author
    """
    self.store  = store
    self.policies = None #FIXME: what should this be?
    #Add back link to store - call as set in store.Base?
    self.uri = store.getUri()
    self.name = EscapeSystemUri(self.uri)
    DocsLoaded[self.name] = self
    store.set_owner(self)
    self.cache = weakref.WeakValueDictionary()

  def __repr__(self):
    return self.name

  def getUri(self):
    return self.uri

  
  def EnumCategories(self):
    """
     This lists all the existing categories in the MysteryMachine system.

    @return  : Iterable list of caterogies in the system
    @author
    """
    return self.store.EnumCategories()

  def DeleteCategory(self,cat):
    """
    This deletes an existing empty category in the MysteryMachine system.

    @return  : Iterable list of caterogies in the system
    @author
    """

    cat = self.canonicalise(cat)
    objlist = list(self.EnumObjects(cat))
    if len(objlist) == 0:
        self.store.DeleteCategory(cat)
    else: raise "Can't delete non-empty category"
 
  def DeleteObject(self,object):
    return self.store.DeleteObject(object)    

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

    cat = self.canonicalise(cat)
    fullid = cat + ":" + id
    try:
        o = self.cache[fullid]
    except KeyError:
        o = MMObject(fullid,self,self.store.GetObjStore(fullid))
        self.cache[fullid] = o
    #TODO:Unlock Cache.
    return o

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

  def NewCategory(self, CategoryName, formathelper = None , defaultobjref = None):
    """
     Creates a new category

    @param string CategoryName : 
    @param string defaultobjref : Basic template to use for new objects in this category
    @return bool :
    @author
    """
    CategoryName = self.canonicalise(CategoryName)
    self.store.NewCategory(CategoryName)

  def NewObject(self, category, parent = None , formathelper = None):
    """
     Creates a new object in the system.

    @param string category : Category in which to create new object
    @return MMOBject: Created object. 
    @author
    """
    category = self.canonicalise(category)

    id = self.store.NewObject(category)
    obj = self.get_object(category,id)
    obj.set_parent(parent)
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

  def EnumContents(self):
    for cat in self.EnumCategories():
        for obj in self.EnumObjects(cat):
            yield obj


  def getSelf(self):
    """
    A hack function required for our memory Management Strategy
    """
    ## This exists so that MMObject can dereferences the weak proxy
    #  object that the store subsystem will normally pass it.
    return self

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
