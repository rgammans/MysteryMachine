Object Model
============
MysyteryMachine's data handling is based on the `'prototype object model' <http://en.wikipedia.org/wiki/Prototype-based_programming>`_ , but we focus on computed data elements rather than active methods, more details are given below.

Objects are created in `Categories <Category>`_ , which from which the object
finds is starting prototype (or parent as it is called in MysteryMachine parlance).
This parent can be changed at any time though, and there is no requirement
for objects in a single category to all share a single root parent. In this
way `Categories <Category>`_ are just a grouping mechanism.

Categories can be defined by the users, and these are aligned
with the different types of documents the system will need to produce

  ie.
   1. Character Sheets
   2. Rule books
   3. Item Cards
   4. GM Plot Summary's 


Object Identity
---------------

The other primary use for the `<Category>`_ system is to provide a structure for naming the
objects in a consistent and unambiguous way. Each object will have designated an 
id , which is unique only within it's `<Category>`_.  So the full id for and object
includes it's Category, hence
a Object can be referred to as Plot:1 , or Character:10. The ':' Character is
used as the separator.


Object Structure
----------------
Each object is made up of a number of `<Attributes>`_. These `<Attributes>`_ can represent
a number of different things such as:-

   1. A paragraph for inclusion in a final document.
   2. A reference to another object.

The value of each attribute can include by reference the value of any other Attribute in the
system. So if you always refer to a character by its 'Name' attribute, you can rename it later in the development
of the game - safe in the knowledge that it should get rename automatically everywhere it is mentioned.

More complex use of attributes can bring together various information stored say in the Plot
category and add it into each characters background, keeping track of any custom modifications required
to keep the text reading smoothly. The text attribute type, allows macro replacement
of it's contents or parts of the content from other attributes.

Use  from which they inherit a default set of attributes and 
values. By convention an  `<Category>`_ named `<Templates>`_ stores the most
basic parents in a system, and these are normally set on a Category as it's default parent.

Objects can inherit from any other object in the system, but it Sensible prototypes  for each category simplify the repeated setup. For
instance my character objects normally have a 'fullname' attribute which is
a concatenation of 'firstname' 'lastname' attributes. This means I can use the fullname
and in places where I need it, but still access the firstname in prose element
where it is reads better.
Likewise if the games contains a large number of members of the same family which whare a 'familyname' attribute (and a maybe other characteristics ), I can create a specific
parent object for the family and then bind all the member to that family object. Then
when I change such details , it automatically flows into each character.

One-to-Many links in the MysteryMachine architecture are normally implemented via the
list attribute, combined with bidilink. If a uni-directional reference is required 
then the list is not normally needed (except for Many-Many) links. However in
my experience bidilinks make writing output documents much simpler. 
The downside to using bidilinks is that you need a join-object for Many-Many links however the join object becomes a useful place to store information relevant to that association.

The classic join Object I use in writing games is the PlotRole which links to a single Plot and a single Character, but creates a Many-Many link between characters and plots.
