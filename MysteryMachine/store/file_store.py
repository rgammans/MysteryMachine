#!/usr/bin/env python
#   			file_store.py - Copyright Roger Gammans
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
from MysteryMachine.store import *
from MysteryMachine.store.Base import Base

import os
import sys
import thread
import glob

policy = MysteryMachine.policies


class SafeFile(file):
    """
    This class implements Tytso's safe update mechanism.

    See:
    http://thunk.org/tytso/blog/2009/03/12/delayed-allocation-and-the-zero-length-file-problem/#comment-1986http://thunk.org/tytso/blog/2009/03/12/delayed-allocation-and-the-zero-length-file-problem/#comment-1986
     
    """
    ##TODO - Allow to use as context manager which aborts the write and cleans
    #        up is the client code throws.
    def __init__(self,*args,**kwargs):
        self.finalname = args[0]
        (path , file ) = os.path.split(self.finalname)
        self.realname  = os.path.join(path,".new."+file)
        newargs = [ self.realname ]
        newargs.append( *args[1:]) 
        super(SafeFile,self).__init__(*newargs)

    
    def threadFn(self,otherself):
        self.flush()
        os.fdatasync(self.fileno())
        super(SafeFile,self).close()
        os.rename(self.realname,self.finalname)
    
    def close(self):
        #TODO - launch this in subsidary thread for performance.
        # but note we need to keep a ref to this class. 
        self.threadFn(self)


#We may want to change this to a subclass later 
# but at the moment factory method suffices.
#
# A subclass would all the set_value method to write back to the
# disc.
def FileStoreAttributePart(filename,partname):
    """
    Create a MMAttributePart from a filename
    """
    infile = file(filename,"r")
    data = infile.read()
    infile.close()
    print "FSAPi:data:%s"%data
    return {partname: data }

class filestore(Base):
    """
    A basic persistent Store which is designed to be simple but complaint
    with the Mysterymachine interface.

    There are no SCM methods attached to this store - will we
    create a mixin for the SCM actions.
    """
    
    uriScheme = "attrfile"

    invalidobj = re.compile("^\.")

    @staticmethod
    def GetCanonicalUri(uri):
        #Canonical filepath.
        return os.path.normcase(os.path.realpath(os.path.normpath(uri)))

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
  
    def NewCategory(self,category):
        catpath = os.path.join(self.path , category)
        os.mkdir(catpath)


    def NewObject(self,category):
        objs = list(self.EnumObjects(category))
        Id = policy.NewId(objs)
        catpath = os.path.join(self.path , category , Id)
        os.mkdir(catpath)
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
        objpath = self.canonicalise(object) 
        found = []
        for candidate in os.listdir(os.path.join(self.path,*objpath)):
            items = candidate.split(".")
            if items[0] not in found:
                found += [ items[0] ]
                yield items[0]
    
    def HasAttribute(self,attr):
        attrele = self.canonicalise(attr) 
        for candidate in os.listdir(os.path.join(self.path,*attrele[:2])):
            items = candidate.split(".")
            if items[0] == attrele[2]: return True

        return False

    def SetAttribute(self,attr,type,parts):
        """

        @param string attribute : 
        @return MMAttribute :
        @author
        """

        pathparts = list(self.canonicalise(attr))
        for partname,value in parts.items():
            filename = os.path.join(self.path,*pathparts)
            filename = "%s.%s.%s" % (filename,type,partname)
            file =SafeFile(filename,"w")
            file.write(value)
            file.close()
            #Ensure any RCS knows about the file.
            self.Add_file(filename)


    def DelAttribute(self,attr):
        attrele = self.canonicalise(attr)
        workuri= os.path.join(self.path,*(attrele[:3]))
        files = [  ]
        files += glob.glob(workuri + ".*" )
        files += glob.glob(".new." + workuri + ".*" )
        for f in files:
                os.remove(f)
        

    def GetAttribute(self,attr):
        attrele = self.canonicalise(attr)
        workuri = os.path.join(self.path,*(attrele[:2]))
        files = {}
        attrtype = None
        for candidate in os.listdir(workuri):
            items = candidate.split(".")
            print "GA:Candiate-items:%s" %items
            if items[0] == attrele[2]:
                if attrtype == None:
                    attrtype = items[1]
                if attrtype != items[1]:
                    raise exception("Inconsisent attrype in store")
                print "GA:Loading:%s-%s)" %(candidate,items[2])
                files.update(FileStoreAttributePart(os.path.join(workuri,candidate),items[2]))
        
        if attrtype is None: return None
        
        return (attrtype,files)
