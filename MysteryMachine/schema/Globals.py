#!/usr/bin/env python
#   			Globals.py - Copyright Roger Gammans
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
# The original location of this file is /home/roger/sources/MysteryMachine/generated/MMSystem.py
#
#

import weakref
import re
import binascii

import logging

modlogger = logging.getLogger("MysteryMachine.Globals")

##Support functions to allow a single MysteryMachine instance to
# be used to edit multiple systems.
#
# We use a Weak ref here so that the System can be discarded once it
# is finished with.
DocsLoaded = weakref.WeakValueDictionary()

def GetLoadedSystemByName(name):
    return DocsLoaded[name]

def EscapeSystemUri(uri):
    uri = re.sub("%" , "%25" , uri)
    uri = re.sub(":" , "%3a" , uri)  
    return uri

def UnEscapeSystemUri(uri):
    modlogger.warn("*** Func UnEscapeSystemUri Not complete***")
    def findChar(match):
        #TODO Unicode support...
        return  binascii.unhexlify(match.group(1))
    return re.sub("%([0-9a-fA-F]{2})",findChar,uri)


