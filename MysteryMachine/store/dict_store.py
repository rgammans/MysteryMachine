
import re
import operator
from MysteryMachine.policies.SequentialId import NewId
from MysteryMachine.store import *
from MysteryMachine.store.Base import Base 
from MysteryMachine.Exceptions import *

import logging

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
        Base.__init__(self,uri,create)
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
        return self._GenericEnum("", lambda d,k:  operator.isMappingType(d[k]) and k[0] !="." )

    def _testObject(self,container,name):
        return re.match(self.invalidobj,name) is None
    
    def EnumObjects(self,cat):
        return self._GenericEnum(cat, self._testObject ) 

    def NewCategory(self,cat):
        dbpath = self.canonicalise(cat)
        d = self._walkPath(dbpath[:-1])
        if dbpath[-1] in d: return
        self.catdict[dbpath[-1]] = {}
  
    def _GenericHas(self,name):
        dbpath = self.canonicalise(name)
        d = self._walkPath(dbpath[:-1])
        return dbpath[-1] in d
  
    HasCategory = _GenericHas

    def NewObject(self,cat):
        dbpath = self.canonicalise(cat)
        d = self._walkPath(dbpath)
        objs = list(self.EnumObjects(cat))
        newid = NewId(objs)
        d[newid] = { }
        return newid

    def _GenericDelete(self,name):
        dbpath = self.canonicalise(name)
        d = self._walkPath(dbpath[:-1])
        del d[dbpath[-1]]

    DeleteCategory= _GenericDelete
    DeleteObject =  _GenericDelete
      
    HasObject = _GenericHas

    def EnumAttributes(self,obj):
       return self._GenericEnum(obj, lambda d,a: (not operator.isMappingType(d[a])) and  a[0] != '.')

    HasAttribute = _GenericHas

    def SetAttribute(self,attr,attrtype,parts):
        dbpath = self.canonicalise(attr)
        d = self._walkPath(dbpath[:-1])
        #Verify the StoreApi is being adhered too
        #  this will pick up issues in tests where we use dict_store.
        for p,v in parts.iteritems():
            if not isinstance(v,basestring): 
                raise StoreApiViolation("%s has part %s of type %s"%(attr,p,type(v)))
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
