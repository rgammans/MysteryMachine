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


#We import identifier to allow to ensure consisentcy 
from MysteryMachine.parsetools.grammar import identifier
import pyparsing
import logging

#For the container base class
import weakref

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
    self.logger = logging.getLogger("MysteryMachine.schema")

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

  def get_ancestor(self):
    """Return the ancestor node in the schema heirachy.

    This is usually the owner.
    """
    return self.owner

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
  

  def getSelf(self):
    """
    returns self. 

    Used to strengthen a weakref and find the prefered object.
    """
    ## This exists so that MMObject can dereferences the weak proxy
    #  object that the store subsystem will normally pass it.
    return self

  def getRef(self):
    """
    This function is sort of the opposite of getSelf().

    Use on an schema object when creating a schema reference
    this ensures a reference is taken rather than a copy. There is
    only a few places this matters but this method is available
    everywhere.

    @returns: value which references self
    """
    ##Actually a NULL op in the general case. Overriden where it matters. 
    return self


class MMContainer(MMBase):
    """
    This is the base class for object which manage container of
    other MMBase objects to inherit from.

    This is important as the a MMSystem is supposed to provide a guarantee
    a guaranteee about that an Attribute or instance has a single in-core
    instance. 
    """
    def __init__(self,*args,**kwargs):
        super(MMContainer,self).__init__(self,*args,**kwargs)
        self.cache = weakref.WeakValueDictionary()


    def _invalidate_item(self,item):
        try:
            del self.cache[item]
        except KeyError: pass

    def _get_item(self,key,func,*args):
        try:
            item = self.cache[key]
        except KeyError:
            item = func(*args)
            self.cache[key] = item
        return item

    def _set_item(self,k,v):
        self.cache[k] = v


