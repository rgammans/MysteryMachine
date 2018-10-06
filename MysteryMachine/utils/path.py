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

#Arguably this should be utils/files.py but I'm not
# creating one just for this!
def zunpack(azip,workdir):
    """
    Unpacks an open zipfile instance into workdir.

    This uses azip.extractall() is it exists.
    """
    try:
        azip.extractall(workdir)
    except AttributeError:
        #extractall not in the python2.5 library.
        path = ""
        for inf in azip.infolist():
            #Construct destination path.
            if inf.filename[0] == '/':
                path = os.path.join(workdir, inf.filename[1:])
            else:
                path = os.path.join(workdir, inf.filename)
            path = os.path.normpath(path)
            
            # Create all upper directories if necessary.
            upperdirs = os.path.dirname(path)
            if upperdirs and not os.path.exists(upperdirs):
                os.makedirs(upperdirs)

            if inf.filename[-1] == '/':
                #Found dir entry in zip
                try :
                    os.mkdir(path)
                except OSError  as e:
                    #Ignore file exists error
                    if e.errno != 17: raise e
            else:
                #Do save actual file
                outf = file(path,"w")
                outf.write(azip.read(inf.filename))
                outf.close()

