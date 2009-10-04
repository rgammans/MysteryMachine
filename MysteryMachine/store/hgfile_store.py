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


import mercurial
import mercurial.cmdutil as cmdutil
from mercurial import hg

import MysteryMachine
import MysteryMachine.store.Base

import sys
import os 

class HgStoreMixin(object):
    """
    This class is a mixin which provide the SCM related functions require for a MysteryMachine
    store class.
    """

    def __init__(self,*args,**kwargs):
        super(HgStoreMixin,self).__init__(self,*args,**kwargs)
        #We get the Ui from our Root so that our Ui's can provide their own
        # implementation.
        self.ui = MysteryMachine.GetMercurialUi()
        self.repo = hg.repository(self.ui,self.get_path(),create = (kwargs.get('create') or 0))
        

    def Add_file(self,filename):
       if filename not in self.repo[None]:
          self.repo.add( [ filename  ]) 

    def commit(self,msg):
        return self.repo.commit(msg, None, None , cmdutil.match(self.repo),
                         editor=cmdutil.commiteditor, extra= { })

    def rollback(self):
        return self.repo.rollback()

    def revert(self,revid):
        #Forcing to string ensures the revif is in a form mercurial is happy with
        # and allows changectx objects to be passed
        return mercurial.hg.update(self.repo,str(revid))

    def getChangeLog(self):
        for change in self.repo:
            #FIXME:
            # We will want to wrap this into a generic container so
            # other SCMs are usable.
            # 
            # This wraping requires integration with the underlying store
            # so filenames <-> MysteryMachine names can be mapped if poss.
            yield self.repo[change]
