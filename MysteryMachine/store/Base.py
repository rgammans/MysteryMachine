#!/usr/bin/env python
#   			MysteryMachine/store/Base.py - Copyright Roger Gammans
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

"""
"""


from MysteryMachine.store import * 


class Base(object):
    """
    New base class for Mystery Machine store to inherit from.


    Many method of this class take Id in the form of
    category:object:Attribute .
    Each part of the id should be in it's cannonical 
    form and be a valid part of the MM Namespace.
    see:
        http://trac.backslashat.org/MysteryMachine/wiki/NameSpace

    Behavour is undefined if names outside the NameSpace are used.
    (With the exception that a leading '.' must be accepted by the store engine)

   


    """
    __metaclass__ = storeMeta

    supports_txn = False

    def canonicalise(self,name):
        """Splits a object or attribute name into it's component parts"""
        if len(name) == 0: return  []
        else: return name.split(":")

    def __init__(self,uri,*args,**kwargs):
        self.uri   = GetCanonicalUri(uri)
        self.owner = None

    def getUri(self):
        """Returns the canonical uri of the store"""
        return self.uri
   
    def get_path(self):
        """Returns the path element of the store"""
        return GetPath(self.uri)
 
    @staticmethod
    def GetCanonicalUri(uri):
        """
        This method is required for all store. 

        If you are writing a new store you should override this.

        It should return a persistent unique identifier for this store which
        can also function as a uri.
        For instance filebased store could resolve all of the symlinks to provide
        a constant uri.
        """
        return uri

    def get_owner(self):
        """
        Returns the MMsystem instance associated with this store.
        """
        return self.owner

    def set_owner(self,v):
        """
        Sets the MMsystem instance associated with this store.
        """
        self.owner = weakref.proxy(v)

    def start_store_transaction(self):
        """This function is required to be overridden for ACID compliance

        This function doesn't return until the outstanding changes are
        are in stable store. It *doesn't* require the outstanding
        changes to be integrated into the main data - they can be stored in
        some sort of log file - to be written to the main Db in the 
        background.

        After start_store_transaction the Enum*,Get* and HAs* functio
        have undefined behaviour until commit_ or abort_ store_transaction
        is called.
    
        You should define support_txn = True in your class if
        this function is overridden.

        (The schema model guarantees this interleave won't  occurs
        as schema/transman implements a 2PL scheme.)
        """
        pass

    def abort_store_transaction(self):
        """Discard any data written , until the store state is set
        to the last created checkpoint"""
        pass



    def commit_store_transaction(self,):
        """This function is required to be overridden for ACID compliance
        (This should not be confued with commit - see below)

        This function the last part of the ACID complaince functions.

        Calling this function writes out the changes made since
        start_store_transaction into persistent store.
        """

    def commit(self,msg):
        """
        Override the to support revisions - usually used in the context
        of version control.

        This function has nothing to do witht he ACID properties, see
        commit_store_transaction for that.
        """
        return False

    def rollback(self):
        """
        Override this to provide a rollback action .
        Takes the store back to the last commit.
        """
        return False

    def revert(self,revid):
        """
        Override this to take the game back to any previous revision.
        """
        return False

    def getChangelog(self):
        """
        Override this if you provide transaction logging.

        Retuens a list of revid's which can be revert'ed to .
        """
        return []

    def EnumCategories(self):
        """
        Returns a list or a generator yielding category names
 
        System categories, (those starting with a leading period) should 
        be return be by this method.

        You are expected to override this for your own store.
        """
        pass

    def EnumObjects(self,category):
        """
        Returns a list or a generator yielding item id in the passed category
        
        You are expected to override this for your own store.
        """
        pass

  
    def NewCategory(self,catname):
        """
        Creates a new category with the name catname.
        If a category called 'catname' already exists this has no effect

        You are expected to override this for your own store.
        """ 
        pass

    def NewObject(self,category):
        """
        Creates a NewObject in Category category.

        Returns the Unique id within the category for the object
    
        You are expected to override this for your own store.
        """
        pass

    def HasCategory(self,category):
        """
        Returns True if the store contains an category named category.

        System categories, (those starting with a leading period) should
        be treated normally. Eg. This method must reflect their presence
        or absence to a caller

        You are expected to override this for your own store.
        """ 
        return False


    def HasObject(self,obj):
        """
        Returns True if the store contains an object named obj.

        You are expected to override this for your own store.
        """ 
        return False

    def DeleteObject(self,objectid):
        """
        Deletes the object objectid from the store.

        If you override this you should also call self.RemoveFiles(..)
        on any files removed from the store by this action.

        Behaviour is undefined if there are any attributes on the object

        You are expected to override this for your own store.
        """
        pass

    def DeleteCategory(self,catname):
        """
        Deletes the category catname from the store.

        If you override this you should also call self.RemoveFiles(..)
        on any files removed from the store by this action.

        Behaviour is undefined if there are any objects in the category

        You are expected to override this for your own store.
        """
        pass

    def HasAttribute(self,attrname):
        """
        Returns true if a attribute of name attrname exists in the store.
 
        System attributes, (those starting with a leading period) should
        be treated normally. Eg. This method must reflect their presence
        or absence to a caller

   
        You are expected to override this for your own store.
        """
        pass
  
    def EnumAttributes(self,object):
        """
        Returns a list or a generator yielding attributes names in object object.

        System attributes, (those starting with a leading period) should be
        be returned by this method.        
 
        You are expected to override this for your own store.
        """
        pass

    def GetAttribute(self,attrname):
        """
        Returns a tuple of type and parts for the attribute name attrname
           
        Behavoir is undefined if no attribute attrname exists in the store.
        
        You are expected to override this for your own store.
        """
        pass
    def SetAttribute(self,attrname,attrtype,parts):
        """
        Sets an attribute named attrname to be type attrtpe and composed of parts
        parts

        Type is a string , and parts should be a with strings for both keys
        and values. 

        The Keys  and the type should obey our Namespace guidelines. A store
        provider should be able to retrieve the type and the parts dict.

        You are expected to override this for your own store.
        """
    def DelAttribute(self,attrname):
        """
        Removes and attribute name attrname from the store.

        You are expected to override this for your own store.
        """ 

    def GetObjStore(self,obj):
        """
        Returns a store proxy object for object obj usable as a 
        store by an MMObject

        Behavoir is undefined if no object obj exists in the store.

        You may wish to override this if you use a custom 
        storeproxy class for your store.
        """
        return obj_storeproxy(self,obj)


    def Add_file(self,filename):
        """
        Adds a file to the SCMs repo 

        Override this in your own store to if you provide tranasction
        function usable by other store mixins.

        This function is intended to be called by store modules, so
        to allow them to commincate to the SCM provider. A store provider
        is required to call this if it support interworking with SCM mixins
        """

    def Remove_file(self,filename):
        """
        Removes a file from the SCMs repo 

        Override this in your own store to if you provide tranasction
        function usable by other store mixins.

        This function is intended to be called by store modules, so
        to allow them to commincate to the SCM provider. A store provider
        is required to call this if it support interworking with SCM mixins

        """

    def lock(self):
        """
        Call to wait for the store to be queiscent - called prior to Saving
        a system to pack file.

        SCM systems should use this to enusre the store in a stable state
        before checkpointing any transactions. Data only backends should
        provide this.
        """
        pass
   
  
    def unlock(self):
        """
        Allow updates to continue. see lock()
        """
        pass

    def get_storefiles(self):
        """Returns a generator, or sequence which walks over the files which 
        should be placed in a pack file.  
        """
        return []

    def close(self,):
        """Called prior to nolong using the store to ensure every is saved
        correctly"""
        self.lock()

class obj_storeproxy:
    """
    A generic Proxy store for MMObjects. 

    This class is keeps a referenece to the store and the 
    objects relative path, and forwards the requests tothe main store
    object.
    """
    def __init__(self,store,obj):
        self.store=store
        self.obj=obj

    def GetAttribute(self,attr):
        return self.store.GetAttribute(self.obj + ":" +attr)
        

    def SetAttribute(self,attr,type,parts):
        return self.store.SetAttribute(self.obj + ":" +attr,type,parts)
   
    def DelAttribute(self,attr):
        return self.store.DelAttribute(self.obj + ":" +attr)

    def EnumAttributes(self):
        for a in self.store.EnumAttributes(self.obj):
            yield a

    def HasAttribute(self,attr):
        return self.store.HasAttribute(self.obj + ":" +attr)
 
