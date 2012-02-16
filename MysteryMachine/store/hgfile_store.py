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

import mercurial
import mercurial.cmdutil as cmdutil
from mercurial import hg

import MysteryMachine
import MysteryMachine.store.Base

import sys
import os 
import itertools

class HgStoreMixin(object):
    """
    This class is a mixin which provide the SCM related functions require for a MysteryMachine
    store class.
    """

    def __init__(self,*args,**kwargs):
        super(HgStoreMixin,self).__init__(*args,**kwargs)
        #We get the Ui from our Root so that our Ui's can provide their own
        # implementation.
        #
        # The with statement doesn't make the best sense here as we keep the 
        # resources past the end of the block /BUT/ our special use of singletons 
        # in startapp should take care of it  - providing StartApp is also guarding
        # main routine.
        with MysteryMachine.StartApp() as MMGlobals:
            self.ui = MMGlobals.GetMercurialUi()
            self.repo = hg.repository(self.ui,self.get_path(),create = (kwargs.get('create') or 0))
        
    def _wdir_obj(self):
        # Mask the differences between  hg1.5, and later
        if hasattr(self.repo,"add"):
            addobj = self.repo
        else:
            addobj = self.repo[None]
        return addobj


    def start_store_transaction(self,):
        self.filechanges = []
        super(HgStoreMixin,self).start_store_transaction()

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
        if filename not in self.repo[None]:
            self._wdir_obj().add( [ filename  ]) 

    def Remove_file(self,filename):
        if self.supports_txn:
            self.filechanges.append(("r",filename,))
        else:
            self._Remove_file(filename)

    def _Remove_file(self,filename):
       if filename in self.repo[None]:
          s = self.repo.status()
          #Is the file got the added status?
          if filename in s[1]:
            self._wdir_obj().forget( [filename] )
          else:
            self._wdir_obj().remove( [filename] )

    def commit(self,msg):
        self.lock()
        rv = self.repo.commit(msg, None, None , cmdutil.match(self.repo),
                         editor=cmdutil.commiteditor, extra= { })
        self.unlock()
        return rv

    def rollback(self):
        
        return self.repo.rollback()

    def revert(self,revid):
        #Forcing to string ensures the revid is in a form mercurial is happy with
        # and allows changectx objects to be passed
        return mercurial.hg.revert(self.repo,str(revid),None)

    def getChangeLog(self):
        for change in self.repo:
            #FIXME:
            # We will want to wrap this into a generic container so
            # other SCMs are usable.
            # 
            # This wraping requires integration with the underlying store
            # so filenames <-> MysteryMachine names can be mapped if poss.
            yield self.repo[change]


    def uptodate(self,*args,**kwargs):
        """
        Returns true is repo is uptodate.

            Add Argurment deleted=True to include deleted files

        Up to date - is the equivalent of an empty result from 'hg status'
        """
        modified, added, removed, deleted, unknown, ignored, clean = self.repo.status()
        if not kwargs.get("deleted"):
            deleted = []

        for list in itertools.chain(modified,added,removed):
            #We're not interested in deleted
            return False

        return True 

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
            self.ui.warn("%slean requested in non-up-todate repo." % (
                         "Forced c" if kwargs.get('force') else "C"  
                        ))

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
            #Basic clean - just remove files stored in revision control.
            ctx = self.repo[None]
            for f in ctx:
                os.unlink(os.path.join(self.get_path(),f))

