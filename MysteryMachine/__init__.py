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
Mystery Machine
===============

The mystery machine is an application with a strong plugin architecture
target at writing freeform and murder mystery style games.

This base modules encapuslates the globals for the mystery machine
system.
"""

from __future__ import with_statement

import mercurial
import mercurial.ui
import sys
import types
import re
import threading
from contextlib import contextmanager

import tempfile
import zipfile
import os

from MysteryMachine.ExtensionLib import ExtensionLib
from MysteryMachine.ConfigDict import pyConfigDict
from MysteryMachine.ConfigYaml import ConfigYaml
from MysteryMachine.Exceptions import *

#Global vars
#Configuration details...
defaults=dict()

def set_mysterymachine_default(name,value):
    """
    This is global routine for modules (rather than extensions) to
    register global default values.

    This aim is this should be called as earlier as possible - before
    any instances are created. The main routine will use these defaults
    to aid in configuring various options. Including the configuration
    engine itself. The Gui module , our script support modules may
    be the main users of these so that the full Gui config engine isn't
    loaded for quick scripts.

    Don't set these unless you really have to as if two modules set the
    same setting it may not be reliable as to witch one sticks.

    These defaults should be called before a LibraryContext instance
    is created throught startapp. So these are the has to be a module global.
    """
    global defaults

    defaults[name]=value

def get_mysterymachine_default(name,defvalue=None):
    global defaults

    value=defvalue
    if name in defaults:
        value=defaults[name]
    return value

 
#We could use getopts here - but that needs a list of options
#  - this doesn't.
def parse_options(args):
    """
    Generic zero knowledge command line options parser.
    
    This function treats all input as either an option, or an
    argument. There is no such thing as unknown options, they all 
    all treated equally.

    Options syntax understood 
        short options -x, -x val , or -xval
        long  options --option , --option value , or --option=value
        end of options can be signalled by '--'

        Anything not in the above form or that follows '--' is treated as an
        argument

    Returns: opts(dict), args(list)
    """
    #Basic syntax regex for options.
    option=re.compile("^-(([\w])|(-([\w]+)))[=\s]?([^\s]+)?")

    #Setup initial 'state'
    state=None
    out_args=list()
    out_opts=dict()

    #iterate around options
    for opt in args:
        #Are we waiting on a value...
        if opt == "--":
            state=opt
            continue
        #No lets match to see if this is an option specifier
        found =option.match(opt)
        if found and state != '--':
            if not state is None:
                #Valueless option detected.
                out_opts[state]=None
            found=found.groups()
            #Check for short of long opt and get appropriately
            if len(found[0]) ==1:
                state=found[1]
            else:
                state=found[3]
            #If option value is specified in this arg apply it immediately
            if (not found[4] is None) and len(found[4]) > 0:
                out_opts[state]=found[4]
                state=None 
        elif (state == None) or (state == '--'):
            #Either in state '--' which indicates we reached an end of opts specifier
            # or we have a value we no option - treat as an argument.
            out_args += [ opt ]
        else:
            #State indicates we are waiting for a value.
            out_opts[state]=opt
            state=None
    
    #Handle any dangling options. (nonvalue options specified last) 
    if not (state is None or state == "--"):
        out_opts[state]=None

    return out_opts, out_args


class _SingletonWithExternalLocking(type):
    """
    An internal singleton metaclass 
    """
    def __init__(self, name, bases, dict):
        super(_SingletonWithExternalLocking, self).__init__(name, bases, dict)
        self.instance = None
        self.mutex = threading.Lock()
 
    def __call__(self, *args, **kw):
        if self.instance is None:
            self.instance = super(_SingletonWithExternalLocking, self).__call__(*args, **kw)
 
        return self.instance

    def IsInstantiated(self):
        return self.instance is not None
 
    @contextmanager
    def Lock(self):
        """
        A context manager design to protect the singleton from construction 
        races. I doubt these are common - but its good practice to lock if possible.

        Bear in mind the use of the  IsInstantiated() / __init__() pair in StartApp
        has a natural race as well which could cause some nasties without locking.
        """
        self.mutex.acquire()
        try:
            yield True
        finally:
            self.mutex.release()

class _LibraryContext(object):
 
    __metaclass__ = _SingletonWithExternalLocking
 
    def __init__(self,args):
        ###DO all initialisation.

        self.cmdline_options,self.args=parse_options(args)

        ##Initiliase Config engine.
        self.cfg_engine = self.get_app_option_object("cfgengine")
        self.cfg_engine.read(self.get_app_option_object("cfgfile"))
        if "testmode" in self.cmdline_options:
            self.cfg_engine.testmode()    
        
        #Initialise Extlib
        self.ExtLib=ExtensionLib(self.cfg_engine)
        #TODO Check config for Ui data.
        self.Ui = None    

    def close(self):
         ## Do our Application finalisation here.
        self.cfg_engine.write()

        # TODO Write close action to logfile. 
        #     (Important so we can trace any bug provoked by an early close).
 
        #Delete our context to force a reinit
        self.__class__.instance = None

        #Zero our our members in case of a stored reference to us.
        self.cfg_engine = None
        self.ExtLib = None
        

    def Run(self):
        """
        If an extension with mainloop has been registered and select call it.
        """
        if self.Ui is not None:
            self.Ui.Run()


    def GetExtLib(self):
        """
        Returns the extension lib instance to use.
        """
        return self.ExtLib

    def GetMercurialUi(self):
        """
        Gets a mercurial ui instance to use when calling mercurial api
        functions.
        """
        if self.Ui == None:
            return mercurial.ui.ui()
        else:
            return Ui.mercurial_ui()

    def get_app_option(self,name):
        """
        Find application level option 'name'.

        The function first checks the configuration engine if
        it has been initialised, and then checks the command line options.

        Finally it checks the system defaults.
        """   
        val=None 
        
        if name in self.cmdline_options:
            return self.cmdline_options[name]

        if self.cfg_engine != None and name in self.cfg_engine:
            return self.cfg_engine[name]   

        return get_mysterymachine_default(name,None)

    def get_app_option_object(self,name):
        """
        This is the same as get_app_option, but instanties a 
        object of the value's class iff the value has type str.

        This function DOES NOT import any more modules so the
        value must be a callable at the main level scope, and
        take no arguments.
        """
        val=self.get_app_option(name)
        if type(val) in types.StringTypes:
            #Call 'val' with no args.
            if val in globals():
                val=(globals()[val])()
        return val

    def GetStoreBases(self,classspec):
        rv = []
        for line in classspec:
            line = re.sub("^\s+","",line)
            line = re.sub("\s+$","",line)
            sys.stderr.write(line + "\n" )
            #TODO: Error reporting - this file is untrusted remember
            lib,classname,req_version = re.split('\s+',line)
            ext = self.GetExtLib().getExtension(lib,version  = req_version)
            print "MMI-GSB: ext = %s"%ext
            print "MMI-GSB: extobj = %s"%ext.plugin_object
            if ext is None:
                raise ExtensionError("Can't find %s" % lib)
            elif 'storeclass' not in ext.plugin_object.getInterfaces(): raise ExtensionError("storeclass interfaces not advertised")
            rv +=  [ ext.plugin_object.getStoreMixin(classname,version) ]
        return rv

    def OpenPackFile(self,filename):
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
        try:
            pack.extractall(workdir)
        except AttributeError:
            #extractall not in the python2.5 library.
            path = ""
            for inf in pack.infolist():
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
                    os.mkdir(path)
                else:
                    #Do save actual file
                    outf = file(path,"w")
                    outf.write(pack.read(inf.filename))
                    outf.close()

        pack.close()
        #Read store requirements
        store = file(os.path.join(workdir,".store"))
        storestr = store.readlines()
        store.close()
        #Load exts etc,
        bases = self.GetStoreBases(storestr)
        #Build store class.
        storetype = type(filename,bases, { 'scheme': aname} )
        mmstore = GetStore(aname+":"+workdir)
        log = list(mmstore.getChangLog())
        #Unpack last rev into working dir and open MMsyste,
        mmstore.revert(log[len(log)-1])
        return MMSystem(mmstore)   

    def SavePackFile(self,system,filename,**kwargs):
        """
        Save an opened MMSystem into a packed file - commiting first
        with the message argument as the commit msg if supplied.
        """
        system.commit(kwargs.get('message'))
        system.clean()
        pack = ZipFile(filename,"w")
        #FIXME Use locker object here.
        system.lock()
        for file in os.walk(system.store.get_path()):
            pack.add(file)
        pack.close()
        system.unlock()
            
    def CreateNewSystem(self,**kwargs):
        """
        Creates a new MMSytem.

        Confugration arguments provided overirde the application
        defaults.
        """


            
class StartApp(object):
    """
    Start up the main Mystery machine application.

    This class is a context manager for the main LibraryContext. We allow
    StartApp(..) to create nested contexts. However for simplicity these contexts
    must be strictly nested. The first one created always destroys the context.

    This should be easy to achieve by wrapping your main routine with a with StartApp..
    """
    def __init__(self,args = [ ]):
        with _LibraryContext.Lock() as  lck:
            self.primary = not _LibraryContext.IsInstantiated()
            if self.primary and len(args) ==0: 
                #We could allow the app to continue on with some defaults - but it's more likely
                # to mean that application writer hasn't initiallised the MM library.
                raise RuntimeError("Arguments required - MM should probably have been initialised before the program got this far.")
            self.maincntxt = _LibraryContext(args)
  
    def __enter__(self):
        return  self.maincntxt
    
    def __exit__(self,exctype,excvalue,tb):
        if self.primary:
            self.maincntxt.close()

if __name__ == '__main__':
   with StartApp(sys.argv[1:]) as MyMM:
        MyMM.Run()
