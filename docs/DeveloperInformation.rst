Information for Developers
==========================


Extension Mechanism
-------------------

This primary way of adding non-core features to MysteryMachine.

To add feature you can do this by writing one (or more)  `<Extensions>`_ .
Each `Extension <Extensions>`_ has a mm-plugin file which describes what Features are offered by the plugin,
and a python file which is imported if the plugin is loaded.

The MysteryMachine context will only load plugins which are trusted. A SHA hash of the plugins python
file is stored in the users configuration file and the MysteryMachine will only load plugins whose
hash is known.


Features are connected to 'Points' which describe the API exposed by the plugin, each plugin 
can lost a set of 'features' it exposes on each 'Point' .  Both a 'Point' and a feature , are 
simple textual names·

The plugin system is based on Yapsy, and The `mm-plugin <plugin_file>`_ file is a simple ini-file format file , the usual yapsy format. 

Extension Points
----------------

Currently there are four defined extension points. Each extension point is a comma separated list.

Attribute Types
'''''''''''''''

To implement a new `Attribute type <Attributes>`_  a plugin need to provide features
on two complementary points. As both the internal MysteryMachine type name for the
new Attribute type needs to be advertised, and also the typename of any python object
which should be auto converted to the appropriate type.

To define the MysteryMachine typename which will trigger loaded of the module 
list the on the 'AttributeValueMMType' point, and the python type names on the 'AttributeValuePyType' 
point.

Loading a plugin which advertises any names on these points should cause the plugin toregister it's 
types with `MysteryMachine.schema.MMAttributeValue.register_value_type <http://rgammans.bitbucket.org/MysteryMachine/schema/MMAttributeValue.m.html#MysteryMachine.schema.MMAttributeValue.register_value_type>`_ . After that they can be referenced by the core engine.

The register class should be a subclass of `MMAttributeValue <http://rgammans.bitbucket.org/MysteryMachine/schema/MMAttributeValue.m.html#MysteryMachine.schema.MMAttributeValue.MMAttributeValue>`_ .

Store Types
'''''''''''

The other extension point currently implemented is 'StoreScheme'. The features advertised
on this point should be the name of MysteryMachine store backends. Again a when the plugin is 
loaded in should register it's stores with the `MysteryMachine.store.RegisterStore <http://rgammans.bitbucket.org/MysteryMachine/store/index.html#MysteryMachine.store.RegisterStore>`_ function.

A store class should derive from or a least implement `MysteryMachine.store.Base <http://rgammans.bitbucket.org/MysteryMachine/store/Base.m.html>`_

Packfile helpers
''''''''''''''''

An extension point named 'PackFileDescriptor' also exists , this is to allow extension
to loaded with Packfile, and have directives which control the pack files. This is of
use mainly to Store extensions.

The implementation of this though is subject to change. Please refer the source for the
time being. And let me know if you use it. That way I can see how you need and I can
try to avoid breaking your extension with updates.


Future Points
'''''''''''''

The following places need extension points defined for threm in the core, but currently
lack and code for it.

    # Error handling. Some error will be able to resolved if it is known that the `System`_ follows certain conventions. By adding error handler's the aiding the users experience with an appropriate `Convention`_ module becomes possible.
    # `Policies`_
    # UI Menu entries. These entries allow actions like batch email sending. And insertion of complex MysteryMachine expansions, show in a way that doesn't force the user to learn more than necessary about the internal syntax of MysteryMachine.
    # UI Panel objects. Currently if you add a new type, there is No way to extend the wx UI to correctly allow editing of you new type. This will need and extension point as well.

Links to more resources
-----------------------

If you are bug fixing core features ,or need to no more about how the 
core is implemented these links should help.

There is now  autogenerated API documentation at on here at
`bitbucket <http://rgammans.bitbucket.org/MysteryMachine>` .

Please also See:-
 1. `<CodingGuidelines>`_.
 2. `<FileFormats>`_.



