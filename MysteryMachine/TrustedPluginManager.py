#!/usr/bin/env python
#   			TrustedPluginManager.py - Copyright roger
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

from yapsy.FilteredPluginManager import *
from ExtensionInfo import *

class TrustedPluginManager (FilteredPluginManager):

  """
  Manage the trust policies for Mystery Machine plugins.

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
        return data[plugin_info.name]==plugin_info.getSecureID()

  def trustPlugin(self, plugin):
    """
     Add a plugin to the trustList and update the PluginManager

    @param ExtensionInfo plugin : 
    @return  :
    @author
    """
    self.trustlist[0][plugin.name]=plugin.secureID
    self.collectPlugins()    

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

    if plugin.is_activated:
       plugin.deactivate()
     
    #Update internal lists.
    self.collectPlugins()
     
    for data in self.trustlist:
       if data.contains(plugin.name):
         del data[plugin.name]



