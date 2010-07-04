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
#


#
# Find the current state of setuptools..
#


existing_setuptools_available   = False
try:
    import setuptools
    existing_setuptools_available = True
except:
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
                 "MysteryMachine.Ui","MysteryMachine.utils",
                 "MysteryMachine.policies" , "MysteryMachine.document"]

PY_MODULES  = [ 'pyparsing' ]

#Mercurial and pyaprsing (as of 1.5.2 ) don't install with easy_install. 
EZ_PACKAGES   = ["docutils" , 
#                 "mercurial" ,
                 "bpython" , 
#                 "pyparsing > 1.5" ,
                 "PyYaml"]


TESTSDIR = "tests"
FILES = [ "AUTHORS", "CodingGuidelines", "OriginalDesign" ,"README",
          "paver-minilib.zip" ]
DIRS  = ["docs" , "examples" ,"graphics", "scripts" ,"patches" , TESTSDIR]
SCRIPTS = [ 'setup.py' , 'ez_setup.py' ]

VENVSCRIPT = 'install.py'

PYTHONS= [ "python" ]

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


#
# Redefine minilib so that it includes the virtual module
# 
@task
def minilib(options):
    #paver seems to complain if this is already there..
    if 'extra_files' not in options:
        options['extra_files']= [ ]
    options['extra_files'] += ['virtual']
    paver.misctasks.minilib(options)


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
               except:
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
                   atexit.register(os.remove,os.path.join(filedir[0],*filedir[1:]))
               except:
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
    """Run MysteryMachine unit test on the default python"""
    path=os.getenv("PYTHONPATH")
    if path == None:
    	path = os.curdir 
    else:
    	path = path+os.pathsep+os.curdir
    
    os.putenv("PYTHONPATH",path)

    for python in PYTHONS:
	sys.stderr.write( "Testing under %s:\n" % python )
	#TODO: should this inner loop go inside tests/__init__.py ?
	for module in os.listdir('tests/'):
		#Turn filenmae into module name
		testname , replaced =re.subn(STRIP,"",module)
		# SKip invalid module names
		if not replaced: continue
		#run tests.
		sys.stderr.write("Running %s (%s)" % (module,python) )
		os.system("%s %s/%s" % ( python,  TESTSDIR, module))



def relaunch_self(extra_args):
    """Relaunches this process with additional arguments"""
    args = [ sys.executable ] + sys.argv + extra_args
    #Start again, 
    os.execv(sys.executable,args)

@task
#should install mercurial
def dst_environ(options):
    """Install MysteryMachine dependencies that setuptools can't handle without help"""
    #Check  whether we need pyparsing...
    try:
        import pyparsing
        v = pyparsing.__version__.split(".")
        for existing,minimum in zip(v,['1','5','0']):
            if existing < minimum: raise ImportError()
        #pyparsing exists in a usable version - don't override.
        options.setup.py_modules.remove('pyparsing') 
    except ImportError:
        #We need the shipping version of pyparsing with mysterymachine
        pass

    #TODO Install mercurial

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
        #Bpython doesn't work under windows to remove it from the
        # deps list
        if 'bpython' in  options.virtualenv.packages_to_install:
            options.virtualenv.packages_to_install.remove('bpython')
        if 'bpython' in options.setup.install_requires:
            options.setup.install_requires.remove('bpython')
      
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

@task
@needs('dst_environ')
def install_here():
    """Install everything from the build dir into t)he current env.
   
    This does the usual install thing installing all of the MysteryMachine
    packages and there dependencies into the current environment.

    If you wish to install MysteryMachine into your global environement
    this /might/ be want you want.    
    """
    call_task('setuptools.command.install')


@task
@needs('src_environ')
@cmdopts([('installdir=', 'd' ,'Directory to install MysteryMachine into')])
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
    paver =os.path.join(options.install.installdir,"bin","paver")
    try:
	    os.stat(paver)
    except (WindowsError,OSError):
	    paver = os.path.join(options.install.installdir,"scripts","paver")
    subprocess.call([paver,"-f",os.path.join(here,"pavement.py"),"install_here" ])


setup(name ="MysteryMachine",
      packages = DIST_PACKAGES ,
      scripts  = SCRIPTS ,
      py_modules =PY_MODULES,
      version  = "0.1.3pre", 
      install_requires = EZ_PACKAGES,
      url="http://trac.backslashat.org/MysteryMachine",
      author="Roger Gammans",
      author_email="rgammans@computer-surgery.co.uk",
      license = "GPLv2",
      entry_points={ 'console_scripts': [
                         "mysterymachine = MysteryMachine.Main:main",
                         "mmcli          = MysteryMachine.Ui.cli:main"
                   ]},
      package_data= paver.setuputils.find_package_data(".", package="paver",
                                            only_in_packages=False),
    )

options(
    virtualenv = Bunch(
        script_name = VENVSCRIPT, 
        packages_to_install = EZ_PACKAGES,
    )
)
