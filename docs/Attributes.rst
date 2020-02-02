Attributes
==========

If `<Objects>`_ are the core of the MysteryMachine scheme , then attributes are the workhorse. Attributes contain all the text and data which pulls a MysteryMachine `<System>`_ together.

Attributes have an informal type system ( this may change -see `<TypeSystem>`_) and a structure all to themselves inside MysteryMachine.

For the most part attributes are the basic containers of the text which is used to create the documents which MysteryMachine generates, attributes
are also the atomic unit of data reference in the system. Attributes are substituted into different contexts by the use of links..

Currently I have these different attribute types.
   1) List.
        Uniquely in the system , the list attribute type can itself contain
        multiple attributes, but it can only contain attributes which themselves
        are singe part attributes. List are not single part attributes, so lists 
        of lists are not possible. But lists, of basictest,references, and bidilinks
        are.
   2) Reference.
       A reference attribute is a reference to one of the other `<Objects>`_ in the system. Reference paths can be used to encode simple lookups common to an object 
(such as appropriate pronouns) on ann object be object basis.
   3) BasicText.
       This type is formatted text, including substitutions of text from other attributes.
   4) `<BidiLinks>`_
      `<BidiLinks>`_ are an important attribute type a MysteryMachine system , together
      with the list type, these form the basis of relationships between objects. While references could be used for this , most object relationships benefit from being traversed
from either end. Uniquely in the the MysteryMachine a bidilink consists of two attributes, one for either end. An unconnected BidiLink is known as an `<Anchor>`_ .
The internal system goes to some efforts to keep the two Attributes synchronised.

   5) `<ExtendedText>`_. (Not currently implemented)
       This extension of basic text , is the same as the above but includes a set of changes made to the final substituted text of the attribute
 
This final type has the unique property that it can be made Invalid, that is the attribute is made to fail `<Validation>`_ by an edit of another attribute belonging to a the same or a different object.
This although perhaps counter intuitive to the user, allows editing of data in the `<System>`_ to which may be included in multiple places in different forms (say via ExtendedText Attributes).  MysteryMachine will be able to either apply the changes correctly, or flag up the problem (`<Validation>`_ failure) for the user to manually correct

(Developers see `<AttributeInternals>`_ )
