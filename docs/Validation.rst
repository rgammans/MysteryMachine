Validation
==========

MysteryMachine support the concept of Validation - that is it is possible to have an 'invalid' `<System>`_.

A `<System>`_ is invalid if any of the `<Attributes>`_ within the system fail validation.

Reasons for Validation to fail include but are not limited to:-
   1) Attribute contains a reference to a non-existent object.
   2) Attribute (normally an extended attribute) cannot to resolved to text because a it involves a modification to text from a different attribute which has changed in a way that cannot be handled automatically.

Much of the Validation support is currently unimplemented , but since it's most important
use is with the ExtendedText Attributes which are also unimplemented, this is consistent (ish)

A system cannot be saved or `committed <Commit>`_ unless it first validates.

