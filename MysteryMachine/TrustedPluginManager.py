#!/usr/bin/env python
#               TrustedPluginManager.py - Copyright roger
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
# This file was generated on Mon Feb 2 2009 at 22:51:50
# The original location of this file is /home/roger/sources/MysteryMachine/generated/TrustedPluginManager.py
#
#
"""
This module is a bit of a mis-nomer as this is the Plugin manager, which
mananges plugins which may not be Trusted.

It also manages the trust for it's plugins and works with the config
engine to store those decisions in a persistent manner.

So the is the TrustedPluginManger as it Manages plugins and their
trust, and can distinguish between them. (cf. CorePluginManager)

"""
from yapsy.FilteredPluginManager import *
from . import CorePluginManager as cpm
from .ExtensionInfo import *
import collections.abc

class TrustedPluginManager (cpm.YapsyHelpers,FilteredPluginManager):

  """
  Manage the trust policies , and the loading of plugins
  only plugins which are marked as trusted.

  :version:
  :author:
  """

  """ ATTRIBUTES


  trustList  (private)

  """
    
  def __init__(self, 
        decorated_manager=None,
        categories_filter={"Default":IPlugin}, 
        directories_list=None, 
        plugin_info_ext="mm-plugin",
        trustList=None):
        """
        Create the plugin manager and record the trustlists 
        that will be used afterwards.
        
        """
        # Create the base decorator class
        if not isinstance(directories_list,collections.abc.Sequence):
            directories_list = [ directories_list ] 

        FilteredPluginManager.__init__(self,decorated_manager,
                                        categories_filter,
                                        directories_list,
                                        plugin_info_ext)
        
        self.setPluginInfoClass(ExtensionInfo)
        self.trustlist=trustList

  def isPluginOk(self,  plugin_info ):
    """
     Determine whether a plugin is trusted by looking for it's secureId in the
     trustList

    @param ExtensionInfo plugin : 
    @return bool :
    @author
    """
    for data in self.trustlist:
      if plugin_info.name in data:
        secureid=data[plugin_info.name]
        if type(secureid) != ExtensionSecureID:
            #Create secure Id from alternative representation
            secureid=ExtensionSecureID(plugin_info.path,secureid)
        return plugin_info.getSecureID() == data[plugin_info.name]
    return False

  def trustPlugin(self, plugin):
    """
     Add a plugin to the trustList and update the PluginManager

    @param ExtensionInfo plugin : 
    @return  :
    @author
    """
    self.trustlist[0][plugin.name]=str(plugin.secureID)
    for pluginTuple in self.getRejectedPlugins():
        if pluginTuple[2] is plugin:
            self.unrejectPluginCandidate(pluginTuple)
    #self.collectPlugins() 

  def untrustPlugin(self, plugin):
    """
     remove a plugin from the trust list - deactivate if necessary.
     This update the plugin manager - but cannot ensure all effect of an untrusted
     plugin are reversed to be sure of this you must restart the whole application.
     Well behaved plugins will do their best on deactivate

    @param ExtensionInfo plugin : 
    @return  :
    @author
    """
    if plugin.plugin_object and plugin.is_activated:
       plugin.deactivate()
     
    for data in self.trustlist:
       if plugin.name in data:
         del data[plugin.name]

    #Update internal lists.
    for pluginTuple in self.getPluginCandidates():
        if pluginTuple[2] is plugin:
            self.rejectPluginCandidate(pluginTuple)
    #self.collectPlugins()

  def getRejectedPluginInfo(self):
    for p in self.getRejectedPlugins():
        yield p[2]


