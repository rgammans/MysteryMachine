"""
This plugin is design to import some of the Mysterymachine core. So elements
in the core which provide simliar interfaces to the extensions can be found
by using the extensions API andlooking in the `Extension'.
"""

from MysteryMachine.Extension import Extension

from yapsy.IPlugin import IPlugin
import MysteryMachine.store.file_store
import MysteryMachine.store.dict_store
import MysteryMachine.store.hgfile_class
import MysteryMachine.Packfile
import MysteryMachine.Extension

import logging

_storeClasses =  { 'hg_store'   : MysteryMachine.store.hgfile_store.HgStoreMixin,
                   'file_store' : MysteryMachine.store.file_store.filestore }

class Core(Extension):
    def __init__(self):
        global _storeClasses
        super(Core,self).__init__()
        self.logger = logging.getLogger("MysteryMachine.Extensions.Core")
        #Bring globals into our namespace - to ensure they have a ref.
        self._storeClasses = _storeClasses
        self.logger.debug( "MMCore-Init:%s" %self)

    def activate(self):
        pass

    def deactivated(self):
        pass

    def getInterfaces(self):
        return ["storeclass"]

    def getMixinTargets(self):
        return [] 

    def getStoreMixin(self,classname,version):
        return self._storeClasses[classname]

    @staticmethod
    def PackFileDescriptorCmd_Store(line,flags):
        """Call out to Core routine"""
        MysteryMachine.Packfile.GetStoreBases(line,flags)
