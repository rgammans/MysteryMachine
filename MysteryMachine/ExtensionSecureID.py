#!/usr/bin/env python
#   			ExtensionSecureID.py - Copyright Roger Gammans 
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
#

import hashlib
import os

class ExtensionSecureID(object):

  """
   This class represents a secure hash for an extension. Trust of one version of an
   extension is not transitive to earlier or later versions.

   This base class uses SHA256 as the hash function

  :version: 1.0
  :author:  R G Gammans
  """


  @classmethod
  def fromPathName(cls,path):
    input= open(path,"rb")
    hash = hashlib.sha256()
    for chunk in input:
      hash.update(chunk)
    return cls(path,hash,"sha256")

  @classmethod
  def fromHash(cls,path,hashstring):
     return cls(path,hashstring) 
    
  def __init__(self, path, hashstr, hashtype ="sha256"):
    """
     Computes the signature of an extension from it's path.

    @param string path : Pathname of extension to compute signature of.
    @author
    """
    self._path= path

    if isinstance(hashstr,str):
      self._hashtype , self._value = hashstr.split("|")
      self._hash = hashlib.new(self._hashtype)
    else:
      self._hash= hashstr
      self._value=hashstr.hexdigest()
      self._hashtype=hashtype


  def __repr__(self):
    return "%s(%s,%s|%s)" % (self.__class__ , self._path , self._hashtype , self._value ) 

  def __str__(self):
    return "%s|%s" % (self._hashtype, self._value )

  def __eq__(self, other):
    """
  
    @param ExtensionSecureID other : 
    @return bool :
    """
    if isinstance(other , self.__class__):
        return [self._hashtype, self._value] == [self._hashtype , other._value ]
    else:
        return self.__str__() == str(other)

  def __hash__(self):
    return ("%s[%s|%s]" % (self.__class__,self._hashtype,self._value)).__hash__() 

