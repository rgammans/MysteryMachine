#!/usr/bin/env python
#   			hgfile_store.py - Copyright Roger Gammans
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


import re
import MysteryMachine.policies
from MysteryMachine.schema.MMObject import MMObject
from MysteryMachine.store import *
from MysteryMachine.store.Base import Base

import os

import thread

policy = MysteryMachine.policies

class SafeFile(file):
    """
    This class implements Tytso's safe update mechanism.

    See:
    http://thunk.org/tytso/blog/2009/03/12/delayed-allocation-and-the-zero-length-file-problem/#comment-1986http://thunk.org/tytso/blog/2009/03/12/delayed-allocation-and-the-zero-length-file-problem/#comment-1986
     
    """

    def __init__(self,*args):
        self.finalname = args[0]
        args[0] = ".new."+args[0]
        self.realname =  args[0]
        super(SafeFile,self).__init__(*args)

    
    def threadFn(self,otherself):
        self.flush()
        os.fdatasync(self.fileno)
        super(SafeFile,self).close()
        os.rename(self.realname,self.finalname)
    
    def close(self): 
        thread.start_new_thread(self.threadFn,self)

class filestore(Base):
    """
    A basic persistent Store which is designed to be simple but complaint
    with the Mysterymachine interface.

    There are no SCM methods attached to this store - will we
    create a mixin for th`e SCM actions.
    """
    
    uriScheme = "hgstore"

    invalidobj = re.compile("^\.")

    @staticmethod
    def GetCanonicalUri(uri):
        #FIXME# Canonical filepath...
        return uri

    def __init__(self,uri,create = False):
        Base.__init__(self,uri,create)
        self.path = GetPath(uri)
        if create:
          os.mkdir(self.path) 

    def _getpath(self,expr):
        return expr.replace(":",os.sep )

    def EnumCategories(self):
        for dentry in os.listdir(self.path):
            #Skip directories which we don't manage.
            #Current plan is to have one directory per store inside the
            # system if multiple stores are used.
            if os.path.isdir(os.path.join(self.path , dentry )):
                yield dentry

    def EnumObjects(self,category):
        for dentry in os.listdir(os.path.join(self.path,category)):
            yield dentry
  
    def NewCategory(self,category,defparent = None):
        catpath = os.path.join(self.path , category)
        os.mkdir(catpath)
        if defparent != None:
            parentfile = SafeFile(os.path.join(catpath,".parent","w"))
            parentfile.write(defparent)
            parentfile.close()

    def NewObject(self,category,parent):
        objs = list(self.EnumObjects(category))
        Id = policy.NewId(objs)
        catpath = os.path.join(self.path , category , Id)
        os.mkdir(catpath)
        if parent != None:
            parentfile = SafeFile(os.path.join(catpath,".parent","w"))
            parentfile.write(parent)
            parentfile.close()
        return Id

    def HasCategory(self,cat):
        path = os.path.join(self.path,cat)
        return os.path.isdir(path)
 
    def HasObject(self,obj):
        objele = self.canonicalise(obj)
        path = os.path.join(self.path,*objele)
        return os.path.isdir(path)
    
    def DeleteObject(self,object):
        dir = os.path.join(self.path,self._getpath(object))
        os.rmdir(dir)

    def DeleteCategory(self,cat):
        catpath = os.path.join(self.path , cat)
        os.rmdir(catpath)

    def EnumAttributes(self,object):
        pass

    def HasAttribute(self,attr):
        pass

    def SetAttribute(self,attr,val):
        pass

    def DelAttribute(self,attr):
        pass

    def GetAttribute(self,attr):
        pass
