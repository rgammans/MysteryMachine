Attribute Type System
=====================

This page documents a proposed (but likely) change to the way Attribute types are considered in MysteryMachine. This proposal puts forward a Formal Type system to which attributes can belong.

We have currently implemented or have plan to implement the the flowing types:-

#. Text
    Described as BasicText elsewhere . A piece of text ReST text including MM roles etc.

#. References.
    These can be used to refer to objects.

#. Document pieces.
    These allow a output document structure to be held in a object.

#. Lists.

   It is this last type (lists) which leave us with simple quandary. What type are the elements of the list.

   To keep thing as simple as possible for the AttributeInternals, we need to decide this in a simple way. If list can     
   store any attribute type internally then we immediately get into the the possibility of having an ever increasing 
   number of parts specifiers for the attribute (see `<AttributeInternals>`_ )

The simple way to solve this problem is not to support generic Container Attributes as Objects are our container system in the MysteryMachine architecture.

The original aim of List was to be able to give attributes an ordering relation in the Document objects. (This could be solved by using sort attribute order or similar here).

Another of List style attributes would be in special attributes which link Plot elements back to the Characters which included them. Again the attribute would provide a ordering relation and mechanism to refer to plot element from the character object. Although in the case the actuall data in the listAttribute is stored in other attributes elsewhere.

When we look at this two uses we can see that we the problem can solve itself, look at second use first we can see that what this use needs is not so much a container attribute but an 'indexable' attribute. The actual content of each index element is pulled from other attributes within the system.

The first use is also easy as it only store references.

So the current resolution is that MysteryMachine will support indexable attribute **but** not generic container attributes as they can be implemented with Objects.

