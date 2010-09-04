
import re
import operator
from MysteryMachine.policies.SequentialId import NewId
from MysteryMachine.store import *
from MysteryMachine.store.Base import Base 

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
        if path not in _dict_stores:
            _dict_stores[path] = { }

        self.catdict = _dict_stores[path]

    def _walkPath(self,dbpath):
        head = self.catdict
        for ele in dbpath:
            head = head[ele]
        return head

    def EnumCategories(self):
        for k in self.catdict.keys():
            if not operator.isMappingType(self.catdict[k]): continue 
            if k[0] != '.': yield k

    def EnumObjects(self,cat):
        dbpath = self.canonicalise(cat)
        d = self._walkPath(dbpath)
        for o in d.keys():
            if re.match(self.invalidobj,o) is None: yield o

    def NewCategory(self,cat):
        dbpath = self.canonicalise(cat)
        d = self._walkPath(dbpath[:-1])
        if dbpath[-1] in d: return
        self.catdict[dbpath[-1]] = {}
  

    def HasCategory(self,cat):
        dbpath = self.canonicalise(cat)
        d = self._walkPath(dbpath[:-1])
        return dbpath[-1] in d
  
    def NewObject(self,cat):
        dbpath = self.canonicalise(cat)
        d = self._walkPath(dbpath)
        objs = list(self.EnumObjects(cat))
        newid = NewId(objs)
        d[newid] = { }
        return newid

    def DeleteCategory(self,cat):
        dbpath = self.canonicalise(cat)
        d = self._walkPath(dbpath[:-1])
        del d[dbpath[-1]]

    def DeleteObject(self,object):
        dbpath = object.split(":")
        d = self._walkPath(dbpath[:-1])
        del d[dbpath[-1]]

    def HasObject(self,obj):
        dbpath = self.canonicalise(obj)
        d = self._walkPath(dbpath[:-1])
        return dbpath[-1] in d       

    def EnumAttributes(self,object):
        dbpath = self.canonicalise(object)
        d = self._walkPath(dbpath)
        path = self.canonicalise(object)
        for a in d:
            #Skip Objs/Categories at this level
            if operator.isMappingType(d[a]): continue
            if a[0] != '.': yield a

    def HasAttribute(self,attr):
        dbpath = self.canonicalise(attr)
        d = self._walkPath(dbpath[:-1])
        self.logger.debug( "CHECKPATH = %s " % dbpath)
        return dbpath[-1] in d       

    def SetAttribute(self,attr,type,parts):
        dbpath = self.canonicalise(attr)
        d = self._walkPath(dbpath[:-1])
        #self.logger.debug( "setting %s" % attr)
        d[dbpath[-1]]=(type,parts)

    def DelAttribute(self,attr):
        dbpath = attr.split(":")
        d = self._walkPath(dbpath[:-1])
        del d[dbpath[-1]]

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
