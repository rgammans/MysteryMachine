#!/usr/bin/env python
#   			storeTest.py - Copyright Roger Gammans
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
"""
Tests for the MysteryMachine dictstore  module
"""

from MysteryMachine import * 
from MysteryMachine.store.gitfile_base import *
from MysteryMachine.store.Base import Base
from MysteryMachine.store import GetPath
from base.scm import scmTests

import unittest

import os
import tempfile 
import shutil

import sys

class BasicStore(Base):
    uriScheme = "basic_git"
    def __init__(self,*args,**kwargs):
        create = kwargs.pop('create',None)
        super().__init__(*args,**kwargs)
        self.path = GetPath(args[0])
        if create:
            os.mkdir(self.path)

    def get_path(self):
        return self.path

    def ReadFile(self,name):
        f = open(os.path.join(self.path,name),"r")

        rv = f.read()
        f.close()
        return rv

    def WriteFile(self,name,content):
        f = open(os.path.join(self.path,name),"w")
        f.write(content)
        f.close()
        self.Add_file(name)

uniq_name = 1
class gitstoreTests(scmTests, unittest.TestCase):

    def setUp(self):
        global uniq_name

        self.testpath = None
        self.ctx = StartApp(["--cfgengine=ConfigYaml", "--cfgfile=tests/test.yaml", "--testmode"])
        try:
            self.testpath = tempfile.mkdtemp("mysmachg")
        except Exception:
            pass
        uniq_name += 1
        self.testtype = type("GitTestStore", (GitStoreMixin , BasicStore ), {'uriScheme':"gitbasic"+str(uniq_name)} )
        #Ensure delte - will create again in a moment
        os.rmdir(self.testpath)
        self.store= self.testtype("gitbasic"+str(uniq_name)+":"+self.testpath,create = True)
        self.has_scm = True

    def tearDown(self):
        self.store.close()
        shutil.rmtree(self.testpath)
        if os.path.exists(self.testpath):
            os.rmdir(self.testpath)
        self.ctx.close()

    def processDirs(self,dirs):
        if '.git' in dirs:
           #Don't scan the .git directory.
           del dirs[dirs.index('.git')]

def getTestNames():
    	return [ 'gitfile_store.gitstoreTests' ] 

if __name__ == '__main__':
    unittest.main()

