File Formats
=============

Revision Control
----------------
Our undo, version control and merging behaviour will be provided internally by the use of the _mercurial: http://www.selenic.com/mercurial/wiki/
SCM. The mercurial system has a python API (python-hglib) which fits in well with the choice of python as the implementation language for MysteryMachine.

Mercurial supports case sensitive and preserving repositories even on filesystems which do not have this properties.

It will do be possible to 'Save' a work point without creating a mercurial changeset (eg. doing a commit), this will be handled transparently
by the system , except the fact the user will be prompted for a message when the 'save'.

Working format
--------------
The basic element of MysteryMachine is it `PluginArchitecture <Extensions>`_ which enables it to use many different file formats inside the revision control container.

However to start with I will only intend a single basic format options , although will try to ensure others such as XML can be added later.

To model the object nature of the database , the default store will use traditional filesystem abstractions which are support by most if not all modern operating systems,
eg, file and directories. No use of extended attributes or alternate data streams will be required.

Each attribute will live in it own file or files (on file per Value part see `<AttributeInternals>`_, the name of which reflects the attribute name (see `<NameSpace>`_) however the use of the '.' as a separator character will be used to indicate the internal handler for that attribute. It is possible though for an attribute to be composed of multiple files.

Attributes from the same object are stored in a directory which is unique to that object, and similarly each object is a directory which is unique to it's category.

Save format
-----------
On disk, a complete game will be stored in a .MMPack file, this will be the .hg/ directory and any other relevant mercurial
control files stored in a standard PKzip container with the deflate option.

As noted above the working format can be quite wasteful of disk space although this is a abundant resource in most machines toady we use a zip file to allow many copy of the game in development , to be stored efficiently. Technically thought further saving may be possible be the use of the mercurial hard linking between repositories, - it is harder to manage and even harder for untrusted users to follow while shouldn't cause problems has the potential for violating the principle of least surprise.

The .mmpack file will contain a '.format' file (making '.format' and invalid attribute name) which contains hints and version numbers etc, so the file can be successfully loaded.

