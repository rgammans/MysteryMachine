"""
This plugin is design to import some of the Mysterymachine core. So elements
in the core which provide simliar interfaces to the extensions can be found
by using the extensions API andlooking in the `Extension'.

This plugin import the MMDLinkvalue module, which provides the the bdidilink
value type.
"""

from MysteryMachine.Extension import Extension


import logging

import MysteryMachine.schema.MMDLinkValue

class BidiTypePlugin(Extension):
    def activate(self):
        pass
    def deactivate(self):
        pass
