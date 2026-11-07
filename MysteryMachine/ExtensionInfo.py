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
import configparser
import logging
import os
import re

from .ExtensionSecureID import ExtensionSecureID
from .VersionNr import VersionNr

logger = logging.getLogger(__name__)

EXTENSION_POINT_SECTION_NAME="ExtensionPoints"

class ExtensionInfo:

  """
  The description of a plugin, read from its .mm-plugin file, and
  once loaded the plugin's Extension instance (plugin_object).

  :version: 2.0
  :author:  R Gammans
  """

  @classmethod
  def from_file(cls,infofile):
    """
    Read a plugin description (.mm-plugin) file.
    """
    details = configparser.ConfigParser(interpolation=None)
    with open(infofile,encoding="utf-8") as f:
        details.read_file(f,infofile)
    name   = details.get("Core","Name")
    module = details.get("Core","Module")
    return cls(name,os.path.join(os.path.dirname(infofile),module),details)

  def __init__(self,plugin_name,plugin_path,details=None):
    """
    Create a plugin info instance.

    plugin_path is the plugin's module path without the .py suffix.
    """
    self.name = plugin_name
    self.path = plugin_path
    if details is None:
        details = configparser.ConfigParser(interpolation=None)
    self.details = details
    self.plugin_object = None
    self.is_activated  = False
    self._points = None
    self.secureID= ExtensionSecureID.fromPathName(self.path+".py")

  def __repr__(self):
    return "<%s %s %s>" % (self.__class__.__name__,self.name,self.path)

  def _doc_field(self,field,default=""):
    return self.details.get("Documentation",field,fallback=default)

  @property
  def version(self):
    return VersionNr(self._doc_field("Version","0.0"))

  @property
  def author(self):
    return self._doc_field("Author")

  @property
  def website(self):
    return self._doc_field("Website")

  @property
  def description(self):
    return self._doc_field("Description")

  @property
  def points(self,):
    if self._points is None:
        self._points = { }
        if self.details.has_section(EXTENSION_POINT_SECTION_NAME):
            for opt in self.details.options(EXTENSION_POINT_SECTION_NAME):
                provides = self.details.get(EXTENSION_POINT_SECTION_NAME,opt)
                provides = [ p.strip() for p in re.split(r",",provides) ]
                self._points[opt.lower()]=provides
    return self._points

  def getName(self):
    """
    @return string : Name of the plugin.
    """
    return self.name

  def getSecureID(self):
    """
    Return the secure hash of the plugins source files.

    @return ExtensionSecureID :
    """
    return self.secureID

  def activate(self):
    """
    Activates a loaded plugin - no-op on a plugin which isn't loaded
    """
    if self.plugin_object is not None:
       self.plugin_object.activate()
       self.is_activated = True

  def deactivate(self):
    """
    Deactivates a loaded plugin , this should be a no-op
    on an unloaded plugin - although may be called on a plugin
    when it's trust is removed.
    """
    if self.plugin_object is not None:
       self.plugin_object.deactivate()
    self.is_activated = False

  def isLoaded(self):
    """
    Returns True if the plugin has been loaded into the interpreter
    """
    return self.plugin_object is not None

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
