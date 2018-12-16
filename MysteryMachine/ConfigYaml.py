#!/usr/bin/env python
#           ConfigYaml.py - Copyright Roger Gammans
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
This module provides a MysteryMachine configuation engine
based on python's Yaml module.
"""

import yaml
import logging

def argshift(args,default):
    """
    return (args[0] , args[1:])  or (default , [] ) if args empty.
    """

    value=default
    remaining=[]
    if len(args)>0:
        value=args[0]
        if len(args)>1:
            remaining=args[1:]

    return value,remaining 



class ConfigYaml(object):
    def __init__(self,*args,**kwargs):
        self.persistent,args = argshift(args,True)
        self.readonly ,args = argshift(args,False)
        self.logger = logging.getLogger("MysteryMachine.ConfigYaml") 

    def __setitem__(self, name, value):
        if self.readonly: raise ReadOnly()  
        else: self.modified=True
        
        #TODO Create dict if necessary
        try:
            for k, v in value:
                self.cfg[name][k] = v
        except Exception:
            self.cfg[name] = value


    def __delitem__(self, name):
        if self.readonly: raise ReadOnly()
        else: self.modified=True

        del self.cfg[name]

    
    def __getitem__(self,k):
        return self.cfg[k]

    def __iter__(self):
        for i in self.cfg:
            yield i
 
    def testmode(self):
        self.persistent=False
        self.readonly=False

    def read(self,filename):
        self.filename=filename
        try:
            with open(self.filename,"r") as f:
                self.cfg = yaml.safe_load(f)
        except IOError as e:
            self.logger.debug(str(e))
            self.logger.warn("Using empty config")
            self.cfg = { }
            #If not FILE NOT FOUND , disable writeback.
            # to avoid clobbering an otherwise good config.
            if e.errno != 2: self.filename=None

    def write(self):
        if not self.persistent: return
        if self.filename:
            with open(self.filename,"w") as f:
                yaml.dump(self.cfg,f)
