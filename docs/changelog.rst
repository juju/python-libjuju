Changelog
---------

2.9.42.3
^^^^^^^^

Wednesday May 24 2023

## What's Changed
* [JUJU-1467] Application status from API by @cderici in https://github.com/juju/python-libjuju/pull/849
* [JUJU-3750] Fix bug in Type.from_json() parsing simple entries by @cderici in https://github.com/juju/python-libjuju/pull/854


2.9.42.2
^^^^^^^^

Thursday May 11 2023

## What's Changed

* [JUJU-3253] add missing force in bundle deployment by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/815
* [JUJU-3348] Fix assumes parsing by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/820
* [JUJU-3404] Pass series info into origin for ResolveCharm by @cderici in https://github.com/juju/python-libjuju/pull/825
* Fix _resolve_charm errors by @cderici in https://github.com/juju/python-libjuju/pull/834
* [JUJU-3583] wait_for_idle to not block when enough units are ready by @cderici in https://github.com/juju/python-libjuju/pull/840
* [JUJU-3565] Expect and handle exceptions from the AllWatcher task by @cderici in https://github.com/juju/python-libjuju/pull/833
* Fixes to pass the CI problems regarding missing postgresql charm. by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/847
* [JUJU-3641] Fix local charm base channel discovery by @cderici in https://github.com/juju/python-libjuju/pull/846

2.9.42.1
^^^^^^^^

Wednesday March 8 2023

This is an scheduled release to support Juju 2.9.42.

* [JUJU-2935] update juju 2942 by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/809

2.9.38.1
^^^^^^^^

Wednesday January 18 2023

The 2.9.38.1 version breaks the existing python-libjuju release versioning policy.
Initially, the version number matches the juju version this release is intended
to support and has been tested against.

* Merge 2.9.11 by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/713
* add support for ipv6 by @jdkandersson in https://github.com/juju/python-libjuju/pull/726
* [JUJU-1979] Backport upgrade-charm fixes onto `2.9` by @cderici in https://github.com/juju/python-libjuju/pull/744
* [JUJU-2256] Add integration tests to github actions pinning juju 2.9 by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/775
* [JUJU-2392] Cherrypick to fix wrong bases by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/783
* [JUJU-2485] Added nightly built checks. by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/787
* [JUJU-2381] Facade updated to 2.9.38 by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/788

2.9.11
^^^^^^

Monday July 11 2022

* Add REPL quickstart subsection by @sed-i in https://github.com/juju/python-libjuju/pull/676
* Revision of test onos.charm by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/686
* [JUJU-1353] Parse assume directives. by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/685
* Replace deprecated juju.loop() calls from examples and documentation by @ittner in https://github.com/juju/python-libjuju/pull/687
* Fixed the bundle run when the channel is None by @oEscal in https://github.com/juju/python-libjuju/pull/664

2.9.10
^^^^^^

Thursday June 9 2022

* [JUJU-1155] Avoid incorrectly setting `series: kubernetes` for sidecar charms in k8s bundles by @cderici in https://github.com/juju/python-libjuju/pull/679
* [JUJU-1172] Visiting the pylibjuju CI by @cderici in https://github.com/juju/python-libjuju/pull/681
* [JUJU-1124] Avoid sending path across the wire for local resource file name by @cderici in https://github.com/juju/python-libjuju/pull/678

2.9.9
^^^^^

Wednesday April 26 2022

* [JUJU-835] Avoid ignoring asyncio exceptions in coroutines by @cderici in https://github.com/juju/python-libjuju/pull/658
* [JUJU-843] Attach-resource to check if given binary file by @cderici in https://github.com/juju/python-libjuju/pull/659
* [JUJU-858] Add quality of life feature ensure application removal at return by @cderici in https://github.com/juju/python-libjuju/pull/665
* [JUJU-965] Add a bit of client side constraint validation by @cderici in https://github.com/juju/python-libjuju/pull/666
* support python3.10 with later versions of websockets by @addyess in https://github.com/juju/python-libjuju/pull/673
* Revert "Avoid ignoring asyncio exceptions in coroutines" by @simskij in https://github.com/juju/python-libjuju/pull/672
* [JUJU-796] Add relate method and deprecate add-relation by @jack-w-shaw in https://github.com/juju/python-libjuju/pull/660
* [JUJU-981] Get series from deployed app instead of metadata when charm upgrade by @cderici in https://github.com/juju/python-libjuju/pull/671

2.9.8
^^^^^

Monday March 21 2022

* [JUJU-567] Use ModelManager instead of ControllerFacade to list available models by @cderici in https://github.com/juju/python-libjuju/pull/632
* [JUJU-573] Fix charm resolution for Juju 2.8.11 by @cderici in https://github.com/juju/python-libjuju/pull/633
* [JUJU-704] Remove non-implemented (stuıb) functions by @cderici in https://github.com/juju/python-libjuju/pull/646
* [JUJU-676] Avoid defaulting to empty string for charm origin by @cderici in https://github.com/juju/python-libjuju/pull/647
* Charmstore compatability of deploying bundles by @addyess in https://github.com/juju/python-libjuju/pull/650
* [JUJU-731] Subordinate charm num unit by @cderici in https://github.com/juju/python-libjuju/pull/648
* [JUJU-769] Facade schemas for 2.9.27 by @cderici in https://github.com/juju/python-libjuju/pull/652
* [JUJU-771] Auto switch to scale from add_unit on container based models by @cderici in https://github.com/juju/python-libjuju/pull/653

2.9.7
^^^^^

Friday February 11 2022

* [JUJU-556] Facade schemas for Juju 2.9.24 by @cderici in https://github.com/juju/python-libjuju/pull/626
* Provide extra metadata with charmstore.entity(...)  by @addyess in https://github.com/juju/python-libjuju/pull/635

2.9.6
^^^^^

Thursday January 27 2022

* [JUJU-320] Unit public address by @SimonRichardson in https://github.com/juju/python-libjuju/pull/600
* [JUJU-244] Add attach-resource by @cderici in https://github.com/juju/python-libjuju/pull/601
* [JUJU-140] Model.wait_for_idle -- for apps with no units yet by @cderici in https://github.com/juju/python-libjuju/pull/575
* [JUJU-367] Improve `get_charm_series` to check the model for series for a local charm by @cderici in https://github.com/juju/python-libjuju/pull/607
* [JUJU-366] Utility for connecting directly to existing connection by @cderici in https://github.com/juju/python-libjuju/pull/605
* Use public-address key instead of public_address by @wolsen in https://github.com/juju/python-libjuju/pull/610
* [JUJU-376] `wait_for_idle` to support scale down by @cderici in https://github.com/juju/python-libjuju/pull/613
* [JUJU-378] Utility for block_until-ing with a custom coroutine by @cderici in https://github.com/juju/python-libjuju/pull/614
* Fallback to 'local-fan' by @dparv in https://github.com/juju/python-libjuju/pull/612
* Minor comments on docs for block_until related functions. by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/617
* Additional checks in print status. by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/622

2.9.5
^^^^^

Friday December 3 2021

* remove the event loop arguments by @cderici in https://github.com/juju/python-libjuju/pull/560
* add debug-log by @cderici in https://github.com/juju/python-libjuju/pull/562
* Model status by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/563
* Pin cffi version to 1.14.6 for Python 3.5 by @cderici in https://github.com/juju/python-libjuju/pull/570
* Wait for applications to terminate on model reset by @balbirthomas in https://github.com/juju/python-libjuju/pull/572
* Babysitting python3.5 by @cderici in https://github.com/juju/python-libjuju/pull/571
* Deploy charmhub bundles by @cderici in https://github.com/juju/python-libjuju/pull/569
* Facade schemas for 2.9.17 by @SimonRichardson in https://github.com/juju/python-libjuju/pull/579
* Bundles with overlays by @cderici in https://github.com/juju/python-libjuju/pull/566
* Consistently getting a unit's public address by @cderici in https://github.com/juju/python-libjuju/pull/573
* [JUJU-158] Add python3.9 to setup.py by @cderici in https://github.com/juju/python-libjuju/pull/585
* [JUJU-157] Add note for removing services by @cderici in https://github.com/juju/python-libjuju/pull/583
* Added boolean entries to normalize values. by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/582
* [JUJU-138] Streamlining asyncio tasks/events by @cderici in https://github.com/juju/python-libjuju/pull/580
* [JUJU-234] Fix for small bug in task handling by @cderici in https://github.com/juju/python-libjuju/pull/589
* Ensure all watchers validate for the Id by @SimonRichardson in https://github.com/juju/python-libjuju/pull/592
* [JUJU-276] Facade schemas for 2.9.19 by @cderici in https://github.com/juju/python-libjuju/pull/594
* [JUJU-238] Small bug fix for old ClientFacade support by @cderici in https://github.com/juju/python-libjuju/pull/593
* [JUJU-239] Debug-log parameters by @cderici in https://github.com/juju/python-libjuju/pull/595
* [JUJU-213] Local type `file` resource support by @cderici in https://github.com/juju/python-libjuju/pull/590
* [JUJU-289] Use provided series in deploy if supported by @jack-w-shaw in https://github.com/juju/python-libjuju/pull/596
* [JUJU-292] Update the charms in the tests to use Charmhub by @cderici in https://github.com/juju/python-libjuju/pull/597
* Legacy "services" for describing "applications" within bundles are no longer supported. "applications" can be used as a direct replacement for "services" in bundles.yaml.
* The websocket (ws) in a Connection object became a read-only property.

2.9.4
^^^^^

Tuesday October 12 2021

* Charmhub deploy charm by @SimonRichardson in https://github.com/juju/python-libjuju/pull/483
* add wait_for_status instead of wait_for_active by @sed-i in https://github.com/juju/python-libjuju/pull/517
* Adds resource support for charmhub deployments by @tlm in https://github.com/juju/python-libjuju/pull/516
* Fix bug #519 and #522: Add local resources for bundles by @davigar15 in https://github.com/juju/python-libjuju/pull/520
* Patching some missing kwargs by @cderici in https://github.com/juju/python-libjuju/pull/527
* Implementing `backup` functionality by @cderici in https://github.com/juju/python-libjuju/pull/536
* Fix issue 532: Set the default_series properly by @davigar15 in https://github.com/juju/python-libjuju/pull/533
* A random small bug fix by @cderici in https://github.com/juju/python-libjuju/pull/541
* Allow ApplicationFacade set_config with non-string values by @cderici in https://github.com/juju/python-libjuju/pull/540
* Skip macaroon tests issue 534 by @cderici in https://github.com/juju/python-libjuju/pull/542
* Fix issue 530: Check the controller for unsynched models by @cderici in https://github.com/juju/python-libjuju/pull/539
* Upgrade setup-python action. by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/543
* Fix integration tests by @cderici in https://github.com/juju/python-libjuju/pull/544
* Bring juju/juju.py into life by @cderici in https://github.com/juju/python-libjuju/pull/546
* Extract resources info from apps in locally deployed bundle by @cderici in https://github.com/juju/python-libjuju/pull/552
* Fix for simple bug in bundle deployment code self.charm -> self['charm'] by @jnsgruk in https://github.com/juju/python-libjuju/pull/558
* Fix integration tests continued by @cderici in https://github.com/juju/python-libjuju/pull/547
* Get the config dir resolve logic into one place by @cderici in https://github.com/juju/python-libjuju/pull/555
* Complete the backups functionality by @cderici in https://github.com/juju/python-libjuju/pull/556

2.9.3
^^^^^

Monday August 12 2021

* Bug fix - Fix 'Default to bundle series if the charm has no series field' #514

2.9.2
^^^^^

Monday June 28 2021

* Bug fix - Fix 'metadata referenced before assignment' error #509

2.9.1
^^^^^

Wednesday June 16 2021

* Bug fix - Bundle Exposed endpoints missing #502
* Bug fix - Fix series requirement for local charms #504
* Add local charm update support #507

2.9.0
^^^^^

Thursday May 27 2021

* Update facade methods for Juju 2.9.0
* Update facade methods for Juju 2.9.1
* Bug fix - Support for Juju client proxies (LP#1926595)
* Bug fix - Honor charm channel in bundles #496
* Remove machine workaround for Juju 2.2.3

2.8.6
^^^^^

Tuesday March 23 2021

* Update facade methods for Juju 2.8.10
* Bug fix - Fix typo in param name for ScaleApplications
* Introduction of hostname property for Machines

2.8.5
^^^^^

Monday February 8 2021

 * Implement add_space and get_spaces.
 * Update facade controllers.
 * Support already archived (.charm or .zip) local charms.
 * Introduction of wait_for_bundle method.
 * Bug fix - Handle None in list_offers results
 * Bug fix - Update libraries to support Python 3.9+

2.8.4
^^^^^

Thursday October 1 2020

 * Update facade methods for Juju 2.8.3
 * Bug fix - Add force and max wait for destroying a model
 * Bug fix - Fix derivation of the application status

2.8.3
^^^^^

Friday August 28 2020

 * Bug fix - Export the CAAS model operator facade (#434)
 * Bug fix - Allow passing controllers to prevent consume reading local filesystem (#436)


2.8.2
^^^^^

Tuesday July 14 2020

 * Update facade methods for Juju 2.8.1
 * Add documentation to the client API methods (using the 2.8.1 changes)
 * Bug fix -Fixes application status being reported as unset (#430)
 * Bug fix - Handle Network Unreachable OSErrors (#426)

2.8.1
^^^^^

Monday May 18 2020

 * Fix positional argument usage in facade calls.
 * Add get shim to facade types.
 * Fix SSH await on unit
 * Fix integration tests
 * Fix tox.ini to use supported python versions.
 * Fix constraints regex using subscript on matches (py36).
 * Fix facade return type documentation.
 * Fix schema objects with array values.
 * Fix subscript lookups by using JSON keys.
 * Add definition test.

2.8.0
^^^^^

Wednesday May 13 2020

 * Update facade methods for Juju 2.8.0
 * Fixes codegen for Python 3.7+
 * Nested facade definitions are now deserialised properly (e.g. storage on ApplicationDeploy)
 * Missing client facades are now ignored and a warning is printed (#382)
 * Add SCP example (#383)
 * Add watch_model_summaries method to Controller (#390)
 * Bug fix - make_archive on Model handles symlinks (#391 #392)
 * Add SSH support for units and machines (#393)
 * Add connection HA support (#402)
 * Bug fix - resolve api_endpoints from controller (#406 #407)

2.7.1
^^^^^

Thursday January 9 2020

 * Added the missing facade type, when attempting to connect to a model.

2.7.0
^^^^^

Tuesday January 7 2020

 * Update facade methods for Juju 2.7.0
 * Fix an issue when querying CMR relations (#366) 
 * Fix storage support in bundles (#361)
 * Fix reporting of unit leaders (#374)
 * AddCloud API support (#370)

2.6.3
^^^^^

 * Refactor bundle handler code so that it can be more resilient against changes
   to the bundle changes API.
 * Updated the dependencies to the latest version (pyyaml)

2.6.2
^^^^^
Wednesday August 27 2019

 * Fixes validation issue with a go interface{} type (Any type) being returned
   from the Juju API server (#344)

2.6.1
^^^^^
Wednesday August 21 2019

 * Pylibjuju now validates arguments correctly, instead of relying on default
   positional argument values.

2.6.0
^^^^^
Wednesday August 14 2019

* Update facade methods for Juju 2.6.6
* Pylibjuju release now follows the cadence of Juju releases, which also
  includes bumping the version number to follow suit.
* Pinned API facades. All facades in Pylibjuju are now pinned to a set of
  facade versions that is more conservative to prevent breakages against new
  features. The ability to override the pinned facades and specify your own
  facade versions is possible upon connection to a controller or model.
* Cross model relations (CMR) when deploying and adding relations. Additionally
  getting information about the CMR offers are available on the model.
* Cross model relations (CMR) in bundles.
* Ability to export bundle including overlays.
* Manual provisioning without a ubuntu user (#335)
* Addition of remote applications when adding relations via SAAS blocks
* Applying topological sorting to bundle changes API response, allows deployment
  of complex bundles possible.
* Updated definitions types to include the latest information from Juju.
* Keyword arguments (`unknown_field` in code) are now available on Juju
  responses.

0.11.7
^^^^^^
Wednesday April 19 2019

* Update facade methods for Juju 2.6.4
* Support for trusted bundles and charms (See: Trust_ documentation)

.. _Trust: https://discourse.jujucharms.com/t/deploying-applications-advanced/1061#heading--trusting-an-application-with-a-credential

0.11.6
^^^^^^
Wednesday May 22 2019

* Disable hostname checking on controller connection (#305)
* Handle RedirectError payloads returned by Login RPCs (#303)


0.11.5
^^^^^^
Monday April 1 2019

* Handle deltas of unknown types (fixes connecting to Juju 2.6 controllers) (#299)
* Test fixes (#298)


0.11.4
^^^^^^
Monday April 1 2019

* Additional work with annotations. (#290)
* Check server cert. (#296)


0.11.3
^^^^^^
Wednesday March 13 2019

* k8s bundles no longer have application placement (#293)
* Add retry for connection if all endpoints fail (#288)
* Support generation of registration string for model sharing. (#279)
* Add Twine for dist upload on release (#284)


0.11.2
^^^^^^
Wednesday January 16 2019

* update facade methods for Juju 2.5-rc2 (#281)
* Add test case for redirect during connect (#275)
* Implement App.get_resources and pinned resources in bundles (#278)


0.11.1
^^^^^^
Thursday December 13 2018

* Fix bundles with subordinates for Juju <2.5 (#277)


0.11.0
^^^^^^
Tuesday December 11 2018

* Updates for new Juju version (#274)
* Fix wrong variable name in revoke_model function (#271)


0.10.2
^^^^^^
Tuesday September 18 2018

* set include_stats to false to reduce request time (#266)


0.10.1
^^^^^^
Monday September 17 2018

* Retry ssh in manual provision test (#265)
* Clean up lint and add lint coverage to travis config (#263)
* Increase the timeout for charmstore connections (#262)
* Fix log level of `Driver connected to juju` message (#258)


0.10.0
^^^^^^
Thursday August 16 2018

* Fix error due to scp extra opts order (#260)
* Implement set/get model constraints (#253)


0.9.1
^^^^^
Monday July 16 2018

* Update websockets to 6.0 to fix OS X support due to Brew update to Py3.7 (#254)


0.9.0
^^^^^
Friday June 29 2018

* python3.7 compatibility updates (#251)
* Handle juju not installed in is_bootstrapped for tests (#250)
* Add app.reset_config(list). (#249)
* Implement model.get_action_status (#248)
* Fix `make client` in Python 3.6 (#247)


0.8.0
^^^^^
Thursday June 14 2018

* Add support for adding a manual (ssh) machine (#240)
* Backwards compatibility fixes (#213)
* Implement model.get_action_output (#242)
* Fix JSON serialization error for bundle with lxd to unit placement (#243)
* Fix reference in docs to connect_current (#239)
* Wrap machine agent status workaround in version check (#238)
* Convert seconds to nanoseconds for juju.unit.run (#237)
* Fix spurious intermittent failure in test_machines.py::test_status (#236)
* Define an unused juju-zfs lxd storage pool for Travis (#235)
* Add support for Application get_actions (#234)


0.7.5
^^^^^
Friday May 18 2018

* Surface errors from bundle plan (#233)
* Always send auth-tag even with macaroon auth (#217)
* Inline jsonfile credential when sending to controller (#231)

0.7.4
^^^^^
Tuesday Apr 24 2018

* Always parse tags and spaces constraints to lists (#228)
* Doc index improvements (#211)
* Add doc req to force newer pymacaroons to fix RTD builds
* Fix dependency conflict for building docs

0.7.3
^^^^^
Tuesday Feb 20 2018

* Full macaroon bakery support (#206)
* Fix regression with deploying local charm, add test case (#209)
* Expose a machines series (#208)
* Automated test runner fixes (#205)

0.7.2
^^^^^
Friday Feb 9 2018

* Support deploying bundle YAML file directly (rather than just directory) (#202)

0.7.1
^^^^^
Monday Dec 18 2017

* Fix missed renames of model_uuids (#197)

0.7.0
^^^^^
Fri Dec 15 2017

* Fix race condition in adding relations (#192)
* Fix race condition in connection monitor test (#183)
* Fix example in README (#178)
* Fix rare hang during Unit.run (#177)
* Fix licensing quirks (#176)
* Refactor model handling (#171)
* Refactor users handling, add get_users (#170)
* Upload credential to controller when adding model (#168)
* Support 'applications' key in bundles (#165)
* Improve handling of thread error handling for loop.run() (#169)
* Fix encoding when using to_json() (#166)
* Fix intermittent test failures (#167)

0.6.1
^^^^^
Fri Sept 29 2017

* Fix failure when controller supports newer facade version (#145)
* Fix test failures (#163)
* Fix SSH key handling when adding a new model (#161)
* Make Application.upgrade_charm upgrade resources (#158)
* Expand integration tests to use stable/edge versions of juju (#155)
* Move docs to ReadTheDocs (https://pythonlibjuju.readthedocs.io/en/latest/)

0.6.0
^^^^^
Thu June 29 2017

* Implement scp functionality (#149)
* Add Unit.public_address property (#153)
* Adds support for getting/setting config on a model (#152)

0.5.3
^^^^^
Thu June 22 2017

* Improve handling of closed connections (#148)
* Configurable and larger max message size (#146)

0.5.2
^^^^^
Wed June 14 2017

* Fix deploying non-stable channels and explicit revs (#144)

0.5.1
^^^^^
Tue June 13 2017

* Update schema for Juju 2.3 alpha1 (#142)
* Improve API doc navigation and coverage (#141)
* Add type info to Model.add_machine docs (#138)

0.5.0
^^^^^
Thu June 8 2017

* Add machine status properties (#133)
* Add model context manager (#128)
* Implement Application.upgrade_charm method (#132)

0.4.3
^^^^^
Thu June 1 2017

* Accept new / unknown API fields gracefully (#131)
* Add support for new agent-version field in ModelInfo (#131)
* Replace pip with pip3 in install instructions (#129)
* Strip local:-prefix from local charm urls (#121)

0.4.2
^^^^^
Wed May 10 2017

* Support (and prefer) per-controller macaroon files (#125)

0.4.1
^^^^^
Wed Apr 27 2017

* Remove VERSION_MAP and rely on facade list from controller (#118)
* Refactor connection task management to avoid cancels (#117)
* Refactored login code to better handle redirects (#116)

0.4.0
^^^^^
Wed Apr 19 2017

* Feature/api version support (#109)
* Expanding controller.py with basic user functions, get_models and
  destroy (#89)
* Added Monitor class to Connection. (#105)
* Support placement lists (#103)
* Include resources from store when deploying (#102)
* Allow underscore to dash translation when accessing model
  attributes (#101)
* Added controller to ssh fix. (#100)
* Regen schema to pick up missing APIs
* Improve error handling
* Fix issue where we do not check to make sure that we are receiving the
  correct response.
* Retry calls to charmstore and increase timeout to 5s
* Make connect_model and deploy a bit more friendly
* Fix model name not including user
* Implement Model.get_status
* Add integration tests.

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
