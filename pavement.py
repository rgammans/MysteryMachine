#!/usr/bin/env python
#   			paverment.py - Copyright Roger Gammans
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
# d


#
# Find the current state of setuptools..
#


existing_setuptools_available   = False
try:
    import setuptools
    existing_setuptools_available = True
except Exception:
    pass

ez_setup_available = False
try:
   import ez_setup
   version = ez_setup.DEFAULT_VERSION
   if existing_setuptools_available:
        version = setuptools.__version__
   ez_setup.use_setuptools(version = version)
   ez_setup_available = True
except ImportError:
   pass

easy_install_available = False 
try:
    import setuptools.command.easy_install
    easy_install_available = True
except ImportError:
    pass


DIST_PACKAGES = [ "yapsy" , "MysteryMachine","MysteryMachine.schema",
                 "MysteryMachine.store","MysteryMachine.parsetools",
                 "MysteryMachine.Ui",
                 "MysteryMachine.Ui.wx","MysteryMachine.Ui.wx.dialogs",
                 "MysteryMachine.utils",
                 "MysteryMachine.policies" , "MysteryMachine.document"  ]

PY_MODULES  = [ 
                #'pyparsing',
               ]

##Read dependencies in from requirements.txt
with open("requirements.txt") as f:
    EZ_PACKAGES  = f.readlines()


TESTSDIR = "tests"
FILES = [ "AUTHORS", "CodingGuidelines", "OriginalDesign" ,"README",
          "paver-minilib.zip" ]
DIRS  = ["docs" , "examples" ,"graphics", "scripts" ,"patches" ,
         "MysteryMachine/TrustedPlugIns", TESTSDIR ]
SCRIPTS = [ 'setup.py' , 'ez_setup.py' ]

VENVSCRIPT = 'install.py'

PYTHONS= [ "python" ]


##Windows compat hack
FileErrors = [OSError ]
try:
    FileErrors.append(WindowsError)
except NameError:pass
FileErrors = tuple(FileErrors)

import sys
import os
import shutil
import atexit

from paver.easy import *
from paver.setuputils import setup

def find_all(path,dirname):
    for dir,dirs,files in os.walk(path):
        for file in files:
            if re.search("~$",file): continue
            if re.search("\.pyc$",file): continue
            if re.search("^\.",file): continue
            if re.search("\.orig$",file): continue
            filename = os.path.join(dir,file)
            yield filename



@task
@needs('generate_setup','minilib','src_environ')
def sdist():
    """Create a source distribution (tarball, zip file, etc.)"""
    global SCRIPTS

    pkgs = {}
    path = sys.path
    path.insert(0,".")
    for pkg in DIST_PACKAGES:
       pkgdir  = pkg.split(".")
       for dir in sys.path:
            if os.path.isdir(os.path.join(dir,*pkgdir)):
               try:
                   #Put all our need packages in the local directory.
                   os.symlink(os.path.join(dir,*pkgdir),os.path.join(pkgdir[0],*pkgdir[1:]))
               except Exception:
                   pass

    for pkg in PY_MODULES:
        filedir = pkg.split(".")
        filedir[-1] = filedir[-1]+ ".py"
        for dir in sys.path:
            #Check for package as standalone file
            if os.path.exists(os.path.join(dir,*filedir)):
               try:
                   #Put all our need packages in the local directory 
                   shutil.copy(os.path.join(dir,*filedir),os.path.join(filedir[0],*filedir[1:]))
                   #Register deletion of new filefor when we've finished..
                   if os.path.realpath(".") != os.path.realpath(os.path.join(filedir[:-1])):
                       atexit.register(os.remove,os.path.join(filedir[0],*filedir[1:]))
               except Exception:
                   pass

    #Create find data files scripts etc needed for sdist.    
    for dir in DIRS:
         for file in find_all(dir,dir):
            SCRIPTS += [ file ]

    SCRIPTS += FILES
    SCRIPTS += VENVSCRIPT 

    #If ez_setup.py is not on our sys.path.
    if not ez_setup_available:
        import urllib
        urllib.urlretrieve("http://peak.telecommunity.com/dist/ez_setup.py","ez_setup.py")
         

    paver.virtual.bootstrap() 
    call_task("setuptools.command.sdist")

import re
STRIP   = re.compile('\.py$')

@task
def test():
    """Run MysteryMachine units tests from the source distribution
        with the default python"""
    _do_test( [ os.curdir ] )

@task
def test_installed():
    """Run MysteryMachine units tests on the Installed MysteryMachine distribution
        with the current python"""


    global PYTHONS
    PYTHONS = [ sys.executable ]
    _do_test()

def _do_test(path_prefix=[]):
    path=os.getenv("PYTHONPATH")
    add_path = os.pathsep.join(path_prefix)
    if path == None:
        path = add_path
    else:
        path = path+os.pathsep+add_path
    
    if path: os.putenv("PYTHONPATH",path)

    for python in PYTHONS:
        sys.stderr.write( "Testing under %s:\n" % python )
        #run tests.
        sys.stderr.write("Running tests with %s" % (python) )
        os.system("%s -m unittest discover -p '*.py' -s %s" % ( python,  TESTSDIR ))



def relaunch_self(extra_args):
    """Relaunches this process with additional arguments"""
    args = [ sys.executable ] + sys.argv + extra_args
    #Start again, 
    os.execv(sys.executable,args)

@task
#should install mercurial
def dst_environ(options):
    """Install MysteryMachine dependencies that setuptools can't handle without help"""
    #Currently there are none of these. Woot!.
    pass

@task 
@cmdopts([('srcenv-loop=', 'l' ,'internal use only - used to detect infinite loops')])
def src_environ(options):
    """Install packages necessary for the installer in the source environment"""
    print "verifying src environment"
    try:
        import virtualenv
        print "virtual env already here - nothing to do"
    except ImportError:
        if int(options.src_environ.get('srcenv_loop',0)) == 1:
            raise LogicError("Virualenv install loop detected")
        print "trying to install virtualenv"
        if easy_install_available:
            print ".with easy_install"
            print "calling easy_install"
            old_args = sys.argv
            sys.argv = ['fake', 'virtualenv']
            import setuptools.command.easy_install
            setuptools.command.easy_install.main()
            sys.argv = old_args
        else:
            print "...giving up - can't install virtualenv"
 
    #Hope all is well
    print "importing paver virtual"
    import paver.virtual
    if not paver.virtual.has_virtualenv:
        relaunch_self(["--srcenv-loop","1"])
        #**** NEVER GETS HERE - Relaunch DOES NOT RETURN****
   
    if sys.platform[:3] == 'win':
        try:
            ##This is a workaround for issue 40 in virtualenv
            import FixTk
            #Fix Tk sets some useful envvars that the virtual env will need
            tk=open("FixTk.py","w")
            tk.write("import os\n")
            tk.write("os.environ[\"TCL_LIBRARY\"]=\"%s\"\n" % os.environ["TCL_LIBRARY"])
            tk.write("os.environ[\"TK_LIBRARY\"] =\"%s\"\n" % os.environ["TK_LIBRARY"])
            tk.write("os.environ[\"TIX_LIBRARY\"]=\"%s\"\n" % os.environ["TIX_LIBRARY"])
            tk.close()
            options.setup.py_modules += ['FixTk']
        except ImportError:
            pass            
    else:
        #Bpython is worth install on the Unix & Macs.
        if 'bpython' not in  options.virtualenv.packages_to_install:
            options.virtualenv.packages_to_install.append('bpython')
 
@task
@needs('dst_environ')
@cmdopts([('no-tests', 'n' ,'suppress post-install tests')])
def install_here():
    """Install everything from the build dir into t)he current env.
   
    This does the usual install thing installing all of the MysteryMachine
    packages and there dependencies into the current environment.

    If you wish to install MysteryMachine into your global environement
    this /might/ be want you want.    
    """
    call_task('setuptools.command.install')
    #Check the plugins (TrustedPlugins directory has been installed.

    ##We do this here since the MysteryMachine directory should have been
    ## created by now, and by using the import we can hopefully, ensure
    ## consistency.
    oldpath  = sys.path
        #Remove local dir from serahc path so we find the installed lib
    try:
        sys.path.remove("paver-minilib.zip")
    except ValueError:pass
    try:
        sys.path.remove("")
    except ValueError:pass
    try:
        sys.path.remove(".")
    except ValueError:pass
    from MysteryMachine.ExtensionLib import DEFAULT_TRUSTEDPLUGIN_PATH
    print DEFAULT_TRUSTEDPLUGIN_PATH
    shutil.copytree("MysteryMachine/TrustedPlugIns", DEFAULT_TRUSTEDPLUGIN_PATH)
    sys.path = oldpath
 
    #Do a final test of the installation.
    if not options.install_here.get('no_tests',False):
        call_task('test_installed')


@task
@needs('src_environ')
@cmdopts([('installdir=', 'd' ,'Directory to install MysteryMachine into'),
          ('no-tests', 'n' ,'suppress post-install tests')])
def install(options):
    """Create a virtual environment and install into it.

    You problably want this option as it ensures MysteryMachine doesn't
    touch your systemwide yapsy install. 

    MysteryMachine currently requires a patched version of ypasy, so 
    installing mysterrymachine virtually means we don't break any
    existing python scripts on your system. 
    """
    #options(virtualenv = Bunch(dest_dir = options.install.installdir,
    #                           paver_command_line = "install_here"))

    # We can't add this a a dependencies - because it needs virtualenv
    # which might not exist and dependency resolution.
    call_task('paver.virtual.bootstrap')

    here = os.getcwd()
    try:
        os.mkdir(options.install.installdir)
    except OSError, e:
        if e.errno != 17: raise e

    os.chdir(options.install.installdir)
    #call Pre built install file , creates virtual environment etc..
    import subprocess
    subprocess.call([sys.executable , os.path.join(here,"install.py")])
    os.chdir(here)
    #Relaunch paver to install ourself into the newly setup virtualenv.
    # -but first find our paver executable..
    places_to_look = [
            os.path.join(options.install.installdir,"bin","paver"),
            os.path.join(options.install.installdir,"scripts","paver")
    ]
    ## Add system path
    places_to_look.extend([ os.path.join(x, 'paver')  for x in os.getenv('PATH').split(os.pathsep) ])

    for paver in places_to_look:
        try:
            os.stat(paver)
        except FileErrors:pass
        else: break
    else:
        print paver
        raise RuntimeError("Paver binary not found")

    call_data = [paver,"-f",os.path.join(here,"pavement.py"),"install_here" ,]
    if options.install.get('no_tests',False):
        call_data.append('--no-tests')
    
    subprocess.call(call_data)


setup(name ="MysteryMachine",
      packages = DIST_PACKAGES ,
      scripts  = SCRIPTS ,
      py_modules =PY_MODULES,
      version  = "0.4.0", 
      install_requires = EZ_PACKAGES,
      url="http://trac.backslashat.org/MysteryMachine",
      author="Roger Gammans",
      author_email="rgammans@computer-surgery.co.uk",
      license = "GPLv2",
      entry_points={ 'console_scripts': [
                         "mysterymachine = MysteryMachine.Main:main",
                         "mmcli         = MysteryMachine.Ui.cli:main",
                         "mmwx          = MysteryMachine.Ui.wx:main"
                   ]},
      package_data= paver.setuputils.find_package_data(".", package="paver",
                                            only_in_packages=False),
    )

options(
    virtualenv = Bunch(
        script_name = VENVSCRIPT, 
        packages_to_install =  EZ_PACKAGES ,
        no_site_packages = False,
    ),
    minilib = Bunch(
        extra_files = ['virtual']
    )
)
