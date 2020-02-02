Extensions
==========

The MysteryMachine application will support Plugin' and extensions. These are effectively the same.

The Application will search, a system extension path, and per-use extension path and a document extension path. 

Before any extension code is executed though the extension will have to be marked as 'trusted' by the current user. A cryptographic hash is currently used to identify trusted extensions.

These extensions will be able to add all any generic functionality to the system, of particular interest are new attribute types, alternative storage models (as the initial one has some known weaknesses) extra User interface 'views'.

The default storage engines are provided by the defaut MMCore Plugin and the 
Bidi and List attribute types are also use plugins to register them with the 
system.

Extensions consist of at least two files, a `mm-plugin <plugin-file>`_ 
description file, and one or more python modules.
