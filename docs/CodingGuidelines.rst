=================
Coding Guidelines
=================

Python Version 
==============

MysteryMachine supports every CPython release which hasn't reached its end
of life (see https://devguide.python.org/versions/). Currently that is
Python 3.11 to 3.15.

The supported versions are listed in three places, which must be kept in
step: requires-python and the classifiers in pyproject.toml, the envlist in
tox.ini, and the test matrix in .github/workflows/pythonapp.yml. When a
version reaches end of life, drop it from all three, and raise
requires-python; when a new version is released, add it.

CI also runs the test suite on the next Python prerelease, allowed to fail,
to give early warning of breakage.

Python 2 is not supported, so don't use six or other Python 2 compatibility
idioms in new code.

The unit testing framework will check your code on each supported version
if you write useful unit tests for it; run them locally with tox.

Unit Tests
==========
Each class should have unit tests written for it when it is developed, and such tests
must be developed before the initial commit into the main source tree.
Each commit mush ensure that it passes the unit tests in the main tree. However since
we are using mercurial I expect a number of trees to spring up with more relaxed
policies, so that this unit test requirement does not hamper development speed.
