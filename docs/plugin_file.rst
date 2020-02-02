Plugin Description file
=======================

The plugin system is based on Yapsy, and The mm-plugin file is a simple ini-file format file , the the usual yapsy format, described fully here for completeness.

As it is an INI-file it is broken into sections.


Core
----
The mandatory core section defines the name and the python module, hence this must contain a 'Name', and a 'Module entry.

The 'Name', should be a unique name for your plugin, and the moduel
should be the python module or package to import.

Eg, If your python file is X.py, you would normally import with
'import X'. So your plugin file should contain 'module = X'.


Documentation
-------------
Can contain  'Author', 'Version', 'Website' and 'Description' entries.

There are what are available (and source) when prompting the user for
the modules trust status.

The extension system tries to find the latest version of the module
and import that if it is trusted. The any two modules with the 
same name and version are considered identical. 

NB. We should audit how that equivalence interacts with trust.


ExtensionPoints
---------------

The section contains a list ofr what the plugin adds to 
MysteryMachine. Each line is an ExtensionPoint name followed by
a comma separated list of features provided by the module
on that extension point. See `DeveloperInformation`_ for more
details.
