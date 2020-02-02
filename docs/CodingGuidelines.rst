=================
Coding Guidelines
=================

Python Version 
==============

The initial release of MysteryMachine is intended to run with the python2.6
interpreter however it is required that any code run under both python2.5
and the '-3' switch in python 2.6 to ensure support for python 3 when pour
libraries support it.

The unit testing framework will do these tests for you if you write useful unit
tests for your code.

Rationale
---------
Sooner or later we are going to have to support python 3.0 as the libraries
we use move over to python3.0. Critically however many linux distributions
seem to have only got python2.5 in them at this stage. So we are
stuck with ensure we support at least 2.5, and 2.6 . But we need to look forward
to ensure that the code we write isn't going to cause a massive maintenance
burden in the future, when python 3 become standard. Hence we must test with python2.6 -3.

Unit Tests
==========
Each class should have unit tests written for it when it is developed, and such tests
must be developed before the initial commit into the main source tree.
Each commit mush ensure that it passes the unit tests in the main tree. However since
we are using mercurial I expect a number of trees to spring up with more relaxed
policies, so that this unit test requirement does not hamper development speed.
