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
import MysteryMachine.Exceptions

_store_registry = dict()
import logging

modlogger  = logging.getLogger("MysteryMachine.store")

def CreateStore(uri):
    """
    Initialise a store at location Uri. If Uri contains data it may be 
    deleted dependent of the behaviour of the storage driver.

    Returns a MysteryMachine.store.Base instance
    """
    scheme = GetScheme(uri)
    modlogger.debug( "Looking for store scheme %s " % scheme)
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
    modlogger.debug( "registering store schema `%s'" % storename)
    if storename not in _store_registry:
        _store_registry[storename] = storeclass
    else:
        raise MysteryMachine.Exceptions.DuplicateRegistration , "%s already registered" % storename

def GetScheme(uri):
    scheme,path = uri.split(":",1)
    return scheme

def GetPath(uri):
    scheme,path = uri.split(":",1)
    return path 


class storeMeta(type):
    def __init__(self, name, bases, ns):
        super(storeMeta, self).__init__(name,bases,ns)
        if name != "Base":
            RegisterStore(self.uriScheme,self)

