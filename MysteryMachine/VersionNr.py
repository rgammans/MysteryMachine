#!/usr/bin/env python
#               VersionNr.py - Copyright Roger Gammans
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
# This file was generated on Tue Dec 30 2008 at 15:39:18
# The original location of this file is /home/roger/sources/MysteryMachine/generated/VersionNr.py
#
#

import types
from copy import copy
from .utils.RichCompare import RichComparisonMixin
distutils_Ver = None
try:
    from distutils.version import Version
    distutils_Ver = Version
except ImportError:pass

class VersionNr(RichComparisonMixin):

    """
     This simple class provide version number arithmetic.

    :author: R G Gammans
    """
    def __init__(self,*args):
        """
        Initialiser. Takes a string seperated by '.', a list or
        another VersionNr.
        """
        if type(args[0]) == type(self):
            self.SetValue(args[0].nrs)
        elif type(args[0]) == types.StringType:
            self.SetValue(args[0].split("."))
        elif isinstance(args[0],distutils_Ver):
            self.SetValue(list(args[0].version))
        #Assume list type.
        else:
            self.SetValue(list(args))
#    assert true "Cannot initialise version Nr"
    def SetValue(self,list):
        self.nrs=list
    def __str__(self):
        return ".".join(map(str,self.nrs))
    def __repr__(self):
        return "VersionNr"+"("+",".join(map(str,self.nrs))+")"
    def __lt__(self, other):
        """
        Base comparion function to provide an ordering relation.

        @param VersionNr other : value to compare with 
        @return bool : True if other less than self.
        """
        cflist=copy(other.nrs)
        for level in self.nrs:
            if level is None: return True
            val=int(level)

            if len(cflist) == 0: return False 
            cfdig=cflist.pop(0)
            if cfdig is None:
                return False
            else:
                cfdig = int(cfdig)
            #
            if cfdig == None: return False
            if cfdig!=val: return val<cfdig
        
        #Other must be equal or larger, so
        return len(cflist)>0
    
    def __hash__(self):
        return hash(self.__repr())

    def __eq__(self, other):
        """
        Equiavalence relation

        @param VersionNr other : value to compare with
        @return bool : returns if bool version number are equivalent
        """
        cflist=copy(other.nrs)
        for level in self.nrs:
            #None;s compare non-equal..
            if level is None: return False
            val=int(level)
            
            if len(cflist) == 0: return False 
            cfdig=cflist.pop(0)
            if cfdig is None:
                return False
            else:
                cfdig = int(cfdig)
        #
            if cfdig == None: return False 
            if cfdig!=val: return False
        #Other will be the same length if equal
        # so cf list will be empty now.
        return (len(cflist) == 0)

