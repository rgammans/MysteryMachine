#!/usr/bin/env python
#   			MysteryMachine/store/__init__.py - Copyright Roger Gammans
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

import weakref

_store_registry = dict()


def CreateStore(uri):
    """
    Initialise a store at location Uri. If Uri contains data it may be 
    deleted dependent of the behaviour of the storage driver.

    Returns a MysteryMachine.store.Base instance
    """
    scheme = GetScheme(uri)
    print "Looking for store scheme %s " % scheme
    storeclass = _store_registry[scheme]
    return storeclass(uri, create=True)

def GetStore(uri):
    """
    Return and instance of a store the store will provide access to the
    MysteryMachine SYstem stored at uri. 
    """
    scheme = GetScheme(uri)
    storeclass = _store_registry[scheme]
    return storeclass(uri, create=False)


def GetCanonicalUri(uri):
    """
    Return uri in a canonical form.
    """
    scheme = GetScheme(uri)
    storeclass = _store_registry[scheme]
    return scheme + ":" + storeclass.GetCanonicalUri(GetPath(uri))

def RegisterStore(storename,storeclass):
    """
    Register storeclass as the handler store class for uri in scheme storename
    
    Registering the same storename multiple times is an error.
    """
    print "registering store schema `%s'" % storename
    if storename not in _store_registry:
        _store_registry[storename] = storeclass
    else:
        raise MysteryMachine.DuplicateRegistration , "%s already registered" % storename

def GetScheme(uri):
    scheme,path = uri.split(":",1)
    return scheme

def GetPath(uri):
    scheme,path = uri.split(":",1)
    return path 



class Base(object):
    """
    New base class for Mystery Machine store to inherit from
    """
    def __init__(self,uri,*args,**kwargs):
        self.uri   = GetCanonicalUri(uri)
        self.owner = None

    def getUri(self):
        return self.uri

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
        
