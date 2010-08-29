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


from MysteryMachine.VersionNr import VersionNr
import MysteryMachine.utils as utils
import MysteryMachine.utils.path 
import MysteryMachine.store as store
import MysteryMachine.Exceptions as Exceptions

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


def GetStoreBases(classspec):
    """
    This function finds a list of base classes used by a MMSystem.

    It is intended for use by version 1.x and later of the Pack format.
    *** UNTESTED CODE ***
    """
    rv = []
    line_nr=0
    for line in classspec:
        line_nr+=1
        line = re.sub("^\s+","",line)
        line = re.sub("\s+$","",line)
        modlogger.debug("basespec line %s",line )
        if len(line) == 0:
            continue
        #TODO: Error reporting - this file is untrusted remember
        try:
            schemename,req_version = re.split('\s+',line)
        except ValueError, e:
            raise Exceptions.CoreError("Invalid classspec at line %i (error:%s)"%(line_nr,e.message))
            
        ext = self.GetExtLib().findPluginByFeature("StoreScheme" , schemename ,version  = req_version)
        modlogger.debug( "MMI-GSB: ext = %s"%ext)
        if ext is None:
            raise Exceptions.ExtensionError("Can't find %s" % lib)

        self.getExtLib().loadPlugin(ext)
        modlogger.debug( "MMI-GSB: extobj = %s"%ext.plugin_object)
        rv +=  [ ext.plugin_object.getStoreMixin(classname,req_version) ]
    return rv


def LoadFormat0(workdir,formatfile):
    formatfile.close()
    return OpenVersion0(workdir,"hgafile")
formatLoaders.append( (VersionNr('0'),VersionNr('1'),LoadFormat0 ) )

def LoadFormat1(workdir,formatfile): 
    ##FIXME: Test this code etc.
    # A stub of what the code should do is below, but
    # it turns out we've got issues with the extensions engine.
    #raise Exceptions.CoreError("Version 1 suport not implemented")
    #Read store requirements
    formatDescriptors = formatfile.readlines()
    #Load exts etc,
    for desc in formatDescriptors:
        desc = re.sub("^\s+","",desc)
        desc = re.sub("\s+$","",desc)
        modlogger.debug("spec line %s",desc )
        if len(desc) == 0:
            continue
        desctype,line = re.split('\s+',desc)
        handleType(desctype,line)

    return OpenVersion0(workdir,schema)
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

    return formatHandler(workdir,formatfile)



def OpenVersion0(workdir,scheme):
    """
    Handles version Zero of the pack format.

    Version 0 of the pack format is a zipfile of the .hg
    directory. It guarantees to use a hgfile_mixin and file_store.

    """
    mmstore = store.GetStore(scheme+":"+workdir)
    log = list(mmstore.getChangeLog())
    #Unpack last rev into working dir and open MMsystem
    mmstore.revert(log[len(log)-1])
    #Late import since MMSystem depends on this module - we only load 
    # it at run time once we have been fully compiled.
    from MysteryMachine.schema.MMSystem import MMSystem
    return MMSystem(mmstore)   

def SavePackFile(system,filename,**kwargs):
    """
    Save an opened MMSystem into a packed file - commiting first
    with the message argument as the commit msg if supplied.
    """
    system.Commit(kwargs.get('message'))
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
