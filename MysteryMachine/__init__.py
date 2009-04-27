"""
Mystery Machine
===============

The mystery machine is an application with a strong plugin architecture
target at writing freeform and murder mystery style games.

This base modules encapuslates the globals for the mystery machine
system.
"""

import mercurial
import sys
import types
import re



from MysteryMachine.ExtensionLib import ExtensionLib
from MysteryMachine.ConfigDict import pyConfigDict

#Global vars
#Singleton objects.
Ui = None
ExtLib = None

#Configuration details...
cmdline_options=dict()
cfg_engine=None
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
    """
    defaults[name]=value

def get_mysterymachine_default(name,defvalue=None):
    value=defvalue
    if name in defaults:
        value=defaults[name]
    return value


def get_app_option(name):
    """
    Find application level option 'name'.

    The function first checks the configuration engine if
    it has been initialised, and then checks the command line options.

    Finally it checks the system defaults.
    """   
    val=None 
    
    if cmdline_options and name in cmdline_options:
        return cmdline_options[name]

    if cfg_engine != None:
        return cfg_engine.get_option("Global",name)    

    return get_mysterymachine_default(name,None)

def get_app_option_object(name):
    """
    This is the same as get_app_option, but instanties a 
    object of the value;s class iff the valehas type str.

    This function DOES NOT import any more modules so the
    value must be a callable at the main level scope, and
    take no arguments.
    """
    print name
    val=get_app_option(name)
    print val
    if type(val) in types.StringTypes:
        #Call 'val' with no args.
        if val in globals():
            print "calling %s" %val 
            val=(globals()[val])()
    print val
    return val

def GetExtLib():
    """
    Returns the extension lib instance to use.
    """
    return ExtLib

def GetMercurialUi():
    """
    Gets a mercurial ui instance to use when calling mercurial api
    functions.
    """
    if Ui == None:
        return mercurial.ui.ui()
    else:
        return Ui.mercurial_ui()

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

    print "--------", out_opts,out_args ,"-----"
    return out_opts, out_args
 

def StartApp(args):
    """
    Start up the main Mystery machine application.
    """
    global cmdline_options
    global ExtLib 

    ##Initiliase Config engine & Extentions library.
    cmdline_options,args=parse_options(args)
    cfg_engine = get_app_option_object("cfgengine")
    cfg_engine.read(get_app_option_object("cfgfile"))
    if "testmode" in cmdline_options:
        cfg_engine.testmode()    
    ExtLib=ExtensionLib(cfg_engine)


if __name__ == '__main__':
   StartApp(sys.argv[1:])
