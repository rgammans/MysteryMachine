==============================
Welcome to the Mystery Machine
==============================


Synopsis
========

The mystery machine is an application for writing freeform games.

In particular in is a database ,targeted at building highly intricate and linked
documents. These documents are expected to be in a natural language . The system
has to merge paragraphs from different sources. This paragraphs can contain
embedded references and conditionals based on other parts of the system.

Each `<System>`_ (eg, complete game or other project) developed in Mystery Machine
is created from a collection of `<Objects>`_ .

See `<ObjectModel>`_ for more information.

Current Status
==============

Mystery Machine is currently in alpha. Basic code exist to support the data schema and to create docutils doctrees from which final documents can be output using the standard docutils api.

The plugin system is currently flawed due to problem with Yapsy on which it is based. This is the next big milestone to replace.

Although MysteryMachine support Plugable api's (or main()'s ) , currently the only exuant API is a bpython shell which provide you with direct access the the MysteryMachine API Calls.

Downloads
=========

I maintain a mercurial repository for the soruce,  issue tracker and wiki for the documentation at bitbucket·
   #.  `http://bitbucket.org/rgammans/mystery-machine/ <http://bitbucket.org/rgammans/mystery-machine/>`_

Developer Page
==============

`<DeveloperInformation>`_
