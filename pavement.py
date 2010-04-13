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



DIST_PACKAGES = ["yapsy" , "MysteryMachine","MysteryMachine.schema",
                 "MysteryMachine.store","MysteryMachine.parsetools",
                 "MysteryMachine.Ui","MysteryMachine.utils",
                 "MysteryMachine.policies" , "MysteryMachine.document"]

EZ_PACKAGES   = ["docutils" , "mercurial" , "bpython" , "pyparsing > 1.5" ]

TESTSDIR = "tests"
FILES = [ "AUTHORS", "CodingGuidelines", "OriginalDesign" ,"README",
          "paver-minilib.zip" ]
DIRS  = ["docs" , "examples" ,"graphics", "scripts" ,"patches" , TESTSDIR]
SCRIPTS = [ 'scripts/mysterymachine', 'setup.py' ]

VENVSCRIPT = 'install.py'

PYTHONS= [ "python" ]

import sys
import os

from paver.easy import *
from paver.setuputils import setup
import paver.virtual

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
# Redefine minilib so that it include the virtual module
# 
@task
def minilib(options):
    if 'extra_files' not in options:
        options['extra_files']= [ ]
    options['extra_files'] += ['virtual']
    paver.misctasks.minilib(options)


@task
@needs('generate_setup','minilib')
def sdist():
    """Create a source distribution (tarball, zip file, etc.)"""
    global SCRIPTS

    pkgs = {}
    path = sys.path
    path.insert(0,".")
    for pkg in DIST_PACKAGES:
        pkgdir = pkg.split(".")
        for dir in sys.path:
            if os.path.isdir(os.path.join(dir,*pkgdir)):
               try:
                   #Put all our need packages in the local directory.
                   os.symlink(os.path.join(dir,*pkgdir),os.path.join(pkgdir[0],*pkgdir[1:]))
               except:
                   pass

    #Create find data files scripts etc needed for sdist.    
    for dir in DIRS:
         for file in find_all(dir,dir):
            SCRIPTS += [ file ]

    SCRIPTS += FILES
    SCRIPTS += VENVSCRIPT 

    paver.virtual.bootstrap() 
    call_task("setuptools.command.sdist")

import re
STRIP   = re.compile('\.py$')
@task
def test():
    """Run MysteryMachine unit test on the default python"""
    path=os.getenv("PYTHONPATH")
    if path == None:
    	path = "."
    else:
    	#FIXME: Needs to be ';' under windows
    	path = path+":."
    
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


@task
@needs('setuptools.command.install')
def install_here():
    """Install everything from the build dir into the current env.
   
    This does the usual install thing installing all of the MysteryMachine
    packages and there dependencies into the current environment.

    If you wish to install MysteryMachine into your global environement
    this /might/ be want you want.    
    """
    #Dummy script for rename effect setuptools should do everything required.
    pass


@task
@needs('paver.virtual.bootstrap')
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
    here = os.getcwd()
    try:
        os.mkdir(options.install.installdir)
    except OSError, e:
        if e.errno != 17: raise e

    os.chdir(options.install.installdir)
    #call Pre built install file , creates virtual environment etc..
    os.system(sys.executable + " " + os.path.join(here,"install.py"))
    os.chdir(here)
    #Relaunch paver to install ourself into the newly setup virtualenv.
    os.system(os.path.join(options.install.installdir,"bin","paver")+ " -f "+
              os.path.join(here,"pavement.py")+" install_here")


setup(name ="MysteryMachine",
      packages = DIST_PACKAGES,
      scripts  = SCRIPTS,
      version  = "0.1.0",
      install_requires = EZ_PACKAGES,
      url="http://trac.backslashat.org/MysteryMachine",
      author="Roger Gammans",
      author_email="rgammans@computer-surgery.co.uk",
      license = "GPLv2",
      package_data= paver.setuputils.find_package_data(".", package="paver",
                                            only_in_packages=False),
    )

options(
    virtualenv = Bunch(
        script_name = VENVSCRIPT, 
        packages_to_install = EZ_PACKAGES,
#       Removed as there is no practical way to 
#       predetermie a path back to this pavement file
#        paver_command_line  = " install_here",
    )
)
