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
from MysteryMachine.Exceptions import *
from MysteryMachine.store.Base import Base
from MysteryMachine.utils.locks import RRwLock
from MysteryMachine.utils.path import make_rel 

import os
import sys
import thread
import threading
import glob
from contextlib import closing
 

policy = MysteryMachine.policies

CATEGORY_SENTINEL_NAME="..attrfile_category"
OBJECT_SENTINEL_NAME="..attrfile_object"


if sys.platform != "win32":
        # 
        # We don't use this class as it creates more problems than
        # it solves under windows.
        #
        # We don't need to be sure that the files have
        # truly hit the disk in any way - except when we save a pack
        # file.
        #
        # The exception to this is when we expect to be unable to 
        # recover using these temporary files after a crash.
        #
        # This has been enable by default for over a year and any
        # problems under linux have been safely found to be elsewhere,
        # it is however currently an issue under windows as the final
        # rename fails as opposed to clobbering the sentinel/previous 
        # file.
        #
        # Under windows there is Transactional I/O Api which provides 
        # MoveFileTransacted() which if called directly allows to replace
        # the file *and* guarantee atomcity, but is only available on
        # on Vista and greater.
        #
        # Or the Safe file update algorithm for windows is 
        # docuemnted here:
        # http://blogs.msdn.com/b/adioltean/archive/2005/12/28/507866.aspx
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
                self.realname  = os.path.join(path,"..new."+file)
                self.lock      = kwargs.get('lock')
                self.active    = self.__class__.active
                self.dictlock  = self.__class__.dictlock
                self.locksync  = threading.Semaphore(0)
                
                self.logger = logging.getLogger("MysteryMachine.Store.file_store.SafeFile")
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
                #Before we hand of to another thread ensure we have passed
                #all the data to the OS, so parallel file open()s get the 
                #correct data.
                self.flush()
                #Launch real close() in a thread.
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
                        try:
                            #There is a chance of a race here between testing
                            # if this file is still active and opening it's
                            # working file. - If Opening it working file fails
                            # we fail back to the mainfile.
                            rfile = open(cls.active[filename].realname)
                        except IOError, e:
                            self.logger.debug("%s - Failling back to main file %s"%(e,filename))
                            rfile = open(filename)
                        return rfile
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

else:
    class SafeFile(file):
          """
          This is a NULL class which implements the same API as above,
          except forwards the queries to the usual pyhton places
          """
          def __init__(self,*args,**kwargs):
               del kwargs['lock']
               super(SafeFile,self).__init__(*args,**kwargs)
        
          @classmethod
          def open_read(cls,filename):
                return open(filename)

          @classmethod
          def unlink(cls,filename):
               pass
 

#We may want to change this to a subclass later 
# but at the moment factory method suffices.
#
# A subclass would all the set_value method to write back to the
# disc.
def FileStoreAttributePart(filename,partname):
    """
    Create a MMAttributePart from a filename
    """
    with closing(SafeFile.open_read(filename)) as infile:
        data = infile.read()
        infile.close()
        logging.getLogger("MysteryMachine.Store.file_store").debug("APi:data:%s",data)
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
        return os.path.normcase(os.path.normpath(os.path.realpath(os.path.expanduser(uri))))

    def __init__(self,*args,**kwargs):
        self.logger = logging.getLogger("MysteryMachine.Store.file_store")
        self.logger.debug( args)
        super(filestore,self).__init__(*args,**kwargs)
        uri = args[0]
        create = kwargs.setdefault('create',False)
        self.path = self.GetCanonicalUri(GetPath(uri))
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
                if dentry[0] != '.':
                    if os.path.isfile(os.path.join(self.path,dentry,CATEGORY_SENTINEL_NAME)):
                        yield dentry
                

    def EnumObjects(self,category):
        catpath = self.canonicalise(category)
        for dentry in os.listdir(os.path.join(self.path,*catpath)):
            objpath = catpath + [ dentry ]
            if not os.path.isdir(os.path.join(self.path,*objpath)) : continue
            sentinelpath = objpath + [ OBJECT_SENTINEL_NAME ]
            if not os.path.isfile(os.path.join(self.path,*sentinelpath)): continue
            yield dentry
  
    def NewCategory(self,category):
        catpath = self.canonicalise(category)
        catpath = os.path.join(self.path , *catpath)
        try:
            os.mkdir(catpath)
        except OSError:
            ##FIXME Only discard file exist, still raise perm errors.
            pass #Eat file exists becuase we it can happen
        else:
            sentinel = os.path.join(catpath ,CATEGORY_SENTINEL_NAME )
            #Don't bother with safe file for this - a journalled FS
            # should be enough, since there is no data. 
            f=file(sentinel,"w")
            sentinel,  = make_rel(self.path,sentinel)
            self.Add_file(sentinel)

    def NewObject(self,category):
        objs = list(self.EnumObjects(category))
        Id = policy.NewId(objs)
        catpath = os.path.join(self.path , category , Id)
        os.mkdir(catpath)
        sentinel = os.path.join(catpath ,OBJECT_SENTINEL_NAME )
        #Don't bother with safe file for this - a journalled FS
        # should be enough, since there is no data. 
        f=file(sentinel,"w")
        sentinel, = make_rel(self.path,sentinel)
        self.Add_file(sentinel)
        return Id

    def HasCategory(self,cat):
        objele = self.canonicalise(cat)
        path = os.path.join(self.path,*objele)
        sentinel = os.path.join(path ,CATEGORY_SENTINEL_NAME )
        return os.path.isdir(path) and os.path.isfile(sentinel)

    def HasObject(self,obj):
        objele = self.canonicalise(obj)
        path = os.path.join(self.path,*objele)
        sentinel = os.path.join(path ,OBJECT_SENTINEL_NAME )
        return os.path.isdir(path) and os.path.isfile(sentinel)
    
    def DeleteObject(self,object):
        dir = os.path.join(self.path,self._getpath(object))
        sentinel = os.path.join(dir ,OBJECT_SENTINEL_NAME )
        os.unlink(sentinel)
        self.Remove_file(sentinel)
        os.rmdir(dir)

    def DeleteCategory(self,cat):
        catpath = os.path.join(self.path , cat)
        sentinel = os.path.join(catpath ,CATEGORY_SENTINEL_NAME )
        os.unlink(sentinel)
        self.Remove_file(sentinel)
        os.rmdir(catpath)

    def EnumAttributes(self,object):
        objpath = self.canonicalise(object) 
        found = []
        for candidate in os.listdir(os.path.join(self.path,*objpath)):
            items = candidate.split(".")
            #Filename has a leading space fixup the elements
            if len(items[0]) > 0 and items[0] not in found:
                found += [ items[0] ]
                #Skip any Obj/Categories at this level
                filepath = objpath + [ candidate ]
                if os.path.isdir(os.path.join(self.path,*filepath)) : continue
                yield items[0]
    
    def HasAttribute(self,attr):
        attrele = self.canonicalise(attr) 
        basepath = os.path.join(self.path,*attrele[:-1])
        for candidate in glob.iglob(os.path.join(basepath,attrele[-1]+".*")):
            candidate_path = os.path.join(basepath,candidate)
            if not os.path.isfile(candidate_path):
                 continue
            items = candidate.split(".")
            return True

        return False

    def SetAttribute(self,attr,attrtype,parts):
        """

        @param string attribute : 
        @return MMAttribute :
        @author
        """

        pathparts = list(self.canonicalise(attr))
        #Remove existing objects
        self.DelAttribute(attr)
        for partname,value in parts.items():
            if not isinstance(value,basestring): 
                raise StoreApiViolation("%s has part %s of type %s"%(attr,partname,type(value)))
            filename = os.path.join(self.path,*pathparts)
            filename = "%s.%s.%s" % (filename,attrtype,partname)
            self._lock.acquire_read()
            with closing(SafeFile(filename,"w",lock = self._lock)) as file:
                file.write(value)

            #Ensure any RCS knows about the file.
            file , = make_rel(self.path,filename)
            self.Add_file(file)


    def DelAttribute(self,attr):
        attrele = self.canonicalise(attr)
        workuri= os.path.join(self.path,*(attrele))
        for f in glob.glob(workuri + ".*" ):
                #TODO Ensure python can't reorder 
                #     these two calls.
                SafeFile.unlink(f)
                os.remove(f)
                f , = make_rel(self.path,f)
                self.Remove_file(f)

    def GetAttribute(self,attr):
        attrele = self.canonicalise(attr)
        workuri = os.path.join(self.path,*(attrele[:-1]))
        files = {}
        attrtype = None
        for candidate in glob.iglob(os.path.join(workuri,attrele[-1]+".*")):
            adir, candidate =os.path.split(candidate)
            items = candidate.split(".")
            if items[0] == "":
                items = items[1:]
                items[0] = "."+items[0]
            if len(items) < 3: 
                #If there aren't two periods in the filename then it isn't
                # an attribute part- they might be objects or sentinel files
                # unless we are on windows and
                # someone tried to use and empty part name. Which is
                # why we don't use empty part names, as they cause trailing 
                # periods. which windows doesn't like
                continue
            self.logger.debug( "GA:Candiate-items:%s" %items)
            if items[0] == attrele[-1]:
                if attrtype == None:
                    attrtype = items[1]
                if attrtype != items[1]:
                    raise exception("Inconsisent attrype in store")
                self.logger.debug( "GA:Loading:%s-%s)" %(candidate,items[2]))
                files.update(FileStoreAttributePart(os.path.join(workuri,candidate),items[2]))
        
        if attrtype is None: return None
        
        return (attrtype,files)

    def lock(self):
        self._lock.acquire_write()

    def unlock(self):
        self._lock.release()
