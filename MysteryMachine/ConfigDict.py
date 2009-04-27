#!/usr/bin/env python
#   			ConfigDict.py - Copyright Roger Gammans
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
This module provides the wrapper functions around the various
configurations modules which MysteryMachine supports to 
provide a dict of dicts style interface.

Specifically this can implement a dict of [dict,lists ,str].

The core of Config dict is the section, each section may
have one of three special keys.
__dict__ => this section is another dictdict stored in the file specified
__list__ => this section is a list stored in the file specfied.
__value__ => The section is a plain value , as specified.

If any section has more than one of these values or one of these values
an other the behaviour is undefined.

Additionally a file may have a special section [__root__] , if so
the values in this section appear at the same level as the included
sections. If a section and a item in [__root__] have the same name 
the behavoiur is undefined.

"""

from ConfigParser import ConfigParser
import weakref
import exceptions

class ReadOnly(RuntimeError):
    pass

class MyParser(ConfigParser):
    """
    Simple override of ConfigParser to make case-sensitive
    """
    def optionxform(self,opt):
        return opt

class pyConfigDictSection(object):
 
    def __init__(self, cfg, section ,parent ,ro):
        self.cfg = cfg
        self.section = section
        self.parent  = parent
        self.readonly = ro

    def __getitem__(self, name):
        if self.cfg.has_option(self.section, name):
            return self.cfg.get(self.section,name)
        return None

    def __setitem__(self, name, value):
       if self.readonly: raise ReadOnly()  
       else: self.parent.modified=True
       
       self.cfg.set(self.section, name, str(value))

    def __delitem__(self, name):
        if self.readonly: raise ReadOnly()  
        else: self.parent.modified=True
      
        self.cfg.remove_option(self.section, name)

    def __iter__(self):
        for i in self.cfg.items(self.section):
            yield i


class pyConfigList(object):
    def  __init__(self,*args,**kwargs):
       # self.start = kwargs['start'] or 0
       # self.end   = kwargs['end'] or None
        
        self.dict   = pyConfigDict(*args,**kwargs)
    def read(self,f):
        self.filename=f
        self.dict.read(f)
        self.order  = sorted(self.dict)

    def __getitem__(self,pos):
        return self.dict[self.order[pos]]

    def __delitem__(self,pos,value):
        del self.dict[self.order[pos]]
        del self.order[pos]

    def __setslice__(self,i,j,y):
        for p in self.order[i:j]:
            self.dict[p] = y

    def __delslice__(self,i,j):
        names = copy(self.order[i:j])
        for p in names:
            del self.dict[p]
            self.order.remove(p)

    def __setitem__(self,pos,val):
        name=None
        if pos > len(self.order):
            #Todo support array extension
            pass
        else:
            name=self.order[pos]
        if name is None: raise KeyError()
        self.dict[name]=val

    def __iter__(self):
        for item in self.order:
            yield self.dict[item]

def argshift(args,default):
    value=default
    remaining=[]
    if len(args)>0:
        value=args[0]
        if len(args)>1:
            remaining=args[1:]

    return value,remaining 

class pyConfigDict(object):
        
    def __init__(self, *args, **kwargs):
        self.persistent,args = argshift(args,True)
        self.readonly ,args = argshift(args,False)
 
        self.cfg = MyParser(*args, **kwargs)
        if self.persistent:
           self._sections = weakref.WeakValueDictionary()
        else:
           self._sections = {}
        
    def  __del__(self):
        self.write()

    def testmode(self):
        self.write()
        self.persistent=False
        self.readonly=False

    def read(self,filename):
         #Store filename so write can work
         self.filename=filename
         self.cfg.read(filename)
         self.modified = False 
    
    def write(self,filename=None):
        f = None
        if filename is None:
            f = self.filename
        else:
            f =filename
        if self.persistent and self.modified:
            fp=file(f,"w")
            self.cfg.write(fp)
            fp.flush()



    def _getsection_object(self,type,name,file):
        if name in self._sections: return self._sections[name]
        section=type(self.persistent,self.readonly)
        section.read(file)
        self._sections[name]=section
        return section


    def __getitem__(self, name):
        if self.cfg.has_section(name):
            #Check for subconfigfile - need to 
            # cache this otherwise we lose updates.
            if self.cfg.has_option(name,"__dict__"):
                return self._getsection_object(pyConfigDict, name , self.cfg.get(name,"__dict__"))
            elif self.cfg.has_option(name,"__list__"):
                return self._getsection_object(pyConfigList, name , self.cfg.get(name,"__list__"))
            elif self.cfg.has_option(name,"__value__"):
                return self.cfg.get(name,"__value__")
            else:
                return pyConfigDictSection(self.cfg, name , self, self.readonly)
        else:
            #__root__ section allows values in the root.
            if self.cfg.has_option("__root__",name):
                return self.cfg.get("__root__",name)
        #Not found.
        return None

    def __setitem__(self, name, value):
        if self.readonly: raise ReadOnly()  
        else: self.modified=True

        try:
            for k, v in value:
                self.cfg.set(name, k, v)
        except:
            self.cfg.set("__root__",name,value)

    def __delitem__(self, name):
        if self.readonly: raise ReadOnly()
        else: self.modified=True

        self.cfg.remove_section(name)
        self.cfg.remove_option("__root__",name)

    def __iter__(self):
        # Suppres '__root__' section
        for s in  self.cfg.sections():
            if s != "__root__": yield s
        if self.cfg.has_section("__root__"):
            for k,v in self.cfg.items("__root__"):
                yield k
