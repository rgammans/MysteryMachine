#!/usr/bin/env python
#   			utils/path.py - Copyright Roger Gammans
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
#


"""
Mystery machine path utilites.

Functions here are not part of the formal MysteryMachine interface
but are likely to stay here. 

This file contains miscellanous routines useful for path manipulation
which cannot be found in os.path.
"""

import os

def make_rel(root,*paths):
    """
    Return each element of paths relative to root
    """
    rootdirs = root.split(os.path.sep)
    rpaths = []
    for path in  paths:
        p = path.split(os.path.sep)
        for dir in rootdirs:
            #Remove each matching dir element.
            if p[0] == dir: p = p[1:]
            else: break 
    
        if len(p) == 0: rpaths += [ "." ]
        else:           rpaths += [ os.path.join(*p) ]
        #On unix root comes out as the empty element here
        if rpaths[-1] == "" : rpaths[-1] =os.sep
    return rpaths
