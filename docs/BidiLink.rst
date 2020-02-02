Bi-direction (Bidi) Links
=========================

bidilinks are a special attribute value types in the MysteryMachine architecture.

Each attribute is in a connected, on unconnected state, if it is connected it should
be pointing at an attribute which is pointing back. With one proviso, although the
attributes actually track their partner attribute any attempt to dereference, or
follow the link leads you to a ancestor of the attribute (normally it's containing object)
in the  `<System>`_ schema. An unconnected bidilink is also known as an `<Anchor>` .

Each link is made up of two attributes any attempt to change or move one end will
normally result in the existed reference end becoming an anchor.

Anchors, keep track of which of there ancestors any reference should resolve too.
