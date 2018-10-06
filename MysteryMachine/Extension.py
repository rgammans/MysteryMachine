#!/usr/bin/env python
#   			Extension.py - Copyright roger
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
# This file was generated on Sat Feb 7 2009 at 14:48:36
# The original location of this file is /home/roger/sources/MysteryMachine/generated/Extension.py
#
#

from yapsy.IPlugin import IPlugin

class Extension (IPlugin):

  """
   This is the class from which and extension interacts with the 
   system.
   On Activation an extension should register it's views with the
   Plugin Manager and any mixin's etc with the ExtensionLibrary.
  
   :author: R Gammans`
  """
  def __init__(self):
    IPlugin.__init__(self)

  def getInterfaces(self):
    raise Exception("This function must be overriden")


  def getMixinTargets(self):
    raise Exception("This function must be overriden")


