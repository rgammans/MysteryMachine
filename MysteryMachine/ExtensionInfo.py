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
from MysteryMachine.ExtensionSecureID import ExtensionSecureID

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
    self.secureID= ExtensionSecureID.fromPathName(plugin_path+".py")

  def getName(self):
    """
    
    @return string : Name of the plugin.
    @author
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
    Activates a truste plugin - no-op on untrusted plugin
    """
    if self.plugin_object != None:
       self.plugin_object.activate()


  def deactivate(self):
    """
    Deactivates a truste plugin - no-op on untrusted plugin
    """
    if self.plugin_object != None:
       self.plugin_object.deactivate()



