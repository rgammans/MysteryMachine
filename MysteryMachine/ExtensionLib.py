#!/usr/bin/env python
#   			ExtensionLib.py - Copyright Roger Gammans
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
# This file was generated on Mon Feb 2 2009 at 20:18:08
# The original location of this file is /home/roger/sources/MysteryMachine/generated/ExtensionLib.py
#
#

import Extension
from ExtensionInfo import ExtensionInfo 
from TrustedPluginManager import *
from MysteryMachine import *
from MysteryMachine.VersionNr import VersionNr

class ExtensionLib(object):
    """
   This is a singleton class which handles MysteryMachines extention engine.
   It supports the concept of trusted and untrusted extensions, untrusted
   extensions cannot be used at runtime.
   The set of available extensions and the set of trusted extensions are completely
   distinct.  Meta data can only be enumurated fro available extensions.

    :version:
    :author:
    """

    """ ATTRIBUTES


    known_extensions  (private)
    trusted_extensions  (private)
    plugin_man  (private)

    """
    def __init__(self,cfg):
        if not 'extensions' in cfg:
            cfg['extensions'] = {'path':[] , 'trusted': [] }
        self.plugin_man =TrustedPluginManager.TrustedPluginManager(
                      directories_list=cfg['extensions']['path'],
                      plugin_info_ext="mm-plugin",  
         			  categories_filter={"Default":Extension.Extension}, 
                      trustList=  cfg['extensions']['trusted']
                     )

        self.plugin_man.locatePlugins()
    #    self.known_extentions = cfg['extensions']['known']
        self.helpers=dict()
        self.mixins=dict()

    def register_helper(self,cls,helper_factory):
        """
        DEPRECATED
        
        Registers a factory callable which returns helper instances
        to be used by class cls. How cls uses helpers is up to
        it.

        Helpers are distinguished from mixin's primarily by being
        called volunterlly by there assoicated class ,and by each 
        instance of the helped class haveing it's own helper instances.
        """
        if cls in self.helpers:
           if not helper_factory in self.helpers[cls]:
                self.helpers[cls] += helper_factory
        else:
           self.helpers[cls] = [ helper_factory ]


    def unregister_helper(self,cls,helper_factory):
        """
        DEPRECATED
        Removes a hlper from the registration database.
        """
        self.helpers[cls].remove(helper_factory) 

    def get_helpers_for(self, className):
        """
        DEPRECATED

         Returns helpers for className

        @param string className : className to search for mixins for
        @return Extension :
        """
        if className in self.helpers:
            return self.helpers[className] 
        else:
            return () 

    def IsTrusted(self, extension):
        """
        Determines wheter an extension is trusted. 

        @param Extension extension : 
        @return  : true - if the extension is trusted
        """
        return self.plugin_man.isPluginOk(extension)

    def SetTrust(self, ext, trusted):
        """
        Sets wether an extension is trusted or not.     

        @param Extension ext : 
        @param bool trusted : 
        """
        if trusted:
            self.plugin_man.trustPlugin(ext)
        else:
            self.plugin_man.untrustPlugin(ext)

    def getExtension(self, name, category = "Default", version = None):
        """
        Returns extensionInfo for extension named name if and only if extension is trusted.


        @param string name :   Name of extension to return 
        @param string category:Category if extension
        @param string version: Reserved for later use. Must be None.
        @return Extension :
        """
        return self.plugin_man.getPluginByName(name, category)


    def get_extension_list(self):
        """
        Generates the list of extension names known about.
        """
        #Do trusted plugins
        for plugin in self.plugin_man.getPluginCandidates():
             yield plugin
        
        # Return rejected plugins.
        for plugin in self.plugin_man.getRejectedPluginInfo():
            yield plugin
    
        #Return loaded plugins.
        for plugin in self.plugin_man.getPluginsLoaded():
            yield plugin

    def findPluginByFeature(self,extension_point,featurecode, version = None ):
        """
        Finds the plugin which provides feature code 'featurecode'
        in extension point 'extension_point'.
        """

        for plugin in self.plugin_man.getPluginCandidates():
            if plugin.provides(extension_point,featurecode):
                if VersionNr(None) and  VersionNr(version) <= VersionNr(plugin.version)  : yield plugin

    def loadPlugin(self,plugin):
        self.plugin_man.loadPlugin(plugin)
