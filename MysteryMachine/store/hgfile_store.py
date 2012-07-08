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

from __future__ import with_statement


import MysteryMachine
import MysteryMachine.store.Base

import sys
import os 
import itertools

import hglib
import hglib.client

class HgStoreMixin(object):
    """
    This class is a mixin which provide the SCM related functions require for a MysteryMachine
    store class.
    """

    def __init__(self,*args,**kwargs):
        super(HgStoreMixin,self).__init__(*args,**kwargs)
        if kwargs.get('create',None):
            hglib.init(self.get_path(),encoding="utf-8")
        
        self.repo = hglib.open(self.get_path(),encoding="utf-8")
        #self.repo = hglib.repository(self.ui,self.get_path(),create = (kwargs.get('create') or 0))
        
    def start_store_transaction(self,):
        self.filechanges = []
        super(HgStoreMixin,self).start_store_transaction()

    def abort_store_transaction(self,):
        self.filechanges = []
        super(HgStoreMixin,self).abort_store_transaction()

    def commit_store_transaction(self,):
        super(HgStoreMixin,self).commit_store_transaction()
        for op,filename in self.filechanges:
            if   op == "a":  self._Add_file(filename)
            elif op == "r":  self._Remove_file(filename)

    def Add_file(self,filename):
        if self.supports_txn:
            self.filechanges.append(("a",filename,))
        else:
            self._Add_file(filename)

    def _Add_file(self,filename):
        if filename not in (x[4] for x in self.repo.manifest()):
            self.repo.add( files = [ os.path.join(self.path,filename)  ]) 
    def Remove_file(self,filename):
        if self.supports_txn:
            self.filechanges.append(("r",filename,))
        else:
            self._Remove_file(filename)

    def _Remove_file(self,filename):
        addedlist =  [ f[1] for f in  self.repo.status() if f[0] == 'A' ]
        #Is the file got the added status?
        if filename in addedlist:
          self.repo.forget( files = [os.path.join(self.path,filename)] )
        else:
          self.repo.remove( files = [os.path.join(self.path,filename)] )
    
    def commit(self,msg):
        self.lock()
        print "%r"%msg
        try:
            rv = self.repo.commit(message=msg,user ="foo" )
        except hglib.error.CommandError, c:
            print "E:",c.err
            print "R:",c.ret
            print "O:",c.out
            print "A:",c.args
            raise
        self.unlock()
        return rv

    def rollback(self):
        return self.repo.rawcommand(["rollback",])

    def revert(self,revid):
        #Forcing to string ensures the revid is in a self.repo.log()form mercurial is happy with
        # and allows changectx objects to be passed
        return self.repo.update(str(revid),clean=True)

    def getChangeLog(self):

        class HgRevision(hglib.client.revision):
            repo = self.repo
            def __str__(self,):
                return self[1]

            def manifest(self,):
                return self.repo.manifest(rev=self[0])

        return ( HgRevision(*x) for x in self.repo.log() )

    def uptodate(self,*args,**kwargs):
        """
        Returns true is repo is uptodate.

            Add Argurment deleted=True to include deleted files

        Up to date - is the equivalent of an empty result from 'hg status'
        """
        significant_status = "MA"
        if not kwargs.get("deleted"):
            significant_status += "R"
    
        return all( (x[0] not in significant_status for x in self.repo.status() ) )

    def clean(self,*args,**kwargs):
        """
        Cleans the repo.
              --force   clean runs even if hg is not uptodate.  
              --full    deletes everything except the .hg/ .
                    otherwise we just delete files in the hg manifest.
        """
        #Force the main store to remove any tempfiles
        mysuper = super(HgStoreMixin,self)
        if hasattr(mysuper,"clean"):
            mysuper.clean(*args,**kwargs)
        if not self.uptodate():
            self.logger.warn("%slean requested in non-up-todate repo." % (
                         "Forced c" if kwargs.get('force') else "C" )) 
            if not kwargs.get('force'): return
            
        if kwargs.get('full'):
            #Do a 'full' clean. Remove all the files except for 
            # the repo itself. This /could/ lose data if you
            # haven't added the files to the repo.
            for dirpath,dirs,filenames in os.walk(self.get_path()):
                for f in filenames:
                    os.unlink(os.path.join(dirpath,f))
                if '.hg' in dirs:
                    dirs.remove('.hg')

        else:
            #Basic clean - just remove files in the manifest and marked as added.
            for f in (x[1] for x in self.repo.status(all=True) if x[0] in 'MARC`' ):
                os.unlink(os.path.join(self.get_path(),f))

