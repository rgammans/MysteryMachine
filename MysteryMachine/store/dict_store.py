import six
import re
import operator
from MysteryMachine.policies.SequentialId import NewId
from MysteryMachine.store import *
from MysteryMachine.store.Base import Base 
from MysteryMachine.Exceptions import *


import collections.abc
import logging
import types

_dict_stores = dict()

class dict_store(Base):
    """
    A non-persistent Store which is design to be simple but complaint
    with the Mysterymachine interface - mainly intended for use in the
    test harnessees.
    """
    
    uriScheme = "dict"

    invalidobj = re.compile("^\.")
    @staticmethod
    def GetCanonicalUri(uri):
        return uri

    def __init__(self,uri,create = False):
        Base.__init__(self,uri,)
        self.logger = logging.getLogger("MysteryMachine.store.dict_store")
        path = GetPath(uri)
        if create:
            _dict_stores[path] = { }

        self.catdict = _dict_stores[path]

    def _walkPath(self,dbpath):
        head = self.catdict
        for ele in dbpath:
            head = head[ele]
        return head
    
    def _GenericEnum(self,path,predicate):
        dbpath = self.canonicalise(path)
        root = self._walkPath(dbpath)
        for potential in root.keys():
            if predicate(root,potential): yield potential

    def EnumCategories(self):
        #Forward the iterator object
        return self._GenericEnum("", 
            lambda d,k:  isinstance(d[k],collections.abc.Mapping)  and k[:2] !='..' 
        )

    def _testObject(self,container,name):
        return (re.match(self.invalidobj,name) is None ) and ("..object" in container[name]) 
    
    def EnumObjects(self,cat):
        return self._GenericEnum(cat, self._testObject ) 

    def NewCategory(self,cat):
        dbpath = self.canonicalise(cat)
        d = self._walkPath(dbpath[:-1])
        if dbpath[-1] in d: return
        d[dbpath[-1]] = { "..category": None }
 
    def _GenericHas(self,sentinel_name,name):
        dbpath = self.canonicalise(name)
        d = self._walkPath(dbpath[:-1])
        return dbpath[-1] in d and sentinel_name in d[dbpath[-1]]

    def HasCategory(self,name):
        return self._GenericHas("..category",name)

    def NewObject(self,cat):
        dbpath = self.canonicalise(cat)
        d = self._walkPath(dbpath[:-1])
        #objs = list(self.EnumObjects(cat))
        #newid = NewId(objs)
        newid = dbpath[-1]
        d[newid] = { "..object":None }
        return newid

    def _GenericDelete(self,name):
        dbpath = self.canonicalise(name)
        d = self._walkPath(dbpath[:-1])
        lpath = dbpath[-1]
        try:
            del d[lpath]
        #If it's not there we don't need to delete it...
        except KeyError:pass


    DeleteCategory= _GenericDelete
    DeleteObject =  _GenericDelete
      
    def HasObject(self,name):
         return self._GenericHas("..object",name)

    def EnumAttributes(self,obj):
       return self._GenericEnum(obj, 
            lambda d,a: (not isinstance(d[a],collections.abc.Mapping))  and a[:2] != '..' 
        )

    def HasAttribute(self,name):
        dbpath = self.canonicalise(name)
        d = self._walkPath(dbpath[:-1])
        return dbpath[-1] in d and type(d[dbpath[-1]]) is type((),)

    def SetAttribute(self,attr,attrtype,parts):
        dbpath = self.canonicalise(attr)
        d = self._walkPath(dbpath[:-1])
        #Verify the StoreApi is being adhered too
        #  this will pick up issues in tests where we use dict_store.
        for p,v in parts.items():
            if not isinstance(v,six.binary_type):
                raise StoreApiViolation("%s has part %s of type %s (value:'%r')"%(attr,p,type(v),v))

        d[dbpath[-1]]=(attrtype,parts)

    DelAttribute = _GenericDelete

    def GetAttribute(self,attr):
        dbpath = attr.split(":")
        d = self._walkPath(dbpath[:-1])
        self.logger.debug( "GETPATH = %s " % dbpath)
        return d[dbpath[-1]]


    def lock(self):
        #FIXME - Lock store and save to uri on disk...
        pass

    def unlock(self):
        pass

