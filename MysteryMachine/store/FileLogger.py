#!/usr/bin/env python
#   			FileLogger.py - Copyright R G Gammans 
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
#


"""
This module is an attempt to implement a simplified transactional file store
on top of POSIX file semantics.

The work is done by the FileLogger class, which takes a directory name in which
it assumes all the files it manages live. This class creates a journal file
which is fdatasync()'d before the transactions are committed to the filestore.

Currently the class does *not* support overlapping transactions and 
has a limited number of update operations, although it should
be easier to add update operation type by creating an appropriate class, but I
currently have no plans to support overlapping transactions.

Operations are pushed to the filesystem on commit, and the filesystems integrity
is relied on for read and other behaviours, however the Journal file is used
to support redo in the case of a crash. No UNDO logging is preformed.

This has a number of consequences:-
    1. This module works only as well as fdatasync/fsync on your platform.
        It does not yet call fcntl(FULL_SYNC) on macos.

    2. You cannot reliably read back the upto date state of a file
       which has changed during the current transaction. It is up to
       you to implement a higher layer.

    3. Drive buffering may make this somewhat u/s. YMMV. This depends on the
       qualit of your os's implentation of fsync.

"""

SystemErrors =  []
try:
    SystemErrors.append(OSError)
except Exception: pass
try:
    SystemErrors.append(WindowsError)
except Exception: pass

SystemErrors = tuple(SystemErrors)


#Set this to false to use the Posix FS version
#under windows vista and greater.
TxF_Enabled = True



import thread
import threading
import time
import os
import stat
import errno
import sys
import contextlib
import glob
from itertools import izip, chain
from MysteryMachine.utils.locks import RWLock
from MysteryMachine.utils.path import make_rel

import logging

modlogger = logging.getLogger("MysteryMachine.store.FileLogger")

#TODO Make this a configurable.
SYNC_WAIT_TIME = 10 #seconds
BUFFER_SZ      = 4096 #One Adv disk block , and the block size of many FS instances.
MINIMUM_LOGSZ  = 1048576
DEFAULT_LOGSZ  = 1048576*16

class RecoveryError(RuntimeError): pass
class OverlappedTransaction(RuntimeError): pass

class InvalidTransaction(RuntimeError): pass


try:
     fdatasync = os.fdatasync
except AttributeError:
     fdatasync = os.fsync

class directory(object):
    """A class for directory which provides fileno() method so direcories can be fsync,
    and handed the same as file in lists of things to call fsync on."""
    def __init__(self,path):
        #Windows doesn't let us open directories like this. The documentation
        # I have found so far is unclear on whether < XP requires a seperate
        #call to sync directory data. >XP we sould you transacted calls anyway.

		#And this doesn't work < XP anyway- due to dir BUSY locks.	
        if sys.platform != 'win32':
           self.fd = os.open(path, os.O_RDONLY)
        else: self.fd = None
    def close(self,):
        if self.fd is not None: os.close(self.fd)
    def fileno(self,):
        return self.fd

_operation_type_map = { }

class _OperationMeta(type):
    def __init__(self,name,bases,ns):
        super(_OperationMeta,self).__init__(name,bases,ns)
        if name != 'Tranasction': 
            _operation_type_map[self.operation_type] = self

class JournaledOperation(object):
    """An base class for Transaction objects.

       Each record in our Transction log should be a record discribing
       an object of this type.
    """

    __metaclass__ = _OperationMeta
    operation_type = "base"

    def __init__(self,*args,**kwargs):
        modlogger.debug( "JO:init")
        self.opid     = int(args[0])
        self.optype   = self.__class__.operation_type
        self.completed = False
        self.sync_wait_time = SYNC_WAIT_TIME
        self.callback = None
        self.fobjs = [ ]
        self.recovery_mode = kwargs.get('recovery_mode',False)

    def __repr__(self,):
        return "<Operation Type:%s, Id:%i>"%(self.operation_type,self.opid)


    def _do(self,):
        raise RuntimeError("Base Transaction instance can't be done!")
  
    def update_state(self,state_obj):
        modlogger.warn("Base Transaction instance asked to update state")


    def do(self,**kwargs):
        self._do()
        sync = kwargs.get('sync',False)
        if sync:
            self.complete_txn(**kwargs)
        else:
            thread.start_new_thread(self.complete_txn, () ,kwargs )

    def dont_do(self,**kwargs):
        if self.callback is not None:
            self.callback(self.opid)
        else:
            modlogger.error("Abort before callback set")

    def set_callback(self,cbk):
        self.callback = cbk

    def complete_txn(self,**kwargs):
        """Wait for the transaction to be saved to persistent store"""
        
        sync = kwargs.get('sync',False)
        callback = kwargs.get('callback',self.callback)
        #POSIX has no IO completion event for the condition
        # which this function is design to block waiting for.
        # So we wait a reasonable amount of time in the Hope the
        # OS as already done it for us then we call fsync() as
        # a blocking operation to wait for it to do so. (and triggering
        # it early). 
        #
        # By waiting we hope that the OS has already completed the
        # action - and we are not causing any additional performance
        # impact by requesting the fsync..
        #
        # We skip the wait though if the do() was called
        # synchronously - say during a log replay.
        if not sync and self.fobjs: time.sleep(self.sync_wait_time)
        for f in self.fobjs:
            fd = f.fileno()
            if fd is not None:
                os.fsync(fd)
            f.close()
 
        self.completed = True
        if callback: callback(self.opid)


    def __str__(self,):
        v = ""
        v += (str(self.opid) + '\0')
        v += (self.operation_type + '\0')
        return v

    def __len__(self,):
        v = 0 
        v += len(str(self.opid) )
        v += len(self.operation_type )
        return v
 
    @classmethod
    def load(cls,data, recovery_mode = False):
        opid = _read_delimited_field(data)
        operation_type = _read_delimited_field(data)
        modlogger.debug( "loading: %s,%s"%(opid,operation_type))
        return _operation_type_map[operation_type].load(opid,data, recovery_mode = recovery_mode)


 
class CheckpointOperation(JournaledOperation):
    """A special non-tranasction transaction.

     This is written to the log file to record completed commits.
     It is used during the recovery phase, to determine the start point
     for playback."""

    operation_type = "checkpoint"

    def __init__(self,*args,**kwargs):
        self.chkpoint_id =  args[0]
        super(CheckpointOperation,self).__init__(*(args[1:]),**kwargs)

    def _do(self,):
        return

    def __str__(self,):
        v = super(CheckpointOperation,self).__str__()
        v += str(self.chkpoint_id) +'\0'
        return v

    def __len__(self,):
        v = super(CheckpointOperation,self).__len__() + 1
        v += len(str(self.chkpoint_id))
        return v

    def update_state(self,state):
        #Doesn't modify the state
        pass

    @classmethod
    def load(cls,opid,data, recovery_mode = False):
        chkpoint_id = _read_delimited_field(last_checkpointed)
        return cls(chkpoint_id,opid, recovery_mode = recovery_mode)
 

class ReplaceAll_Operation(JournaledOperation):
    operation_type = "replace_all"
    def __init__(self,*args,**kwargs):
        #Placeholder for future expansion.
        self.content = args[1]
        self.target = args[0]
        if type(self.content) is not str:
            raise TypeError("File contents must be a byte stream")

        super(ReplaceAll_Operation,self).__init__(*(args[2:]),**kwargs)
        self.fobj    = None

    def _do(self,):
        modlogger.debug( "doing")
        #If we are creating a file we need to fsync the directory
        try:
            os.stat(self.target)
        except OSError as  e:
            if e.errno == errno.ENOENT:
                self.fobjs += [directory(os.path.dirname(self.target))]

        self.fobj = open(self.target,"w+")
        self.fobjs += [ self.fobj ]
        self.fobj.truncate(0)
        self.fobj.write(self.content)
        self.fobj.flush()

    def update_state(self,state):
        if state.dir_exists(self.target):
            raise OSError(errno.EISDIR)
        if not state.dir_exists(os.path.dirname(self.target)):
            raise OSError(errno.ENOENT)

        state.add_file(self.target)
        

    def __str__(self,):
        v = super( ReplaceAll_Operation ,self).__str__()
        length = len(self.content) + len(self.target) + 1
        v += (str(length) + '\0')
        v += (self.target.encode('ascii') + '\0')
        v += self.content
        
        return v

    def __len__(self,):
        v = 0 
        v += len(str(self.opid) )
        v += len(self.operation_type )
        length = len(self.content) + len(self.target) + 4
        v += len(str(length) )
        v += length
        return v
 
    @classmethod
    def load(cls,opid,data, recovery_mode = False):
        length = int(_read_delimited_field(data))
        target = _read_delimited_field(data)
        content = _read_fixedlength(data,length - len(target) -1)
        return cls(target,content,opid, recovery_mode = recovery_mode)

class SingleDentry_Operation(JournaledOperation):
    def __init__(self,*args,**kwargs):
        #Placeholder for future expansion.
        self.target = os.path.normpath(args[0])
        super(SingleDentry_Operation,self).__init__(*(args[1:]),**kwargs)
        self.fobj    = None
    def __str__(self,):
        v = super( SingleDentry_Operation ,self).__str__()
        v += (self.target.encode('ascii') + '\0')
        return v

    def __len__(self,):
        v = super( SingleDentry_Operation ,self).__len__()
        v += len(str(self.target) ) + 1
        return v
 
    def add_fds(self,):
        dname = os.path.dirname(self.target)
        if dname == self.target:
            dname = os.path.dirname(self.target[:-1])
        
        self.fobjs += [ directory(dname) ]
 
    @classmethod
    def load(cls,opid,data, recovery_mode = False):
        target = _read_delimited_field(data)
        return cls(target,opid, recovery_mode = recovery_mode)



class DeleteFile_Operation(SingleDentry_Operation):
    operation_type = "delete_file"
    def _do(self,):
        self.add_fds()
        try:
            os.unlink(self.target)
        except SystemErrors as e:
            import errno
            #Ignore missing file during recovery. 
            if not self.recovery_mode and e.errno != errno.ENOENT:
                raise

    def update_state(self,state):
        if state.dir_exists(self.target):
            raise OSError(errno.EISDIR)

        if state.file_exists(self.target):
            state.unlink_file(self.target) 
        else: raise OSError(errno.ENOENT)

class DeleteDir_Operation(SingleDentry_Operation):
    operation_type = "delete_dir"
    def _do(self,):
        self.add_fds()
        os.rmdir(self.target)

    def update_state(self,state):
         if state.file_exists(self.target):
            raise OSError(errno.ENOTDIR)

         if not state.dir_exists(self.target):
            raise OSError(errno.ENOENT)

         if state.dir_empty(self.target):
            raise OSError(errno.ENOTEMPTY)
         else:
            state.unlink_dir(self.target) 

class CreateDir_Operation(SingleDentry_Operation):
    operation_type = "create_dir"
    def _do(self,):
        self.add_fds()
        try:
            os.mkdir(self.target)
            #print "mkdir %s"%self.target
        except OSError as e:
            #Ignore Directory already exists errors .
            if e.errno != errno.EEXIST:
               raise

    def update_state(self,state):
        if state.file_exists(self.target):
            raise OSError(errno.EEXIST)
        if not state.dir_exists(os.path.dirname(self.target)):
            raise OSError(errno.ENOTFOUND)

        state.add_dir(self.target)
 

class GenericTxOperation(object):
    """Mixin class to provide for transaction/start end markers."""
    
    def __init__(self,*args,**kwargs):
        modlogger.debug( "creating :%s"%object.__repr__(self))
        self.txn_id =  args[0]
        super(GenericTxOperation,self).__init__(*(args[1:]),**kwargs)

    def _do(self,):
        return

    def __str__(self,):
        v = super(GenericTxOperation ,self).__str__()
        v += str(self.txn_id) +'\0'
        return v

    def __len__(self,):
        v = super(GenericTxOperation ,self).__len__() + 1
        v += len(str(self.txn_id))
        return v

    def update_state(self,state):
        #also doesn't modify state.
        pass

    @classmethod
    def load(cls,opid,data, recovery_mode = False):
        txn_id = _read_delimited_field(data)
        return cls(opid,txn_id, recovery_mode = recovery_mode)
 
class StartTxOperation(GenericTxOperation,JournaledOperation):
    """Operation which marks the beginning of a Txn"""
    operation_type = "start_txn"

class EndTxOperation(GenericTxOperation,JournaledOperation):
    """Operation which marks the commit of a Txn"""
    operation_type = "end_txn"
      
class AbortTxOperation(GenericTxOperation,JournaledOperation):
    """Operation which marks the abort of a Txn"""
    operation_type = "abort_txn"

 
#Helper functions for parsign the logfile.
def _read_delimited_field(d):
    """d is an iterable of octects from the logfile

       @returns integer length of the content.
    """
    val = d.next()
    while val[-1] != '\0':
        val += d.next()

    modlogger.debug( "read:%s"%val[:-1])
    return val[:-1]

def _read_fixedlength(d,n):
    def _get(*args): return d.next()
    return ''.join(map(_get,range(n)))


class Dentry(object):
    def __init__(self,name,dtype, contents = None):
        self.name = name
        self.dtype = dtype

        if dtype == 'f': contents = None
        self.contents = contents

    def __contains__(self,name):
        return name in self.contents

    def __getitem__(self,name):
        return self.contents[name]

def File_Entry(fname):
    return Dentry(fname,'f') 

def Dir_Entry(fname,contents ):
    return Dentry(fname,'d', contents = contents) 

def _parent(pathname):
    pathname = os.path.dirname(pathname)
    return os.path.normpath(pathname)

class LazyFSMap(object):
    def __init__(self,home):
        self.home = home
        self.mymap = {}

    def __getitem__(self,item):
        if item in self.mymap: return self.mymap[item]
        self._fetch(item)
        return self.mymap[item]

    def __contains__(self,item):
        #Handle simple case first
        if item in self.mymap: return True 
        try:
            self._fetch(item)
        except KeyError:
            return False

        return item in self.mymap

    def __setitem__(self,name,item):
        #check name consistency.
        if os.path.basename(name) != item.name:
            raise ValueError(item.name)

        #Ensure Map updated to allow item to exist.
        try:
            dummy = self[name]
        except KeyError: pass
        #Get parent so add to parents contents and
        #base map.
        pdir = self[_parent(name)]
        pdir.contents[item.name] = item
        self.mymap[name] = item

    def __delitem__(self,name):
        #Fetch item in void context to populate parent tree
        self.mymap[name]
        pdir = self[_parent(name)]
        if pdir.contents: del pdir.contents[os.path.basename(name)]
        del self.mymap[name]
 
    def _fetch(self,name):
        """Internal function to fill the internal state from filing system os calls"""
        #
        #Find name's parent and fill that first....
        if name != '.':
            parent = _parent(name)
            pdentry = self[parent]
            if pdentry.contents is not None or pdentry.dtype == 'f':
                #Parent dentry is a file or has been enumareted.
                #So we should not have got here. This almost certainly
                #means that name does nto exist.
                raise KeyError(name)
        else:
            parent = ''
            pdentry = None 

        
        ##Get entries iterable from FS
        entries = []
        try:
           entries = os.listdir(os.path.join(self.home,parent))
        except OSError as e:
           if e.errno != errno.ENOENT:
              raise
           else:
              modlogger.debug("Cant reach:Non existent directory found in it's own parent.")
              return

        #Make a dict of files a dir entries., adnd put itoput global name list
        contents = {}
        for dentry in entries:
            #Ignore private file reserved for internal use.
            if dentry[:2] == "..": continue

            sr = os.stat(os.path.join(self.home,parent,dentry))
            if stat.S_ISDIR(sr.st_mode):
                 contents[dentry] = Dentry(dentry , 'd')
            elif stat.S_ISREG(sr.st_mode):
                 contents[dentry] = Dentry(dentry , 'f')

            self.mymap[os.path.join(parent,dentry)] = contents[dentry]

        #Put the parents contents in it's own dentry entry too.`
        if pdentry: pdentry.contents = contents
        #Initiallise our root directory
        else:
            self.mymap['.'] = Dir_Entry('.',contents)
            #print contents

    def _entry_exists(self,dname,type_expected):
        r = False
        if dname in self:
            dntry = self[dname]
            r = (dntry.dtype == type_expected)
        return r
        
    def dir_exists(self,dname):
        return self._entry_exists(dname,'d')

    def file_exists(self,dname):
        return self._entry_exists(dname,'f')

    def dir_empty(self,name):
        #force dir enumeration, by _fetch()ing a dummy file inside the dir.
        try:
            self._fetch(name  + os.path.sep + 'dummy')
        except KeyError: pass

        tdir = self[name]
        return len(tdir.contents)

class Transaction(object):
    """A Transaction is a group of operations which either are all in the 
    store or none are.

    This class just groups the operations together, it is assumed operations
    aren't added to the transaction unless they have already hit the journal
    
    This makes failure to commit logically recoverable - once whatever is 
    stopping the store committing the value is fixed.
    """
    def __init__(self,xid,home,**kwargs):
        self.xid = xid
        self.home = home
        self.ops = []
        self.ops_ptr = 0
        self.track_state = kwargs.get('track_state',True)
        if self.track_state:
            self.state = LazyFSMap(home)

    def add(self,op):
        if self.track_state:
            op.update_state(self)
        self.ops += [ op ]
    
    def rollback(self,**kwargs):
        for op in self.ops:
            op.dont_do(**kwargs)

    def commit(self,**kwargs):
        for op in self.ops:
            op.do(**kwargs)

    def _canon_name(self,dirname):
        #Canonicalise dirname
        dirname, = make_rel(self.home,dirname)
        dirname = os.path.normpath(dirname)
        return os.path.normcase(dirname)

    def dir_empty(self,dirname):
        return self.state.dir_empty(self._canon_name(dirname))
 
    def dir_exists(self,dirname):
        return self.state.dir_exists(self._canon_name(dirname))

    def file_exists(self,dirname):
        return self.state.file_exists(self._canon_name(dirname))

    def unlink(self,name):
        del self.state[self._canon_name(name)]

    unlink_file = unlink_dir = unlink
    
    def add_file(self,name):
        name = self._canon_name(name)
        f = File_Entry(os.path.basename(name))
        self.state[name] = f

    def add_dir(self,name):
        name = self._canon_name(name)
        f = Dir_Entry(os.path.basename(name), {} )
        self.state[name] = f


class LogStream(file):
    def __init__(self,*args,**kwargs):
        super(LogStream,self).__init__(*args,**kwargs)
        self.dataptr = 0
        self.pos   = 0 
        self.stack = []

    def __iter__(self,):
        """Yield individual characters in the file"""
        self.seek(self.pos)
        data = self.read(BUFFER_SZ)
        while data:
            while self.dataptr < len(data):
                self.dataptr += 1
                yield data[self.dataptr - 1]

            self.pos = self.tell()    
            self.dataptr = 0
            data = self.read(BUFFER_SZ)


    def peek(self,):
        """Read the next character without moving the file pointer"""
        self.snapshot()
        x = iter(self).next()
        self.restore()
        return x

    def snapshot(self,):
        """Store the current file pointer on a stack"""
        self.stack.append((self.pos,self.dataptr))        

    def restore(self,):
        """Restore the file pointer to the location on the top of the stack"""
        self.pos, self.dataptr, = self.stack.pop()

    def discard(self,):
        """Discard the top entry from the stack of saved file pointers."""
        self.stack.pop() 

class stream_context(object):
    def __init__(self,f):
        self.f = f

    def __enter__(self):
        self.f.snapshot()

    def __exit__(self,e1,e2,e3):
        if e1 is None:
            self.f.discard()
        else:
            self.f.restore()
        return False
            

class LogFile(object):
    """A LogFile is an append only file which 
        contains a sequence of transactions.

        A Logfile is preallocated on disk up to reserve octets
        of store.
     """
    def __init__(self,filename,**kwargs):
        """Create a logfile in <filename>.
    
            readonly: make it a readonly logfile - mainly used for recovery.
            reserve:  minimum sile size for operations
        """
        modlogger.debug( "LF:%s %s"%(filename,kwargs))
        self.fname = filename
        reserve = kwargs.get("reserve",DEFAULT_LOGSZ)
        reserve = max(reserve,MINIMUM_LOGSZ)
        self.ro = kwargs.get("readonly",False)

        mode = "wb+" if not self.ro else "rb"
        self.fd = LogStream(filename,mode)
        #FIXME: In the case that this is a new file
        #we should sync the directory fd (which means opening one).
 
        #We detect sparse logfile, and dont really support
        # them properly.
        self.sparse = False
        self.not_complete_lock = threading.Lock()
        self.not_complete = []
        self.closing = False 
        self.outstanding = threading.Condition(self.not_complete_lock)
 
        if not self.ro: self._reserve(reserve)        
      
    def _reserve(self,req_size):
        """Reserve size bytes on disk.
    
        This function will almost certainly block"""
        modlogger.debug( "RESVR:%s"%req_size)
        stat = os.fstat(self.fd.fileno())
        cur_size = stat.st_size
        try:
            alloc_sz = stat.st_blocks * stat.st_blksize
        except AttributeError: pass
        else:
            if alloc_sz < cur_size:
                self.sparse = True
                raise RuntimeError("Sparse file detected as logfile")


            modlogger.debug( "\t:%s"%cur_size)
            if (cur_size < req_size ):
                blks = req_size // stat.st_blksize
                #If not exact add an extra blk.
                if req_size % stat.st_blksize: blks += 1

                req_size = blks  *  stat.st_blksize

            self.fd.seek(cur_size)
            self.fd.write('\0' * (req_size - cur_size))
            self.fd.flush()
            self.fd.seek(0)

        os.fsync(self.fd.fileno())
        self.limit = req_size
        
    def append(self,op):
        """Write an operation to the logfile"""
        if len(op) > self.limit - self.fd.tell():
            return False

        modlogger.debug( "LF.a:%s"%(map(lambda x:hex(ord(x)), str(op))))
        with self.not_complete_lock:
            if self.closing:
                  raise RuntimeError("Cannot append to a closing logfile.")

            self.not_complete.append(op.opid)
        self.fd.write(str(op))
        self._write_terminator()
 
        op.set_callback(self._mark_xcompleted)
        return True

    def _mark_xcompleted(self,opid):
        """internal: called by an transaction when safely
        recorded in the main store"""
        with self.not_complete_lock:
            modlogger.debug( "%s: completing %s"%(self,opid))
            self.not_complete.remove(opid)
            if not self.not_complete: self.outstanding.notifyAll()

    def _checkpoint(self,):
        """Internal function to ensure the main store has
        all the transactions that are in the logfile"""
        self.outstanding.wait()
 
    def _wait(self,):
        """Wait for all the operations to be commit to persistent store"""
        #modlogger.debug( "%s: waiting"%self)
        self.closing = True
        with self.not_complete_lock:
            if not self.not_complete: return
            self._checkpoint()
               

    def __iter__(self,):
        """From the current file pointer read and iterate through operations"""
        done = False
        while True:
            if self.fd.peek() == '\0': break
            with stream_context(self.fd) as data:
                yield JournaledOperation.load(iter(self.fd))
    
    def unlink(self,):
        """An alternative way of closing the LogFile
 
        This function is not protected against racing with append
        """
        self._wait()
        self.fd.close()
        self.fd = None
        os.unlink(self.fname)

    close = unlink
    def _write_terminator(self,):
        """Write log terminator record. And flush all to disk """
        #It is critical that this function blocks and write the outstanding
        #records to the disc, as without that the whole protocol comes unstuck

        self.fd.write("\0")
        self.fd.flush()
        self.fd.seek(-1,1)
        fdatasync(self.fd.fileno())



def _remove_commited(itrble,op):
    tmp = []
    for id in itrble:
        if id > op.opid: tmp+= [ id ]
    return tmp

def _getop(x):
    r = None
    try: 
        r =x.next()
    except StopIteration: pass

    return r

def _getid(op):
    r = op
    if op != None:
        r = op.opid
    return r

class FileLoggerSimpleFS(object):
    def __init__(self, directory ,**kwargs ):
        """ Create a new controller object for our simplistic TxF implementation

            recover :bool - False to force skipping journal recovery.
            reserve : int - initial minimum size for log file.
        """ 
        self.home  = directory
        self.track_state = kwargs.get('track_state',True)

        self.last_opid = -1        #cleanup
        try:
            os.remove(tstfile) 
        except Exception:
            pass 


        #id_lock prevents new transactions being created 
        # and protect last_opid.
        self.id_lock = threading.Lock()     
        #not_complete_lock protects the not_complete list, prevents
        #transaction being submitted and is used for the 
        #outstanding condition variable. Always acquire not_complete_lock
        #before id_lock
        self.oldlogtx = -1
        self.tx = None

        if kwargs.pop('recover',True): self._recover()
        self.frozen = False        #FIXME: In the case that this is a new file
        #we also should sync the directory fd (which means opening one).
 
        self.logf  = None
        self.in_use_logs = []
        self.logsync = threading.Semaphore(0)
        self.loglocker = RWLock()
        self.rotatelog(**kwargs)

    def _findlogs(self,):
        logs = glob.glob(os.path.join(*self._get_logname("*")))
        modlogger.debug( "Logs:%s"%logs)

        return logs

    def _newname(self,):
        names = self._findlogs()
        avail = list(set(names) - set(self.in_use_logs))
        if avail:
            return os.path.join(self.home, avail[0])
        else:
            path,  zeroth_log = self._get_logname(-1)
            nr = max([x.split(".")[3] for x in chain([zeroth_log],names)])
            nr = int(nr) +1
            return os.path.join(*self._get_logname(nr))

    def _get_logname(self,seq):
        """Takes integer decribing the sequence nr of the log file,
        or * to generate a glob pattern for logfiles"""
        return self.home,"..xaction.%s.log"%seq

    def new_opid(self,):
        """Internal: Create a new unique transaction id (Thread safe)"""
        with self.id_lock:
            v = self.last_opid + 1
            self.last_opid = v
        return v
   

    def _recover(self,):
        """Replay associated logfiles. This function blocks
        until completion."""
        modlogger.debug( "starting recovery")
        with self.id_lock: #Prevent new ops being created.
            logs = [ LogFile(x,readonly=True) for x in self._findlogs() ]      
            logiter = [ iter(x) for x in logs ]
            ops   = [ _getop(x) for x in logiter ]
            opids = [ _getid(x) for x in ops ]
            #order the log files by operation Id.
            data = sorted(izip(logs,logiter,ops,opids),key =lambda x:x[3])
            modlogger.debug( "SR:%s"%data)
            #And now got through all log files in Id order
            state = 'init'
            unrecoverable = []
            for log,it,op,opid in data:
                for cur_op in chain([op],it):
                    #cur_op None indicated end of that logfile.
                    if cur_op is None: break

                    #We ignore any ops until we see a 'startTxn' marker, but we
                    # keep a record of there ids to ensure we see a later checkpoint.
                    # if we don't we can't replay partial Txn.
                    modlogger.debug( "R:%s,%s",cur_op,state)
                    if state=='init':
                        #Record all operations we see before we see the first
                        #start tx marker.
                        if cur_op.optype == 'start_txn':
                             state='txcomplete'
                        elif cur_op.optype == 'abort_txn':
                            #If the partial transaction we found was aborted
                            # we don't need to worry about its operations. 
                            unrcoverable = [ ]
                        elif cur_op.optype == 'Checkpoint':
                            unrecoverable = _remove_commited(unrecoverable,cur_op.opid)
                        else:
                            unrecoverable += [ op.opid]
                    

                    #We are looking for a starttxn, marker to mark the operation
                    #as valid. The only other meaningful transaction in the
                    #journal in the state is a checkpoint making which ops have been
                    #detected as committed to the main store by the FS.
                    if state=='txcomplete':
                        if cur_op.optype == 'start_txn':
                            tx = cur_op.txn_id
                            txops = [ ]
                            state = 'txstarted'
                            continue
                        elif cur_op.optype == 'Checkpoint':
                            unrecoverable = _remove_commited(unrecoverable,cur_op.opid)
                        else: raise RecoveryError("Operation outside tx")

                    #In this state all operations are meaningful.
                    # we store all operations (except checkpoint) until we see
                    # a EndTxn op. At the end TxnOp we synchronously complete
                    # all operations.
                    if state =='txstarted':
                        if cur_op.optype == 'end_txn': 
                            #The test below finds 'overlapped' tx, (or ones missing a commit record
                            #for  some reason. This forces us not to accept this log file.
                            if cur_op.txn_id != tx: raise RecoveryError("Non matching Tx commit found")
                            else:
                                for top in txops:
                                    top.do(sync = True)
                            state = 'txcomplete'
                        elif cur_op.optype == 'abort_txn':
                            state = 'txcomplete'
                        elif cur_op.optype == 'Checkpoint':
                            unrecoverable = _remove_commited(unrecoverable,cur_op.opid)
                        else:
                            txops += [ cur_op ] 
                #Log file has been processed successfully - remove it from the Fs.
                #we could call close() here and reused the allocated space on the
                #FS - but the logfile is readonly - and close() adds a terminator
                #to mark the file as empty.
                try:
                    log.unlink()
                except OSError: pass

            #If there are any partial txn's left we have failed to recover.
            if unrecoverable: raise RecoveryError("Partial uncommitted txn found")
            
    def rotatelog(self,**kwargs):
        """Create a new log file ready for use and place , maek it the
        active file"""
        newname = self._newname()
        newlgf = LogFile(newname,**kwargs)
        with self.id_lock:
            self._rotatelog(newlgf,newname)

    def _rotatelog(self,newlgf,newname):
        """Internal function. Should be called with id_lock held"""
        modlogger.debug( "rl:%s"%newname)
        if self.logf: 
            thread.start_new_thread(self._waitlog,(self.logf,self.logname))
            self.logsync.acquire()

        if newname: self.in_use_logs += [ newname ] 
        try:
            self.logf, self.logname = newlgf , newname
        except Exception:
            if newname:
                self.in_use_logs.remove(newname)
            raise

    def _waitlog(self,logf,fname):
        self.loglocker.acquire_read()
        self.logsync.release()
        logf.close()
        self.in_use_logs.remove(fname)
        self.loglocker.release()

    def Add_File(self,txn,filename,newcontents):
        """Log new file content transaction."""
        opid = self.new_opid()
        fullname = os.path.join(self.home,filename)
        #if not self.tx.dir_exists(os.path.dirname(fullname)):
        #    raise OSError(errno.ENOENT,"No directory: %r"%os.path.dirname(fullname))
        xaction = ReplaceAll_Operation(fullname,newcontents,opid)
        self._add_operation(txn,xaction)
 
    def Delete_File(self,txn,filename):
        """Log a delete file  transaction."""
        opid = self.new_opid()
        xaction = DeleteFile_Operation(os.path.join(self.home,filename),opid)
        self._add_operation(txn,xaction)
 
    def Create_Dir(self,txn,filename):
        """Log a delete file  transaction."""
        opid = self.new_opid()
        xaction = CreateDir_Operation(os.path.join(self.home,filename),opid)
        self._add_operation(txn,xaction)
 
    def Delete_Dir(self,txn,filename):
        """Log a delete file  transaction."""
        opid = self.new_opid()
        xaction = DeleteDir_Operation(os.path.join(self.home,filename),opid)
        self._add_operation(txn,xaction)
         
    def _add_operation(self,txn,xaction):
        modlogger.debug( "ao")
        if txn != self.tx.xid: raise RuntimeError("wrong txn %s!=%s"%(txn,self.tx.xid))
        self.tx.add(xaction)
        while not ( self.logf and self.logf.append(xaction)):
            self.rotatelog(reserve = len(xaction))

    def start_transaction(self,):
        """Start a new transaction to group operations.

        Returns: an opaque obj for use with other mehtods"""

        if self.tx is not None:
            raise OverlappedTransaction(str(self.tx.xid))

        modlogger.debug("start tx")
        opid = self.new_opid()
        xaction = StartTxOperation(opid,opid)
        self.tx = Transaction(opid,self.home, track_state = self.track_state)
        self._add_operation(opid,xaction)
        return opid

    def commit_transaction(self,xid):
        """Commit the tranasaction with id xid.

        This forces all the operations which have been logged as
        part of this transaction to persistent store.
        """
        modlogger.debug( "end tx:%s"%xid)
        if xid != self.tx.xid:
            raise InvalidTransaction(xid)

        opid = self.new_opid()
        xaction = EndTxOperation(opid,xid)
        self._add_operation(xid,xaction)
        try:
            self.tx.commit()
        except Exception:
            self.tx = None
            #There is an arguement to call abort here...
            # but we don't because our (MysteryMachine) use
            # of this is a bottom layer store, which means the
            # schema should have already ensured the transactions
            # are meaningful and a exceptio here is probably a
            # due to local conditions (like diskspace).
            #
            # If we abort we would have to remove the commit record
            # from the log, and then undo the partial tranasction.
            # by not aborting, and re-raisig we make this the 
            # problem of a higher layer. Once the problem is resolved
            # the journal can be replayied making ourselve consistent
            # again.
            #
            # There is one way though of provoking non-recoverable behavour
            # ad that is creating a file in a non-existant dir.
           
            #self.abort_transaction(xid)
            raise

        self.tx = None

    def abort_transaction(self,xid):
        """Aborts the transaction with id xid.

        This forces all the operations which have been logged as
        part of this transaction to persistent store.
        """
        modlogger.debug( "abort:%s"%xid)
        opid = self.new_opid()
        xaction = AbortTxOperation(opid,xid)
        self._add_operation(xid,xaction)
        try:
            self.tx.rollback()
        finally:
            self.tx = None


    def close(self,):
        """Finish use of the File logged directory"""
        self.freeze()
        

    def freeze(self,):
        """Bring main store upto date and prevent any more
        transactions while frozen"""
        if self.frozen: return

        self.id_lock.acquire()
        #Set logfile to None. Put current logfile into wait for chkpt state.
        self._rotatelog(None,"")
        self.loglocker.acquire_write()
        self.frozen = True     
 
    def unfreeze(self,):
        """Release any transactions from being blocked by the frozen state."""
        if self.frozen and self.id_lock.locked():
            self.id_lock.release()
            self.loglocker.release()
            self.frozen = False
    
    thaw = unfreeze

    def _del_(self,):
        if not self.frozen:
            #Depend on nothing outside this object
            import logging
            logging.getLogger("MysteryMachine.store.FileLogger").error("Detected cleanup of Fileloogger incorrectly closed")



class FileLoggerTxF(object):
    def __init__(self,directory,*args,**kwargs):
        self.home = directory
        self.readonly = kwargs.get('readonly',False)
        self.tx = None

    def start_transaction(self,):
        if self.tx is not None:
            raise OverlappedTransaction(str(self.tx))

        self.tx = win32_txf.CreateTransaction()
        return self.tx

    def abort_transaction(self,tx):
        if tx != self.tx:
            raise InvalidTransaction(tx)
        win32_txf.RollbackTransaction(self.tx)
        self.tx = None

    def commit_transaction(self, tx):
        if tx != self.tx:
            raise InvalidTransaction(tx)
        win32_txf.CommitTransaction(tx)
        self.tx = None

    def Add_File(self,tx,filename,newcontents):
        """Log new file content transaction."""
        if tx != self.tx:
            raise InvalidTransaction(tx)
        fullname = os.path.join(self.home,filename)
        h = win32_txf.CreateFileTransacted(fullname,transaction = tx,
                    desired_access = win32_txf.const.GENERIC_WRITE,
                    creation_disposition = win32_txf.const.CREATE_ALWAYS)
        #TODO handle partial writes
        win32_txf.WriteFile(h,newcontents)
        win32_txf.CloseHandle(h)

    def Delete_File(self,tx,filename):
        """Log a delete file  transaction."""
        if tx != self.tx:
            raise InvalidTransaction(tx)

        fullname = os.path.join(self.home,filename)
        win32_txf.DeleteFileTransacted(fullname,transaction = tx)

    def Create_Dir(self,tx,filename):
        """Log a delete file  transaction."""
        if tx != self.tx:
            raise InvalidTransaction(tx)
 
        fullname = os.path.join(self.home,filename)
        win32_txf.CreateDirectoryTransacted(None,fullname,transaction = tx)


    def Delete_Dir(self,tx,filename):
        """Log a delete file  transaction."""
        if tx != self.tx: raise RuntimeError("wrong tx")

        fullname = os.path.join(self.home,filename)
        win32_txf.RemoveDirectoryTransacted(fullname,transaction = tx)


    def freeze(self,): 
        """This is a no-op on Txf"""
        pass

    close = unfreeze = thaw = freeze


FileLogger = FileLoggerSimpleFS

##If on windows try to detext TxF Support and switch to that if available.
if sys.platform[:5] == 'win32' and TxF_Enabled:
    import MysteryMachine.store.win32_txf as win32_txf
    import ctypes
    try:
        #Ask ctypes to look for the CreateTransaction entry point
        ctypes.windll.ktmw32.CreateTransaction
    except AttributeError: pass
    else:
        FileLogger = FileLoggerTxF
   
