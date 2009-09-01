
import re
from MysteryMachine.policies.SequentialId import NewId
from MysteryMachine.schema.MMObject import MMObject
from MysteryMachine.store import *

_dict_stores = dict()

class dict_store(Base):
    """
    A non-persistent Store which is design to be simple but complaint
    with the Mysterymachine interface - mainly intended for use in the
    test harnessees.
    """
    
    uriScheme = "dict"

    invalidobj = re.compile("^\.")

    def canonicalise(self,name):
        return name.split(":")

    @staticmethod
    def GetCanonicalUri(uri):
        return uri

    def __init__(self,uri,create = False):
        Base.__init__(self,uri,create)
        path = GetPath(uri)
        if path not in _dict_stores:
            _dict_stores[path] = { }

        self.catdict = _dict_stores[path]

    def EnumCategories(self):
        for k in self.catdict.keys():
            yield k

    def EnumObjects(self,cat):
        for o in self.catdict[cat].keys():
            if re.match(self.invalidobj,o) is None: yield o

    def NewCategory(self,cat,p):
        if cat in self.catdict: return
        self.catdict[cat] = {}
        self.catdict[cat][".parent"]=p
  

    def HasCategory(self,cat):
        return cat in self.catdict
  
    def NewObject(self,cat,p):
        objs = list(self.EnumObjects(cat))
        newid = NewId(objs)
        self.catdict[cat][newid] = { }
        self.catdict[cat][newid][".parent"] = p
        return newid

    def DeleteObject(self,object):
        dbpath = object.split(":")
        del self.catdict[dbpath[0]][dbpath[1]]


    def GetObject(self,obj):
        return self.GetObjStore(obj).GetObject()
    
    def GetObjStore(self,obj):
        return dict_store_obj(self,obj)

    def DeleteCategory(self,cat):
        del self.catdict[cat]

    def EnumAttributes(self,object):
        path = self.canonicalise(object)
        for a in self.catdict[cat][newid].keys():
            yield a

    def HasAttribute(self,attr):
        path = self.canonicalise(attr)
        val = path[2] in self.catdict[path[0]][path[1]]        
        #print  "%s is %s" % (path ,val)
        return val

    def SetAttribute(self,attr,val):
        #print "setting %s" % attr
        path = self.canonicalise(attr)
        self.catdict[path[0]][path[1]][path[2]]=val        

    def DelAttribute(self,attr):
        path = self.canonicalise(attr)
        del self.catdict[path[0]][path[1]][path[2]]
  

    def GetAttribute(self,attr):
        path = self.canonicalise(attr)
        print "PATH = %s " % path
        return self.catdict[path[0]][path[1]][path[2]]


class dict_store_obj:
    def __init__(self,store,obj):
        self.store=store
        self.obj=obj

    def GetObject(self):
        #print "Request for obj %s" % self.obj
        if not self.HasAttribute(":.self"):
            print "\tSetting system as %s " % self.store.get_owner()
            obj = MMObject(self.obj,self.store.get_owner(),self)
            self.SetAttribute(":.self",obj)
        else:
            obj = self.GetAttribute(":.self")
        return obj

    def GetAttribute(self,attr):
        return self.store.GetAttribute(self.obj + ":" +attr)
    
    def SetAttribute(self,attr,val):
        return self.store.SetAttribute(self.obj + ":" +attr,val)
   
    def DelAttribute(self,attr):
        return self.store.DelAttribute(self.obj + ":" +attr)

    def EnumAttributes(self):
        for a in self.store.EnumAttributes(self.obj):
            yield a

    def HasAttribute(self,attr):
        return self.store.HasAttribute(self.obj + ":" +attr)
