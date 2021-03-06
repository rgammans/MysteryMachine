#!/usr/bin/env python
#   			MysteryMachine - Copyright R Gammans
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

import MysteryMachine
import sys
import os
    

def process_args():
    """
    Add the currently recommended default args to args list.

    The aim of theis is to merge sys.argv with a set of defaults to
    generate a useful set of startup options for MysteryMachine
    """ 
    if sys.platform == 'win32':
        cfgfile = os.path.join(os.getenv('HOMEDRIVE'),os.getenv('HOMEPATH'),'.mysterymachine.yaml')
    else:
        cfgfile = os.path.join(os.getenv('HOME'),'.mysterymachine.yaml')

    defaults = [ '--cfgengine=ConfigYaml' , '--cfgfile=%s' % cfgfile ]

    options = defaults + sys.argv[1:]

    return options

def main():
    """
    Run Mysterymachine
    """
    options = process_args()
    with MysteryMachine.StartApp(options) as MyMM:
        MyMM.Run()
