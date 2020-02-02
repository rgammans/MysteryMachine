Attribute Internals
===================

This page documents the internal structure of the attribute handling. It aimed at giving created a concept of an AttributePart, which is stored by the underlying storage model, whatever that might be.

Attributes objects, are bound to AttributeValues, the distinctoin between the 
two is pretty subtle, an Attribute is a node with a system schema. Attribute
nodes are normally connected to Objects but there a few system attributes
supported on Categories and at the System level. AttributeValues however are
the values which they contain - Attributes when inherited are not shared but the
the AttributeValues are.

Attribute values consists of (optionally) multiple parts. Each part has a valid name
which is a valid path elements in the MysteryMachine `<Namespace>`_ .

Each part contains a sequence of bytes, it is the job of the AttributeValue
subclass to provide the parts to the store engine, and to manage the Attributes
visibility to the user API.
