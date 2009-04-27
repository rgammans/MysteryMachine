#!/usr/bin/env python
#   			MMBase.py - Copyright Roger Gammans
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
# This file was generated on Mon Feb 2 2009 at 20:18:08
# The original location of this file is /home/roger/sources/MysteryMachine/generated/MMBase.py
#

from  MysteryMachine import GetExtLib 
 
class MMBase(object):

  """
   This is base class which handles all the stuff which is common to all the nodes
   in a MMSYstem, such as validation , and Store versioning. It interfaces with the
   ExtensionLib to get any required classes for alternate backend stores.

  :version:
  :author:
  """

  def __init__(self):
    """
     Creates the object and /commifinds any require mixins

    @return  :
    @author
    """
    print "In MMBase.__init__ %s" % self.__class__
    for helper in GetExtLib().get_helpers_for(self.__class__):
        if not hasattr(self,"_helpers"): self._helpers=[]
        #Instatiante a helper instance.
        self._helpers += [ helper(self) ] 

  def getRequiredVersions(self):
    """

    @return string :
    @author
    """
    pass

  def Validate(self):
    """
    The caller interface tthe validation code .

    @return bool :
    @author
    """
    ok = true
    for element in self:
        ok = element.Validate()
        if not ok: break

    if ok: ok=self.DoValidate()
    return ok

  def DoValidate(self):
    """
    Does the actual work of validating this object. Override this
    method to provide your rules.

    @return bool :
    @author
    """
    pass

  def __iter__(self):
    return []
