
import re
from MysteryMachine.policies.SequentialId import NewId
from MysteryMachine.schema.MMObject import MMObject

class dict_store(object):
    """
    """

    invalidobj = re.compile("^\.")

    def concanicalise(self,name):
        return name.split(":")

    def __init__(self,owner):
        self.owner = owner
        self.catdict = { }

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
        return MMObject(obj,self.owner,self.GetObjStore(obj))
    
    def GetObjStore(self,obj):
        return dict_store_obj(self,obj)

    def DeleteCategory(self,cat):
        del self.catdict[cat]

    def EnumAttributes(self,object):
        path = self.concanicalise(object)
        for a in self.catdict[cat][newid].keys():
            yield a

    def HasAttribute(self,attr):
        path = self.concanicalise(attr)
        return path[2] in self.catdict[path[0]][path[1]]        


    def SetAttribute(self,attr,val):
        path = self.concanicalise(attr)
        self.catdict[path[0]][path[1]][path[2]]=val        

    def DelAttribute(self,attr):
        path = self.concanicalise(attr)
        del self.catdict[path[0]][path[1]][path[2]]
  

    def GetAttribute(self,attr):
        path = self.concanicalise(attr)
        return self.catdict[path[0]][path[1]][path[2]]

class dict_store_obj:
    def __init__(self,store,obj):
        self.store=store
        self.obj=obj

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
