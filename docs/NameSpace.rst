Namespace
=========

Restrictions
------------
Names are case insensitive. and must not contain or " ", "/", "\", ":", ";", "|", ",",
"*", "[", "]", '"' , "`", "=" . 

Additionally names starting with a "." are reserved for the core system and schema's use, no other
character position can contain '.' .  

If a store engine needs to store named data in its' backend
it should use names starting with '..' as these are guaranteed to not clash with anything that comes from a higher level.

Additionally it the '.' character is available for the store engine to use as a separator when concatenating elements that define and data elements  internal name.

Additionally ":" is reserved as our 'path' separator character, so that an attribute can be referenced from store:object:attr.

Store names themselves are built up from and escaped version of our Uri format. 

Empty names are not allowed.

Unicode names are strongly discouraged although not actually banned at this point it time, I suspect that they won't work for a while and will require python 3. Also  they are unnecessary for user experience as each object can have a user friendly name - defined by the .defname attribute, this attribute is supported at the `Object <Objects>`_, `<Category>`_ and `<System>`_ levels.

Rationale
---------
 
  1. '.' - Used internally to defined meta type of category or attribute.
  2. ' ' - Would add a lot of complexity to the substitution language , this allows us to guarantee that all object names contain no embedded whitespace. Which in most cases should allow us to have better error recovery.
  3. Empty attribute names would clash with our internal usage rules. 
  4. Case insensitive to allow use of attribute names as file name on case-insensitive systems. 
  5. The list of banned a characters is drawn from a list of banned characters in the windows, linux and macos filenames.


Internal Names
--------------
`<Attributes>`_  support the use of subsidiary name parts, which allow MysteryMachine application framework to find and determine the correct storage model or type handler as appropriate. Additionally other meta-data within the MysteryMachine architecture is handled in this way.

The use of '.' as a separator character should be consider the standard way of composing an attribute  and /or attribute part name. Since '.' is banned a a character in all positions except the first (see below).
 
The schema and MysteryMachine core may use name with a leading '.' , additionally names beginning '..' are reserved for the storage backend.

URI
---

Individual MysteryMachine Systems are identified by their 'URI' the Uri consist of a scheme name follow by scheme dependent string. There are now restrictions of these scheme dependent string.
