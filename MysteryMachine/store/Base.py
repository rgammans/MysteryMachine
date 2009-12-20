#!/usr/bin/env python
#   			MysteryMachine/store/Base.py - Copyright Roger Gammans
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
"""


from MysteryMachine.store import * 


class Base(object):
    """
    New base class for Mystery Machine store to inherit from
    """
    __metaclass__ = storeMeta

    def canonicalise(self,name):
        return name.split(":")

    def __init__(self,uri,*args,**kwargs):
        self.uri   = GetCanonicalUri(uri)
        self.owner = None

    def getUri(self):
        return self.uri
   
    def get_path(self):
        return GetPath(self.uri)
 
    @staticmethod
    def GetCanonicalUri(uri):
        return uri

    def get_owner(self):
        return self.owner

    def set_owner(self,v):
        print "Setting owner to %s" % v
        self.owner = weakref.proxy(v)

    def commit(self,msg):
        """
        Override the to support transactions - usually in the contect
        of version control.
        """
        return False

    def rollback(self):
        """
        Override this to provide a rollback action .
        Takes the game back tot he last commit.
        """
        return False

    def revert(self,revid):
        """
        Override this to take the game back to any previous transaction.
        """
        return False

    def getChangelog(self):
        """
        Override thsi to..
        Rertuns a list of revid's which can be revert'ed to
        """
        return []

    def HasObject(self,obj):
        return False

    def GetObjStore(self,obj):
        return obj_storeproxy(self,obj)


    def Add_file(self,filename):
        """
        Adds a file to the SCMs repo 

        This function is intended to be called by store modules, so
        to allow them to commincate to the SCM provider.
        """

    def lock(self):
        """
        Call to wait for the store to be queiscent - called prior to Saving
        a system to pack file.
        """
        pass
    
    def unlock(self):
        """
        Allow updates to continue.
        """
        pass

class obj_storeproxy:
    def __init__(self,store,obj):
        self.store=store
        self.obj=obj

    def GetAttribute(self,attr):
        return self.store.GetAttribute(self.obj + ":" +attr)
        

    def SetAttribute(self,attr,type,parts):
        return self.store.SetAttribute(self.obj + ":" +attr,type,parts)
   
    def DelAttribute(self,attr):
        return self.store.DelAttribute(self.obj + ":" +attr)

    def EnumAttributes(self):
        for a in self.store.EnumAttributes(self.obj):
            yield a

    def HasAttribute(self,attr):
        return self.store.HasAttribute(self.obj + ":" +attr)
 
