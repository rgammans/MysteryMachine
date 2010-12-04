#!/usr/bin/env python
#               CorePluginManager.py - Copyright roger
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
# This file was generated on Mon Feb 2 2009 at 22:51:50
# The original location of this file is /home/roger/sources/MysteryMachine/generated/TrustedPluginManager.py
#
#
"""
This module is a manages the MysteryMachine core plugins, ie. those
which are distributed with it and are always considered trusted.



"""

##
#This module is also quite empty - but it means the only direct calls into
# yapsy are contained in the PluginManagers, ExtensionInfo and Extension modules
# and outside the Mysterymachine core (including ExtensionLib )
#

from yapsy.PluginManager import *
from ExtensionInfo import *
import types

class CorePluginManager(PluginManager):
    pass


