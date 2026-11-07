User stories for the wx UI
==========================

The ``.feature`` files here are user stories for the wxPython UI, written
in Gherkin. They are kept as documentation of how the UI is meant to
behave, for when work on the UI resumes.

They are **not** run by the test suite. The step definitions (the ``.py``
files) were written for lettuce, which only runs on Python 2, and drive
the UI through dogtail. Many of the steps are unimplemented stubs.
``unittest discover`` doesn't look in this directory because it isn't a
package; don't add an ``__init__.py`` unless the steps have been ported.

To make the stories runnable again, port the steps to a maintained
Gherkin runner such as behave, which reads these ``.feature`` files
largely unchanged.
