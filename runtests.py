#!/usr/bin/python

# First cut of a routine to run our unittests for the
# MysteryMachine Project


#   			runtests.sh - Copyright Roger Gammans
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
import os
import imp
import sys
import re

PYTHONS  =( 'python2.5', 'python2.6', 'python2.6 -3')
UNITTEST ='/usr/lib/python2.6/unittest.py'
TESTSDIR ='tests'

STRIP   = re.compile('\.py$')

sys.path.insert(0,"./%s" % TESTSDIR )

path=os.getenv("MMPYPATH")
if path == None:
	path = os.path.realpath(os.curdir)
else:
	path = os.path.pathsep + os.path.realpath(os.curdir) + path

os.putenv("PYTHONPATH",path)

def NoTests():
	return( )

#Allow the ability to run tests under a single python.
if len(sys.argv) > 1:
    DEFPYTHONS=PYTHONS
    PYTHONS = []
    
    for arg in sys.argv[1:]:
        print arg
        PYTHONS += [ 'python%s' % arg ]

for python in (PYTHONS):
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

os.chdir("tests")
os.system("lettuce")

sys.stderr.write("\n")
sys.stdout.write("\n")
