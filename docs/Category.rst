========
Category
========

Concept
=======

Broadly speaking the concept of category within the MysteryMachine system can be thought of as aligned with the concept `class <http://en.wikipedia.org/wiki/Class_(computer_science)>`_ in a traditional OO programming languages. However this is misleading as MysteryMachine uses a classless, or `prototype
object model <http://en.wikipedia.org/wiki/Prototype-based_programming>`_. See more here `<ObjectModel>`_

In fact category only a arbitrary grouping of objects which being help together make sense for your the purposes of your final document, and our group queries. For instance there is little reason to keep NPCs and PCs together in the same category. The document output and node query syntax supports selecting all objects in a category efficiently.

Instead you can keep them in separate categories so you don't waste paper produce player style packs for NPCs roles, and the object model will still allow you to share common rules and basic attributes between PC & NPCs by using the same parent object.

Names
=====

Category names, will be restricted by the same rules as attributes, see `<NameSpace>`_

Management
==========
Within each category the system needs to create each object a unique id. Currently this is a monotonically increasing numeric Id, however we might want to change this as we have a distributed model. Having said that the use of Hg would allows clash detection trivially and it not difficult to automatically resolve this conflict - but that would require special handling , however an alternate scheme may not need any such additional support code. 

The downside of this would likely to be less human memorable Id's, so it may depend on the level of macro insert support we add to the user interface.

This is still an open issue but may be managed through `<Policies>`_ .
