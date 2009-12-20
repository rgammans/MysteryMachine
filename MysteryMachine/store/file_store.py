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

from __future__ import with_statement

import re
import MysteryMachine.policies
from MysteryMachine.store import *
from MysteryMachine.store.Base import Base
from MysteryMachine.utils.locks import RRwLock

import os
import sys
import thread
import threading
import glob

policy = MysteryMachine.policies


class SafeFile(file):
    """
    This class implements Tytso's safe update mechanism.

    It can also take an R/W lock which it holds as a reader() until complete.
    The rationale for the reader lock is that multiple SafeFile() can share
    the lock . Then when you need the filesystem to be quesient stable and
    in a known state you acquire a writer lock.

    Taking a writer lock is also an effective filesystem barrier.
    
    See:
    http://thunk.org/tytso/blog/2009/03/12/delayed-allocation-and-the-zero-length-file-problem/#comment-1986http://thunk.org/tytso/blog/2009/03/12/delayed-allocation-and-the-zero-length-file-problem/#comment-1986
     
    """

    active   = { }
    dictlock = threading.Semaphore()

    def __init__(self,*args,**kwargs):
        self.finalname = args[0]
        (path , file ) = os.path.split(self.finalname)
        self.realname  = os.path.join(path,".new."+file)
        self.lock      = kwargs.get('lock')
        self.active    = self.__class__.active
        self.dictlock  = self.__class__.dictlock
        self.locksync  = threading.Semaphore(0)
        
        #FS Consistency.       
        try:
            os.stat(self.finalname)
        except:
            #Create sentinel file to ensure HasAttribute uptodate.
            f = open(self.finalname,"w")
            f.close()

        #FIXME
        # - what happens if realname already exists?
           
       #Keep track of the 'most recent' SafeFile for each
        # final file. This is to stop us clobbering a later
        # version with an earlier version in a racing close situation. 
        #
        # We also use this dict to maintain a consisent atomic filesystem
        # view to users who use our open_read() and/or unlink class methods.
        with self.dictlock:
            self.active[ self.finalname] = self
        newargs = [ self.realname ]
        newargs.append( *args[1:]) 
        super(SafeFile,self).__init__(*newargs)

    
    def threadFn(self):
        if self.lock:
            self.lock.acquire_read()
        #Let close() complete.
        self.locksync.release()
        self.flush()
        os.fsync(self.fileno())
        super(SafeFile,self).close()
        with self.dictlock:
            #Are we still the most recent update to this file.
            try:
                #Attribute as been deleted before fsync completed.
                if self.active[self.finalname] == "unlink":
                    os.unlink(self.realname) 
                    #Leave the dict entry in case of multiple outstanding 
                    # updates.
                if self.active[self.finalname] == self:
                    os.rename(self.realname,self.finalname)
                    del self.active[self.finalname]
            except KeyError, e: pass
        if self.lock:
            self.lock.release()
    
    def close(self):
        #TODO - launch this in subsidary thread for performance.
        # but note we need to keep a ref to this class. 
        thread.start_new_thread(self.threadFn, () )
        #Wait for thread to claim reader lock before releasing it here.
        self.locksync.acquire()
        #Release the lock in the main thread
        if self.lock:
            self.lock.release()

    @classmethod
    def open_read(cls,filename):
        """
        Open a file for reading. Normally opens filename - unless it is the process
        of being updated in which case you get the update file - so you should 
        see the most recent updates sent to the filesystem.
        """
        #With Posix file semantics we don't need to protect the actual reads as
        # the file handle stays bound to the actual inode.
        with cls.dictlock:
            if filename in cls.active:
                if cls.active[filename] == "unlink": raise IOError("File deleted")
                return open(cls.active[filename].realname)
            else:
                return open(filename)

    @classmethod
    def unlink(cls,filename):
        """
        Ensure we don't create a file called fileame if there is outstanding
        update for it  -  unlink the file if possible
        """
        with cls.dictlock:
            if filename in cls.active:
                cls.active[filename] = "unlink"


#We may want to change this to a subclass later 
# but at the moment factory method suffices.
#
# A subclass would all the set_value method to write back to the
# disc.
def FileStoreAttributePart(filename,partname):
    """
    Create a MMAttributePart from a filename
    """
    infile = SafeFile.open_read(filename)
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

    def __init__(self,*args,**kwargs):
        print args
        super(filestore,self).__init__(*args,**kwargs)
        uri = args[0]
        create = kwargs.setdefault('create',False)
        self.path = GetPath(uri)
        self._lock = RRwLock()
        if create:
          os.mkdir(self.path) 
    
    def get_path(self):
        return self.path

    def _getpath(self,expr):
        return expr.replace(":",os.sep )

    def EnumCategories(self):
        for dentry in os.listdir(self.path):
            #Skip directories which we don't manage.
            #Current plan is to have one directory per store inside the
            # system if multiple stores are used.
            if os.path.isdir(os.path.join(self.path , dentry )):
                #Ignore hidden directories
                if dentry[0] != '.': yield dentry

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
            if len(items[0]) > 0 and items[0] not in found:
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
            self._lock.acquire_read()
            file =SafeFile(filename,"w",lock = self._lock)
            file.write(value)
            file.close()
            #Ensure any RCS knows about the file.
            self.Add_file(filename)


    def DelAttribute(self,attr):
        attrele = self.canonicalise(attr)
        workuri= os.path.join(self.path,*(attrele[:3]))
        for f in glob.glob(workuri + ".*" ):
                #TODO Ensure python can't reorder 
                #     these two calls.
                SafeFile.unlink(f)
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

    def lock(self):
        self._lock.acquire_write()

    def unlock(self):
        self._lock.release()
