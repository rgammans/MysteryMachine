#!/usr/bin/env python
#   			MysteryMachine/__init__.py - Copyright Roger Gammans
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
Exceptions used by the MysteryMachine APi
"""

import exceptions

class ExtensionError(RuntimeError): pass
class CoreError(RuntimeError): pass
class DuplicateRegistration(RuntimeError): pass
class NullReference(LookupError): pass
class NoAttribute(LookupError): pass #Specifically no MMAttribute.

class InvalidParent(RuntimeError):
    """
    An object as been passed to set_parent which is not a valid parent.

    A parent must be either an MMObject or a MMNullReference.(NYI)
    Additionally a new object must not already exist on the parents
    parent chain.
    """
    pass

class StoreApiViolation(TypeError):
    """Incorrect types have been base to the StoreApi
     
    The store api requires character buffers for almost all of
    it methods. As these are what is safe to write to a file like
    object.

    You should use a custom value object to do any special transcoding
    """
    pass


class NoPackFileName(RuntimeError):
    """Raised after an attempt to Save when nofile name set
    """
    pass
