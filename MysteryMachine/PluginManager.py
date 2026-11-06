#!/usr/bin/env python
#               PluginManager.py - Copyright Roger Gammans
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
"""
MysteryMachine's plugin loader.

A plugin is a single python module described by an INI format
`.mm-plugin` file in the same directory (see docs/plugin_file.rst).

PluginManager finds the plugin descriptions in a list of directories, and
imports and instantiates a plugin's Extension subclass when asked to load
it. Every plugin a PluginManager finds is trusted; it is used for the
system plugins which ship with MysteryMachine.

TrustedPluginManager only offers plugins whose source matches a secure hash
in its trust list. Everything else is held as rejected, and can't be loaded,
until it is trusted.
"""

import importlib.util
import itertools
import logging
import os
import re
import sys

from .Extension import Extension
from .ExtensionInfo import ExtensionInfo

logger = logging.getLogger(__name__)

PLUGIN_INFO_EXT = "mm-plugin"


class PluginLoadError(ImportError):
    pass


class PluginManager(object):
    """
    Locates and loads plugins. Every plugin found is trusted.
    """
    _module_ids = itertools.count()

    def __init__(self, directories, plugin_info_ext=PLUGIN_INFO_EXT):
        if isinstance(directories, str):
            directories = [directories]
        self.directories = list(directories or [])
        self.plugin_info_ext = plugin_info_ext
        self._candidates = []
        self._rejected = []
        self._loaded = []

    def is_trusted(self, info):
        return True

    def locate(self):
        """Scan the plugin directories, replacing any previous results."""
        self._candidates = []
        self._rejected = []
        for info in self._scan():
            if self.is_trusted(info):
                self._candidates.append(info)
            else:
                self._rejected.append(info)

    def _scan(self):
        suffix = "." + self.plugin_info_ext
        for directory in self.directories:
            for dirpath, dirnames, filenames in os.walk(directory):
                #Sort so the plugin order doesn't depend on the filesystem.
                dirnames.sort()
                for filename in sorted(filenames):
                    if not filename.endswith(suffix): continue
                    infofile = os.path.join(dirpath, filename)
                    try:
                        yield ExtensionInfo.from_file(infofile)
                    except Exception:
                        logger.error("Ignoring invalid plugin description %s",
                                     infofile, exc_info=True)

    def candidates(self):
        """Plugins which may be loaded."""
        return list(self._candidates)

    def rejected(self):
        """Plugins which were found, but may not be loaded."""
        return list(self._rejected)

    def loaded(self):
        return list(self._loaded)

    def get_by_name(self, name):
        """Return the loaded plugin called name, or None."""
        for info in self._loaded:
            if info.name == name:
                return info
        return None

    def load(self, info):
        """Import plugin info and instantiate its Extension.

        A no-op if it is already loaded. Only candidates may be loaded.
        """
        if info.isLoaded(): return
        if info not in self._candidates:
            raise PluginLoadError("Plugin %s is not trusted" % info.name)

        module = self._import(info)
        classes = [ obj for obj in vars(module).values()
                    if isinstance(obj, type) and issubclass(obj, Extension)
                       and obj.__module__ == module.__name__ ]
        if len(classes) != 1:
            raise PluginLoadError("Plugin %s must define exactly one Extension"
                                  " subclass, found %d" % (info.name, len(classes)))
        info.plugin_object = classes[0]()
        self._loaded.append(info)

    def _import(self, info):
        #Plugins in different directories may share a module name, so
        # give each one a name of its own.
        modname = "_mm_plugin_%s_%d" % (re.sub(r"\W", "_", info.name),
                                        next(self._module_ids))
        spec = importlib.util.spec_from_file_location(modname, info.path + ".py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[modname] = module
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            del sys.modules[modname]
            raise PluginLoadError("Unable to import plugin %s: %s" % (info.name, e)) from e
        return module


class TrustedPluginManager(PluginManager):
    """
    A PluginManager which only offers plugins whose secure id is in its
    trust list.

    trust_list is a list of mappings from plugin name to secure id (either
    an ExtensionSecureID or its string form). trust() records new trust in
    the first mapping.
    """
    def __init__(self, directories, trust_list, plugin_info_ext=PLUGIN_INFO_EXT):
        super(TrustedPluginManager, self).__init__(directories, plugin_info_ext)
        self.trust_list = trust_list

    def is_trusted(self, info):
        for trusted in self.trust_list:
            if info.name in trusted:
                return info.getSecureID() == trusted[info.name]
        return False

    def trust(self, info):
        """Add plugin info to the trust list, so it may be loaded."""
        self.trust_list[0][info.name] = str(info.getSecureID())
        if info in self._rejected:
            self._rejected.remove(info)
            self._candidates.append(info)

    def untrust(self, info):
        """Remove plugin info from the trust list.

        The plugin is deactivated and will no longer be offered, but code
        it has already run can't be unloaded; to be sure all of its effects
        have gone the application must be restarted.
        """
        if info.is_activated:
            info.deactivate()
        for trusted in self.trust_list:
            if info.name in trusted:
                del trusted[info.name]
        if info in self._loaded:
            self._loaded.remove(info)
        if info in self._candidates:
            self._candidates.remove(info)
            self._rejected.append(info)
