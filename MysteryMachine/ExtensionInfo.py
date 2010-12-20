#!/usr/bin/env python
#   			ExtensionInfo.py - Copyright Roger Gammans
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
# The original location of this file is /home/roger/sources/MysteryMachine/generated/ExtensionInfo.py
#
#

from yapsy.PluginManager import *
from ExtensionSecureID import ExtensionSecureID
import re

EXTENSION_POINT_SECTION_NAME="ExtensionPoints"
 
class ExtensionInfo (PluginInfo):

  """

  :version: 1.0
  :author:  R Gammans
  """

  """ ATTRIBUTES


  secureId  (private)

  """


  def __init__(self,plugin_name,plugin_path):
    """
    Create a plugin info instance.
    """
    PluginInfo.__init__(self,plugin_name,plugin_path)
    self.points = { }
    if self.parser.has_section(EXTENSION_POINT_SECTION_NAME):
        for opt in self.parser.options(EXTENSION_POINT_SECTION_NAME):
            provides = self.parser.get(EXTENSION_POINT_SECTION_NAME,opt)
            provides = re.split("\s*,\s*",provides)
            if len(provides) > 0:
                provides[0] = provides[0].strip()
                provides[-1] = provides[-1].rstrip()
                self.points[opt.lower()]=provides

    self.secureID= ExtensionSecureID.fromPathName(self.path+".py")

  def getName(self):
    """
    
    @return string : Name of the plugin.
    @authorx
    """
    return self.name

  def getSecureID(self):
    """
   Return the secure hash of the plugins source files.  
  
    @return ExtensionSecureID :
    @author
    """
    return self.secureID

  def activate(self):
    """
    Activates a trusted plugin - no-op on untrusted plugin
    """
    if self.plugin_object != None:
       self.plugin_object.activate()


  def deactivate(self):
    """
    Deactivates a trusted plugin , this should be a no-op
    on an untrusted plugin - although may be called on a plugin
    when it's trust is removed.
    """
    if self.plugin_object != None:
       self.plugin_object.deactivate()


  def isLoaded(self):
    """
    Returns True if the plugin has been loaded into the interpreter
    """
    return self.plugin_object is None

  def provides(self,point,feature):
    point = point.lower()
    if point in self.points:
        return feature in  self.points[point]
    return False

  def features_on_point(self,point):
       point = point.lower()
       if point in self.points:
           return self.points[point]
       return []
