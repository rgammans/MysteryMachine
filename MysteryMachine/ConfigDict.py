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

class pyConfigDictSection(object):
 
    def __init__(self, cfg, section):
        self.cfg = cfg
        self.section = section

    def __getitem__(self, name):
        if self.cfg.has_option(self.section, name):
            return self.cfg.get(self.section,name)
        return None

    def __setitem__(self, name, value):
        self.cfg.set(self.section, name, str(value))

    def __delitem__(self, name):
        self.cfg.remove_option(self.section, name)

    def __iter__(self):
        return self.cfg.items(self.section)


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
        if self.pos > len(self.order):
            #Todo support array extension
            pass
        else:
            name=self.order[pos]
        if name is None: raise KeyError()
        self.dict[name]=val

class pyConfigDict(object):
    def __init__(self, *args, **kwargs):
        self.cfg = ConfigParser(*args, **kwargs)

    def read(self,filename):
         #Store filename so write can work
         self.filename=filename
         self.cfg.read(filename)

    def __getitem__(self, name):
        if self.cfg.has_section(name):
            #Check for subconfigfile - need to 
            # cache this otherwise we lose updates.
            if self.cfg.has_option(name,"__dict__"):
                result = pyConfigDict()
                result.read(self.cfg.get(name,"__dict__"))
                return result
            elif self.cfg.has_option(name,"__list__"):
                result = pyConfigList()
                result.read(self.cfg.get(name,"__list__"))
                return result
            elif self.cfg.has_option(name,"__value__"):
                return self.cfg.get(name,"__value__")
            else:
                return pyConfigDictSection(self.cfg, name)
        else:
            #__root__ section allows values in the root.
            if self.cfg.has_option("__root__",name):
                return self.cfg.get("__root__",name)
        #Not found.
        return None

    def __setitem__(self, name, value):
        for k, v in value:
            self.cfg.set(name, k, v)

    def __delitem__(self, name):
        self.cfg.remove_section(name)

    def __iter__(self):
        # Suppres '__root__' section
        for s in  self.cfg.sections():
            if s != "__root__": yield s
        if self.cfg.has_section("__root__"):
            for k,v in self.cfg.items("__root__"):
                yield k
