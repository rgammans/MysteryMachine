#!/usr/bin/env python
#           gitfile_base.py - Copyright Roger Gammans
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

import MysteryMachine
import MysteryMachine.store.Base

import sys
import os 
import contextlib
import itertools
import git

class GitStoreMixin(object):
    """
    This class is a mixin which provide the SCM related functions require for a MysteryMachine
    store class.
    """

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if kwargs.get('create',None):
            self.repo = git.Repo.init(self.get_path())
        else:
            self.repo = git.Repo(self.get_path())
        self.cmd = git.cmd.Git(self.get_path())

    def start_store_transaction(self,):
        self.filechanges = []
        super().start_store_transaction()

    def abort_store_transaction(self,):
        self.filechanges = []
        super().abort_store_transaction()

    def commit_store_transaction(self,):
        super().commit_store_transaction()
        for op,filename in self.filechanges:
            if   op == "a":  self._Add_file(filename)
            elif op == "r":  self._Remove_file(filename)

    def Add_file(self,filename):
        if self.supports_txn:
            self.filechanges.append(("a",filename,))
        else:
            self._Add_file(filename)

    def _Add_file(self,filename):
        self.cmd.add( os.path.join(self.path,filename)) 

    def Remove_file(self,filename):
        if self.supports_txn:
            self.filechanges.append(("r",filename,))
        else:
            self._Remove_file(filename)

    def _Remove_file(self,filename):
        self.cmd.rm(
            '--force',
            '--ignore-unmatch',
            os.path.join(self.path,filename)
        )

    def commit(self,msg):
        self.lock()
        try:
            rv = self.cmd.commit('-m', msg )
        except git.GitCommandError as c:
            self.logger.error("git Command error E:",c.stderr,"R:",c.status,"O:",c.stdout,"A:",c.args)
            raise
        self.unlock()
        return rv

    def rollback(self):
        return self.cmd.reset('HEAD^1','--hard')

    def revert(self,commit):
        return self.cmd.reset('--hard',commit.key())

    def getChangeLog(self):
        class GitCommit:
            def __init__(self, commit):
                self.commit = commit

            def key(self):
                return self.commit.hexsha

            def manifest(self,):
                return [
                    x.path
                    for x in self.commit.tree.traverse()
                    if x.type == 'blob'
                ]
        return [GitCommit(x) for x in self.repo.iter_commits()]

    def uptodate(self,*args,**kwargs):
        """
        Returns true is repo is uptodate.

            Add Argurment deleted=True to include deleted files

        Up to date - is the equivalent of an empty result from 'hg status'
        """
        return not self.repo.is_dirty()

    def clean(self,*args,**kwargs):
        """
        Cleans the repo.

        :param force bool: if True: clean runs even if git is not uptodate
        :param full  bool: if True:  deletes everything except the .git/ .
                    otherwise we just delete files in the git tree.
        """
        #Force the main store to remove any tempfiles
        mysuper = super()
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
                if '.git' in dirs:
                    dirs.remove('.git')

        else:
            #Basic clean - just remove files in the manifest and marked as added.
            for f, _ in self.repo.index.entries.keys():
                with contextlib.suppress(FileNotFoundError):
                    print(f"REmoving {f}")
                    os.unlink(os.path.join(self.get_path(),f))

