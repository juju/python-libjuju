Change Log
----------

0.3.0
^^^^^
Mon Feb 27 2017

* Fix docstrings for placement directives.
* Implement Model.add_machine()
* Bug fix - "to" parameter to Model.deploy() was broken
* Add docs and examples for adding machines and containers and deploying
  charms to them.
* Make Machine.destroy() block the current coroutine, returning only after
  the machine is actually removed from the remote model. This is more
  consistent with the way the other apis work (e.g. Model.deploy(),
  Application.add_unit(), etc).
* Raise NotImplementedError in all unimplemented method stubs instead of
  silently passing.

0.2.0
^^^^^
Thu Feb 16 2017

* Add default ssh key to newly created model.
* Add loop helpers and simplify examples/deploy.py
* Add support for deploying local charms, and bundles containing local charm paths.
* Add ability to get cloud name for controller.
* Bug fix - fix wrong api used in Model.destroy_unit()
* Add error detection in bundle deploy.

0.1.2
^^^^^
Thu Dec 22 2016

* Bug fix - Include docs in package

0.1.1
^^^^^
Thu Dec 22 2016

* Bug fix - Include VERSION file in package

0.1.0
^^^^^
Wed Dec 21 2016

* Initial Release
