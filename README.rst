Installation
============

Note / TLDR:

If you are installing from a source distribution, or a git checkout then the command:-

     pipx install .

should work.

Ipython (or bpython) is recommended for cli aficionados on  platforms which support them.


Windows Install Quick Reference
-------------------------------

(outdated - need checking, but this is for the old paver /python2 installation )
To install on windows I suggest the following commands, if you use python for
other applications want more control I suggest you read all of this README
before doing this

    1. Download a recent Python (2.6.x is recommended) from www.python.org and install it.
    2. Download a recent wxPython (2.8.10 is recommoned) from www.wxpython.org and install it.
    3. Download mercurial from  http://bitbucket.org/tortoisehg/thg-winbuild/downloads/ and install it. 
    4. From the MysteryMachine zip file run 
            python setup.py install -d c:\mysterymachine

    5 Add a Link to the mmcli.exe and mmwx.exe scripts to your Start Menu.


Installation on Debian/Unbuntu
------------------------------

    1. Run 'sudo apt install pipx'
    2. pipx install MysteryMachine


Libraries Required
------------------

You will need to install the following Python packages to use the 
MysteryMachine .

mercurial > 1.9.0
git
(Note, Pyparsing was included here but setup.py now handles that
dependency for you)


Mercurial
'''''''''
MysteryMachine no longer needs to be able to use Mercurial as a library,
but does require mercurial 1.9 or later for the cmd server feature.

However this be now be the standard version pyexe, or other binary version
of mercurial downloaded form the usual sources (ie. selenic.com) .


Git
'''
As an alternative to mercurial git is now available as a Version
manager option, via the gitpython library.

Bpython
'''''''
This package is no longer considerer required as it doesn't work on windows, 
however it is recommended on those platforms where it does work.

Use easy_install or your OS package manager
to install it. If it ia not already installed the installer will try to fetch and 
install it automatically.

MysteryMachine now supports Ipython, instead on other platforms.

Docutils
''''''''
MysteryMachine was first developed with docutils 0.4 but I'm currently using 0.6 myself
as it generates less noise of on the python comaptiblity tests. I suspect 0.5 and 0.6 should
work equally. 0.4 will probably work too but I haven't tested it in a while.

Docutils can either be installed with easy_install or the installer will pull in the
latest version for you.

PyYaml
''''''
Yaml is the current preferred format for the MysteryMachine config file , and if you
intend to start MysteryMachine with it default settings it will need PyYaml.
PyYaml can be install easily using easy_install. Like so:

    easy_install pyyaml

But it should pulled in with the installer.


Tkinter & Tcl/Tk
''''''''''''''''
These are only require for the Idle based Ui, but currently the installer doesn't
setup the tcl/tk environment correctly (see https://bitbucket.org/ianb/virtualenv/issue/40/tkinter-fails-in-a-virtual-env )
to fix this you need ensure the TCL_LIBARRY environmenr variable point to the TCL script
and srtart up files. The easiest way to do this is to add a line to your
activate.bat which set this varaibell to pint to the tcl directories tghat ship with
python.


Running MysteryMachine
======================

Running:-

    mmcli

will start the default MysteryMachine API cli for your platform.

Mystery machine has a two Cli ui's at the moment which dumps you at the
python shell with the global 'ctx' bound to MysteryMachine Library.

The are basically identical, the primary one is base on bpython and can
be started like this:

   mysterymachine --ui=Ui.cli.BPython

Bpython support auto completion and help pop-up documentation. The
down side of Bpython is that it requires a Unix (or unix-like) terminal
to run in, so is not compatible with windows.

For windows , althought it shoulkd work anywhere that has python there is
an alternative Ui based on the Idle development environment, this
Ui can be started like this:-

    mysterymachine --ui=Ui.cli.Idle

Similiarily this supports auto-completion and pop-up documentation but
where as Bpython will show the complete docstring, Idle tries to 
shorten it.


GUI
---

(temporary not wokring)
Your more likely to be interested in running the New MysteryMachine GUI 
and this can be starting by running the mmwx binary from either the bin
or scripts directory depending on your platform.


