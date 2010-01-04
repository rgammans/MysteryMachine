
import re
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

    def EnumCategories(self):
        for k in self.catdict.keys():
            if k[0] != '.': yield k

    def EnumObjects(self,cat):
        for o in self.catdict[cat].keys():
            if re.match(self.invalidobj,o) is None: yield o

    def NewCategory(self,cat):
        if cat in self.catdict: return
        self.catdict[cat] = {}
  

    def HasCategory(self,cat):
        return cat in self.catdict
  
    def NewObject(self,cat):
        objs = list(self.EnumObjects(cat))
        newid = NewId(objs)
        self.catdict[cat][newid] = { }
        return newid

    def DeleteCategory(self,cat):
        del self.catdict[cat]

    def DeleteObject(self,object):
        dbpath = object.split(":")
        del self.catdict[dbpath[0]][dbpath[1]]

    def HasObject(self,obj):
        path = self.canonicalise(obj)
        return path[1] in self.catdict[path[0]]       

    def EnumAttributes(self,object):
        path = self.canonicalise(object)
        for a in self.catdict[path[0]][path[1]].keys():
            if a[0] != '.': yield a

    def HasAttribute(self,attr):
        path = self.canonicalise(attr)
        self.logger.debug( "CHECKPATH = %s " % path)
        val = path[2] in self.catdict[path[0]][path[1]]        
        #self.logger.debug(  "%s is %s" % (path ,val))
        return val

    def SetAttribute(self,attr,type,parts):
        #self.logger.debug( "setting %s" % attr)
        path = self.canonicalise(attr)
        self.catdict[path[0]][path[1]][path[2]]=(type,parts)

    def DelAttribute(self,attr):
        path = self.canonicalise(attr)
        del self.catdict[path[0]][path[1]][path[2]]
  

    def GetAttribute(self,attr):
        path = self.canonicalise(attr)
        self.logger.debug( "GETPATH = %s " % path)
        return self.catdict[path[0]][path[1]][path[2]]


    def lock(self):
        #FIXME - Lock store and save to uri on disk...
        pass

    def unlock(self):
        pass
