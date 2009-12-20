#!/usr/bin/env python
#   			hgfile_store.py - Copyright Roger Gammans
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


"""
A pacakge to contain the filestore engine used by Version 0 of the pack
format. This package may go away at any time - DO NOT Directly USE.

In the future store classes will be loaded through the MysteryMachine.GetStoreBase()
interface.
"""

from MysteryMachine.store.file_store import filestore
from MysteryMachine.store.hgfile_store import HgStoreMixin

class HgFileStore(HgStoreMixin,filestore):
    uriScheme = "hgafile"
