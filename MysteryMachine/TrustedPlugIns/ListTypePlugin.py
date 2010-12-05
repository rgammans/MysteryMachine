
"""
This plugin is design to import some of the Mysterymachine core. So elements
in the core which provide simliar interfaces to the extensions can be found
by using the extensions API and looking in the `Extension'.

This plugin imports the MysteryMachine.schema.MMListAttribute which 
provides the list attribute value type.

"""

from MysteryMachine.Extension import Extension

from yapsy.IPlugin import IPlugin

import logging

import MysteryMachine.schema.MMListAttribute

class ListTypePlugin(Extension):
    def activate(self):
        import MysteryMachine.schema.MMListAttribute

    def deactivated(self):
        pass
