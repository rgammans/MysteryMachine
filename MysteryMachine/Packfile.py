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

from __future__ import with_statement

from MysteryMachine.VersionNr import VersionNr
import MysteryMachine
import MysteryMachine.utils as utils
import MysteryMachine.utils.path 
import MysteryMachine.store as store
import MysteryMachine.Exceptions as Exceptions
from MysteryMachine.schema.MMSystem import MMSystem
from MysteryMachine.Exceptions import *

import datetime
import tempfile
import zipfile
import os
import re
import logging
modlogger = logging.getLogger("MysteryMachine.Packfile")


"""
Mystery Machine Packfiles
=========================

A mystery machine packfile contains the relevant information to open a MMSystem.

In most cases the packfile will contain all of the data and meta-data about how
to access the systems store, but in some cases the packfile may contain nothing
more than a reference to a networked resource.

Each packfle contains a .fo0rmat (or in earlier versions a .formatver) file which
is used by main packfile parsing code to find the appropriate plugins, store etc
which are need to provide access to the MMSystem indicated by or containing in
the packfile.

Packfile are a store agnostic part of MysteryMachine and all store should be able
to work with Packfiles, even if they only safe a network URL into the file.

Packfiles outer format is zip. Filenames starting with a period are reserved
for the use of this module and the Core mysterymachine code.

The only Guarantee provide is that these files will not clash in name with attribute
at the system level. It is acceptable for these files to be treated as System 
atributes by a a store - but it is not required.
"""


#Redirect to LoaderMethod format.
formatLoaders = [ ]

PACKFORMAT_EXTPOINTNAME ="PackFileDescriptor"
PACKFILENAME = "packfile_filename"

def GetStoreBases(line,flags):
    """
    This function finds a store scheme name. 

    It is intended for use by version 1.x and later of the Pack format.
    *** UNTESTED CODE ***
    """
    rv = []
    line = re.sub("^\s+","",line)
    line = re.sub("\s+$","",line)
    modlogger.debug("basespec line %s",line )
 
    #TODO: Error reporting - this command is untrusted remember
    try:
        schemename,req_version = re.split('\s+',line)
    except ValueError, e:
        raise Exceptions.CoreError("Invalid schema spec at line %i (error:%s)"%(flags['line_nr'],e.message))
        
    flags["schema"] = schemename
    flags["schema_version"] = req_version
    flags["schemaclass"] = store.GetStoreClass(schemename , req_version)


def LoadFormat0(workdir,formatfile,startup_flags = {}):
    formatfile.close()
    return OpenVersion0(workdir,"hgafile",startup_flags)
formatLoaders.append( (VersionNr('0'),VersionNr('1'),LoadFormat0 ) )



def _processFormatLine(cmd,line,flags):
    with MysteryMachine.StartApp() as ctx:
        for plugin in ctx.GetExtLib().findPluginByFeature(PACKFORMAT_EXTPOINTNAME,cmd):
            ctx.GetExtLib().loadPlugin(plugin)
            plugin = plugin.plugin_object
            if hasattr(plugin,PACKFORMAT_EXTPOINTNAME  + "Cmd_" + cmd):
                getattr(plugin,PACKFORMAT_EXTPOINTNAME + "Cmd_" + cmd)(line,flags)
            else:
                raise Exceptions.CoreError("Can't process packfile directive %s(%s)" %(cmd,line))

def LoadFormat1(workdir,formatfile,startup_flags = {} ): 
    #Read store requirements
    formatDescriptors = formatfile.readlines()
    #Load exts etc,
    startup_flags['line_nr'] = 0
    for desc in formatDescriptors:
        startup_flags['line_nr']+=1
        desc = re.sub("^\s+","",desc)
        desc = re.sub("\s+$","",desc)
        modlogger.debug("spec line %s",desc )
        if len(desc) == 0:
            continue
        desctype,line = re.split('\s+',desc,maxsplit=1)
        _processFormatLine(desctype,line,startup_flags)
        #print startup_flags
    
    if "schema" not in startup_flags: raise Exceptions.CoreError("No schema specified in packfile")
    return OpenVersion0(workdir,startup_flags["schema"], startup_flags)

formatLoaders.append((VersionNr('1'),VersionNr('2'),LoadFormat1 ) )

def OpenPackFile(filename):
    """
    Returns a MMSystem object representing the contents of a packfile.

    This function unpacks the pack file into temporary store (found
    using mkdtemp(). It then reads the meta-data to contruct an appropriate
    store class, instantiate it. This store class is use to initialise
    a new MMSystem object.
    """
    #Unpack pack file..
    workdir = tempfile.mkdtemp("mm-working")
    pack = zipfile.ZipFile(filename,"r")
    utils.path.zunpack(pack,workdir)
    pack.close()

    #Read format version requirements - very early versions used .formatver 
    # but that has been deprecated in favour of a more complex .format file.
    try:
        formatfile = file(os.path.join(workdir,".format"))
    except IOError , e:
        try:
            modlogger.debug("Loader cant find .format, falling back to .formatver")
            formatfile = file(os.path.join(workdir,".formatver"))
        except IOError, e2:
            raise (e2 , e)

    version = VersionNr(formatfile.readline())
    
    for lowestVer,highestVer,formatHandler in reversed(formatLoaders):
        if ( version >= lowestVer ) and (version < highestVer) :
            break

    return formatHandler(workdir,formatfile  , startup_flags = { PACKFILENAME: filename } )



def OpenVersion0(workdir,scheme,flags = { } ):
    """
    Handles version Zero of the pack format.

    Version 0 of the pack format is a zipfile of the .hg
    directory. It guarantees to use a hgfile_mixin and file_store.

    """
    system = MMSystem.OpenUri(scheme+":"+workdir,flags)
    log = list(system.getChangeLog())
    #Unpack last rev into working dir and open MMsystem
    system.Revert(log[0])
    return system



def SavePackFile(system,*args,**kwargs):
    """
    Save an opened MMSystem into a packed file - commiting first
    with the message argument as the commit msg if supplied.
    """
    flags = kwargs.get("flags",{})
    filename = flags.get(PACKFILENAME)
    if len(args) > 0: filename = args[0]
    if not filename: raise NoPackFileName()

    if not system.store.uptodate():
        default_commit_message = "Auto commit for packfile save at %s"%datetime.datetime.now()
        system.Commit(kwargs.get('message',default_commit_message))

    system.store.clean()
    f  = file(filename,"w")
    pack = zipfile.ZipFile(filename,"w")
    #FIXME Handle versions better
    pack.writestr(".formatver","0")
    #FIXME Use locker object here.
    system.Lock()
    rootpath = system.store.get_path()
    for path,dirs,files in os.walk(rootpath):
        for filename in files: 
            absname  = os.path.join(path,filename)
            relname, = utils.path.make_rel(rootpath,absname)
            pack.write(absname,arcname = relname)
    pack.close()
    system.Unlock()

    #Ensure data is on safe media.
    os.fsync(f.fileno())
    f.close()

