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

import six
import re
import MysteryMachine.policies
from MysteryMachine.store import *
from MysteryMachine.Exceptions import *
from MysteryMachine.store.Base import Base
from MysteryMachine.utils.locks import RRwLock
from MysteryMachine.utils.path import make_rel 
import MysteryMachine.store.FileLogger 

import os
import sys
import threading
import glob
import errno
from contextlib import closing
 

policy = MysteryMachine.policies

CATEGORY_SENTINEL_NAME="..attrfile_category"
OBJECT_SENTINEL_NAME="..attrfile_object"


#We may want to change this to a subclass later 
# but at the moment factory method suffices.
#
# A subclass would all the set_value method to write back to the
# disc.
def FileStoreAttributePart(filename,partname):
    """
    Create a MMAttributePart from a filename
    """
    with closing(open(filename,"r")) as infile:
        data = infile.read()
        infile.close()
        logging.getLogger("MysteryMachine.Store.file_store").debug("APi:data:%s",data)
        return {partname: data }


#Redefine the log file to be outside the MM directory.
class FileLogger(MysteryMachine.store.FileLogger.FileLogger):
    def _get_logname(self,seq):
        basename = os.path.basename(self.home)
        parent   = os.path.realpath(os.path.join(self.home ,os.path.pardir))
        name =  ".%s.xaction.%s.log"%(basename,seq)
        return parent,name



class filestore(Base):
    """
    A basic persistent Store which is designed to be simple but complaint
    with the Mysterymachine interface.

    There are no SCM methods attached to this store - will we
    create a mixin for the SCM actions.


    Reading data during a transaction yields undefined values. It can 
    return pre-xaction values or current balues.
    """
    
    uriScheme = "attrfile"
    supports_txn = True

    invalidobj = re.compile("^\.")

    @staticmethod
    def GetCanonicalUri(uri):
        #Canonical filepath.
        return os.path.normcase(os.path.normpath(os.path.realpath(os.path.expanduser(uri))))

    def __init__(self,*args,**kwargs):
        self.logger = logging.getLogger("MysteryMachine.store.file_store")
        self.logger.debug( args)
        super(filestore,self).__init__(*args,**kwargs)
        uri = args[0]
        create = kwargs.setdefault('create',False)
        self.path = self.GetCanonicalUri(GetPath(uri))
        self._lock = RRwLock()
        if create:
          os.mkdir(self.path) 

        #Create a transaction Log object
        self.tlog = FileLogger(self.path, track_state = False)
        self.newobjs = []
        self.newcat  = []
        self.newattr = {} 
       
    def close(self,):
        self.tlog.close()
 
    def get_path(self):
        return self.path

    def start_store_transaction(self,):
        self._lock.acquire_read()
        try:
            self.tx = self.tlog.start_transaction()
        except Exception:
            self._lock.release()
            raise

    def commit_store_transaction(self,):
        self.tlog.commit_transaction(self.tx)
        self.newobjs = []
        self.newcat  = []
        self.newattr = {} 
        self._lock.release()

    def abort_store_transaction(self,):
        self.tlog.abort_transaction(self.tx)
        self.newobjs = []
        self.newcat  = []
        self.newattr = {} 
        self._lock.release()

    def EnumCategories(self):
        for dentry in os.listdir(self.path):
            #Skip directories which we don't manage.
            #Current plan is to have one directory per store inside the
            # system if multiple stores are used.
            if os.path.isdir(os.path.join(self.path , dentry )):
                if dentry != '.' or dentry !='..':
                    if os.path.isfile(os.path.join(self.path,dentry,CATEGORY_SENTINEL_NAME)):
                        yield dentry
                

    def EnumObjects(self,category):
        catpath = self.canonicalise(category)

        if catpath not in self.newcat:
            for dentry in os.listdir(os.path.join(self.path,*catpath)):
                objpath = catpath + [ dentry ]
                if not os.path.isdir(os.path.join(self.path,*objpath)) : continue
                sentinelpath = objpath + [ OBJECT_SENTINEL_NAME ]
                if not os.path.isfile(os.path.join(self.path,*sentinelpath)): continue
                yield dentry

        for obj in self.newobjs:
            #Search for obj created this txn, in this category.
            if obj[:len(catpath)] == catpath:
                yield obj[len(catpath)]

 
    def NewCategory(self,category):
        can_catpath = self.canonicalise(category)
        catpath = os.path.join( *can_catpath)
        try:
            self.tlog.Create_Dir(self.tx,catpath)
        except OSError as e:
            #Ignore Directory already exists errors .
            if e.errno != errno.EEXIST: raise
        except WindowsError as e:
            #Ignore Directory already exists errors .
            if e.errno != 183: raise
        else:
            sentinel = os.path.join(catpath ,CATEGORY_SENTINEL_NAME )
            self.tlog.Add_File(self.tx,sentinel,b"")
            self.Add_file(sentinel)
            self.newcat.append(can_catpath)

    def NewObject(self,category):
        can_catpath = self.canonicalise(category)
        #objs = list(self.EnumObjects(category))
        #Id = policy.NewId(objs)
        #can_catpath.append(Id)
        catpath = os.path.join( *can_catpath )
        sentinel = os.path.join(catpath ,OBJECT_SENTINEL_NAME )

        self.tlog.Create_Dir(self.tx,catpath)
        self.tlog.Add_File(self.tx,sentinel,b"")
        self.Add_file(sentinel)
        self.newobjs.append(can_catpath)
        #return Id

    def HasCategory(self,cat):
        objele = self.canonicalise(cat)
        if objele in self.newcat: return True

        path = os.path.join(self.path,*objele)
        sentinel = os.path.join(path ,CATEGORY_SENTINEL_NAME )
        return os.path.isdir(path) and os.path.isfile(sentinel)

    def HasObject(self,obj):
        objele = self.canonicalise(obj)
        if objele in self.newobjs: return True

        path = os.path.join(self.path,*objele)
        sentinel = os.path.join(path ,OBJECT_SENTINEL_NAME )
        return os.path.isdir(path) and os.path.isfile(sentinel)
    
    def DeleteObject(self,obj):
        objele = self.canonicalise(obj)
        dirname = os.path.join(*(objele))

        sentinel = os.path.join(dirname ,OBJECT_SENTINEL_NAME )
        self.tlog.Delete_File(self.tx,sentinel)
        self.Remove_file(sentinel)
        self.tlog.Delete_Dir(self.tx,dirname)
        if objele in self.newobjs: self.newobjs.remove(objele)

    def DeleteCategory(self,cat):
        catpath = os.path.join( cat)
        sentinel = os.path.join(catpath ,CATEGORY_SENTINEL_NAME )
        self.tlog.Delete_File(self.tx,sentinel)
        self.Remove_file(sentinel)
        self.tlog.Delete_Dir(self.tx,catpath)
        if cat in self.newcat: self.newcat.remove(cat)

    def EnumAttributes(self,object):
        objpath = self.canonicalise(object) 
        found = set()
        for candidate in os.listdir(os.path.join(self.path,*objpath)):
            #Don't enumerate store prive files.
            if candidate[:2] == '..':continue

            items = candidate.split(".")
            if not len(items[0]):
                del items[0]
                items[0] = "."+items[0]

            #Filename has a leading space fixup the elements
            if items[0] not in found:
                found.add(items[0] )
                filepath = objpath + [ candidate ]
                #Skip any Obj/Categories at this level
                if os.path.isdir(os.path.join(self.path,*filepath)) : continue
                self.logger.debug('FILE ATTRMAP: %r => %r\n'%(filepath,items[0]))
                yield items[0]
    
    def HasAttribute(self,attr):
        attrele = self.canonicalise(attr) 
        if tuple(attrele) in self.newattr: return True

        basepath = os.path.join(self.path,*attrele[:-1])
        self.logger.debug("using glob %s"% os.path.join(basepath,attrele[-1]+".*"))
        for candidate in glob.iglob(os.path.join(basepath,attrele[-1]+".*")):
            candidate_path = os.path.join(basepath,candidate)
            self.logger.debug("Considering %s as attr file"%candidate_path)
            if not os.path.isfile(candidate_path):
                 continue
            #items = candidate.split(".")
            return True

        return False

    def SetAttribute(self,attr,attrtype,parts):
        """

        @param string attribute : 
        @return MMAttribute :
        @author
        """

        pathparts = self.canonicalise(attr)
        filename_base = os.path.join(*pathparts)
        #Remove existing objects
        self.DelAttribute(attr)
        attrkey = tuple(pathparts)
        self.newattr[attrkey] = []
        for partname,value in parts.items():
            if not isinstance(value,six.binary_type): 
                raise StoreApiViolation("%s has part %s of type %s"%(attr,partname,type(value)))
            filename = "%s.%s.%s" % (filename_base,attrtype,partname)
            self.tlog.Add_File(self.tx,filename,value)
            #Ensure any RCS knows about the file.
            self.newattr[attrkey].append(filename)
            self.Add_file(filename)

        if not len(self.newattr[attrkey]):
            del self.newattr[attrkey]


    def DelAttribute(self,attr):
        attrele = self.canonicalise(attr)
        workuri= os.path.join(self.path, *(attrele))
        attrkey = tuple(attrele)

        if attrkey in self.newattr:
            parts_files = self.newattr[attrkey]
            del self.newattr[attrkey]
        else:
            parts_files = glob.glob(workuri + ".*" )

        for f in parts_files:
                #TODO Ensure python can't reorder 
                #     these two calls.
                fname, = make_rel(self.path,f)
                self.tlog.Delete_File(self.tx,fname)
                self.Remove_file(fname)
        

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
                    raise Exception("Inconsisent attrype in store")
                self.logger.debug( "GA:Loading:%s-%s)" %(candidate,items[2]))
                files.update(FileStoreAttributePart(os.path.join(workuri,candidate),items[2]))
        
        if attrtype is None: return None
        
        return (attrtype,files)

    def lock(self):
        self._lock.acquire_write()

    def unlock(self):
        self._lock.release()
