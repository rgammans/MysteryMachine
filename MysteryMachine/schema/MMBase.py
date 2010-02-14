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


from __future__ import with_statement

from  MysteryMachine import StartApp

#We import identifier to allow to ensure consisentcy 
from MysteryMachine.parsetools.grammar import identifier
import pyparsing
import logging

class MMBase(object):

  """
   This is base class which handles all the stuff which is common to all the nodes
   in a MMSYstem, such as validation , and Store versioning. It interfaces with the
   ExtensionLib to get any required classes for alternate backend stores.

  :version:
  :author:
  """

  def __init__(self,*args,**kwargs):
    """
     Creates the object and /commifinds any require mixins

    @return  :
    @author
    """
    self.logger = logging.getLogger("MysteryMachine.schema.MMBase")
    with StartApp() as g:
        for helper in g.GetExtLib().get_helpers_for(self.__class__):
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
  
  def get_root(self):
    """
    Returns the root (eg. MMSystem) node for the system which this object is
    a member of.
    """
    root = self.owner
    # Walk up the owner links
    while hasattr(root,"owner") and root.owner != None:
        root = root.owner
    return root

  def canonicalise(self,name):
    ##This keeps it synchronized with the definition
    # of identifier in parsetools/grammar.py
    try:
       #Supress leading dot from the test.
       tstname = name
       if tstname[0] == '.': tstname = tstname[1:]
       #Check that the identifier is good enough to match it.
       identifier.parseString(tstname,parseAll=True)    
    except pyparsing.ParseException:
       raise ValueError("`%s` is not valid in the MysteryMachine Namespace" % name)

    return name.lower()
    
  def __iter__(self):
    return []
