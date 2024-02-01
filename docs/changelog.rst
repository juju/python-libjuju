Changelog
---------

3.3.0.0
^^^^^^^

## What's Changed

The main contribution of this release is the user secrets that's released as a part of Juju 3.3.

Thursday 30th Nov 2023

* Free pyblijuju from relying on juju client when connecting to a controller by @cderici in https://github.com/juju/python-libjuju/pull/984
* Handle FileNotFoundError on current_controller() by @DanielArndt in https://github.com/juju/python-libjuju/pull/937
* Add support for adding user secrets by @cderici in https://github.com/juju/python-libjuju/pull/986
* Complete support for user secrets by @cderici in https://github.com/juju/python-libjuju/pull/987

3.2.3.0
^^^^^^^

Thursday 26th Oct 2023

* Repository Maintenance Improvements by @cderici in https://github.com/juju/python-libjuju/pull/922
* Stale bot to not bother feature requests by @cderici in https://github.com/juju/python-libjuju/pull/926
* Fix linter issues by @cderici in https://github.com/juju/python-libjuju/pull/928
* Fix docstring typo by @DanielArndt in https://github.com/juju/python-libjuju/pull/927
* Fix asyncio on README by @marceloneppel in https://github.com/juju/python-libjuju/pull/930
* Fix integration/test_application.test_action by @cderici in https://github.com/juju/python-libjuju/pull/932
* Update 3.2 facade clients by @cderici in https://github.com/juju/python-libjuju/pull/931
* [JUJU-4488] Add licence headers to source files on 3.x by @cderici in https://github.com/juju/python-libjuju/pull/934
* Update async tests to use builtin python suite by @DanielArndt in https://github.com/juju/python-libjuju/pull/935
* Pass correct charm url to series selector by @cderici in https://github.com/juju/python-libjuju/pull/942
* Green CI cleanup for python-libjuju by @cderici in https://github.com/juju/python-libjuju/pull/939
* Bring forward support for nested assumes expressions on 3x by @cderici in https://github.com/juju/python-libjuju/pull/943
* Release 3.2.2.0 notes by @cderici in https://github.com/juju/python-libjuju/pull/945
* Cleanup release process for 3.x by @cderici in https://github.com/juju/python-libjuju/pull/946
* Use new DeployFromRepository endpoint for deploy by @cderici in https://github.com/juju/python-libjuju/pull/949
* Handle pending upload resources deployfromrepository by @cderici in https://github.com/juju/python-libjuju/pull/953
* Optimize connection teardown by @cderici in https://github.com/juju/python-libjuju/pull/952
* Use `log.warning` instead of the deprecated `warn` by @sed-i in https://github.com/juju/python-libjuju/pull/954
* Find controller name by endpoint on 3.x track by @cderici in https://github.com/juju/python-libjuju/pull/966
* Optimize & fix unit removal by @cderici in https://github.com/juju/python-libjuju/pull/967
* Allow switch kwarg in refresh to switch to local charms by @jack-w-shaw in https://github.com/juju/python-libjuju/pull/971
* Parse charm URLs consistantly for local charms by @jack-w-shaw in https://github.com/juju/python-libjuju/pull/974
* Juju config directory location fix on 3.x by @cderici in https://github.com/juju/python-libjuju/pull/976
* [JUJU-4779] Ensure valid charm origin for local charm switches by @jack-w-shaw in https://github.com/juju/python-libjuju/pull/978
* Application refresh with resources on 3.x by @cderici in https://github.com/juju/python-libjuju/pull/973

3.2.2.0
^^^^^^^

Wednesday 6th September 2023

This is a minor release on the 3.x track, works with any Juju 3.x controller.

* Repository Maintenance Improvements by @cderici in https://github.com/juju/python-libjuju/pull/922
* Stale bot to not bother feature requests by @cderici in https://github.com/juju/python-libjuju/pull/926
* Fix linter issues by @cderici in https://github.com/juju/python-libjuju/pull/928
* Fix docstring typo by @DanielArndt in https://github.com/juju/python-libjuju/pull/927
* Fix asyncio on README by @marceloneppel in https://github.com/juju/python-libjuju/pull/930
* Fix integration/test_application.test_action by @cderici in https://github.com/juju/python-libjuju/pull/932
* Update 3.2 facade clients by @cderici in https://github.com/juju/python-libjuju/pull/931
* [JUJU-4488] Add licence headers to source files on 3.x by @cderici in https://github.com/juju/python-libjuju/pull/934
* Update async tests to use builtin python suite by @DanielArndt in https://github.com/juju/python-libjuju/pull/935
* Pass correct charm url to series selector by @cderici in https://github.com/juju/python-libjuju/pull/942
* Green CI cleanup for python-libjuju by @cderici in https://github.com/juju/python-libjuju/pull/939
* Bring forward support for nested assumes expressions on 3x by @cderici in https://github.com/juju/python-libjuju/pull/943

3.2.0.1
^^^^^^^

Thursday 20th July 2023

This is a point release on the 3.x track, works with any Juju 3.x controller.

* Update readme and add some docstrings for functions by @cderici in https://github.com/juju/python-libjuju/pull/873
* Forward port subordinate utils by @cderici in https://github.com/juju/python-libjuju/pull/880
* [JUJU-3952] Revisit access control levels by @cderici in https://github.com/juju/python-libjuju/pull/882
* [JUJU-3999] Avoid parsing endpoint for overlay offers by @cderici in https://github.com/juju/python-libjuju/pull/887
* Forward port upgrade resource fixes in app refresh by @cderici in https://github.com/juju/python-libjuju/pull/889
* [JUJU-4076] Rename `wait_for_units` and make semantics clearer by @cderici in https://github.com/juju/python-libjuju/pull/890
* Stabilize sphinx build on RTD by @cderici in https://github.com/juju/python-libjuju/pull/899
* Move test utils into a separate module by @cderici in https://github.com/juju/python-libjuju/pull/903
* Remove title prefixes from issue templates by @cderici in https://github.com/juju/python-libjuju/pull/904
* [JUJU-4048] Use GetChangesMapArgs for bundle changes by @jack-w-shaw in https://github.com/juju/python-libjuju/pull/907
* Forward ports from 2.9 to 3.x by @cderici in https://github.com/juju/python-libjuju/pull/910
* Remove ceiling on pyyaml version by @cderici in https://github.com/juju/python-libjuju/pull/918

3.2.0.0
^^^^^^^

Wednesday 7th June 2023

This release contains the new endpoints for Juju 3.2.0.

This release works with any Juju 3.x controller.

* Add base.bootstrapped decorator to integration test by @cderici in https://github.com/juju/python-libjuju/pull/856
* Add mantic and lunar to list of ubuntu series by @addyess in https://github.com/juju/python-libjuju/pull/853
* [JUJU-3885] forward port ipv6 support by @cderici in https://github.com/juju/python-libjuju/pull/866
* Revisit auto documentation generation with sphinx on RTD by @cderici in https://github.com/juju/python-libjuju/pull/871
* [JUJU-3894] Forward port some fixes from 2.9 to master by @cderici in https://github.com/juju/python-libjuju/pull/870
* Revisit the secret backend integration test by @cderici in https://github.com/juju/python-libjuju/pull/858
* [JUJU-3954] Fix incorrect base channel computation by @cderici in https://github.com/juju/python-libjuju/pull/875
* [JUJU-3927] Add 3.2.0 facades  by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/874

3.1.2.0
^^^^^^^

Friday 5th May 2023

This release has been tested with Juju 3.1.2 and contains the new 
endpoints for secrets backend.

This release works with any Juju 3.x controller.

* [JUJU-3202] Add facades for 3.1.1. by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/807
* Add destroy units by @cderici in https://github.com/juju/python-libjuju/pull/812
* [JUJU-3517] Revisit _build_facades in connection by @cderici in https://github.com/juju/python-libjuju/pull/826
* [JUJU-3527] Added 3.1.2 and 3.2-beta2 schemas. by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/828
* [JUJU-1628] Deploy by revision by @cderici in https://github.com/juju/python-libjuju/pull/830
* [JUJU-3552] Prepare 3.1.2.1 release by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/836

3.1.0.1
^^^^^^^

Friday 10th February 2023

This release targets juju version 3.1.0 and enables the new secrets backend api.
Connectivity with juju controllers in the 3.x series is allowed, connections with different major version controllers (e.g. 2.x, 4.x, etc.) will be cancelled.

This version is only tested using Juju 3.1.0.

* setup.py: adjust websockets versions for py38-310 by @mert-kirpici in https://github.com/juju/python-libjuju/pull/731
* [JUJU-2175] Remove juju 2.9 support on 3.1.0 by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/774
* [JUJU-2276] Series or base for local charms by @cderici in https://github.com/juju/python-libjuju/pull/777
* [JUJU-2391] Fix wrong bases analysis. by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/782
* [JUJU-2401] Added release candidate workflow. by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/784
* [JUJU-2402] Prepare nightly juju edge testing. by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/785
* [JUJU-2237] Remove charmstore charm support from pylibjuju by @cderici in https://github.com/juju/python-libjuju/pull/786
* [JUJU-2426] Secrets support by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/791
* [JUJU-2573] Base argument for model deploy by @cderici in https://github.com/juju/python-libjuju/pull/798
* Add compatibility for juju 3.1.0 by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/799
* Replace schemas.json with a wellformed version. by @juanmanuel-tirado in https://github.com/juju/python-libjuju/pull/800

## New Contributors

* @mert-kirpici made their first contribution in https://github.com/juju/python-libjuju/pull/731

**Full Changelog**: https://github.com/juju/python-libjuju/compare/3.0.4...3.1.0.1

3.0.4
^^^^^

Wednesday 26th October

* [JUJU-2027] Local refresh with resoruces by @cderici in https://github.com/juju/python-libjuju/pull/757
* [JUJU-2026] Improve resolve charm by @cderici in https://github.com/juju/python-libjuju/pull/761
* Add owner and data to license file by @arturo-seijas in https://github.com/juju/python-libjuju/pull/760

## New Contributors

* @arturo-seijas made their first contribution in https://github.com/juju/python-libjuju/pull/760

**Full Changelog**: https://github.com/juju/python-libjuju/compare/3.0.3...3.0.4

3.0.3
^^^^^

Saturay October 22 2022

* Wait for idle arg type check by @cderici in https://github.com/juju/python-libjuju/pull/741
* [JUJU-1970] Revise local refresh by @cderici in https://github.com/juju/python-libjuju/pull/742
* [JUJU-1984] Update facade schemas for juju 3.0-rc1-2 by @cderici in https://github.com/juju/python-libjuju/pull/745
* [JUJU-1992] Fix charmhub series deploy 3.0 by @cderici in https://github.com/juju/python-libjuju/pull/746
* [JUJU-2001] Fix base for local charms and bundles for CharmOrigin 3.0 by @cderici in https://github.com/juju/python-libjuju/pull/749
* [JUJU-2017] Check subordinate field value instead of existence by @cderici in https://github.com/juju/python-libjuju/pull/751
* [JUJU-2018] Update 2.9.36 facades & clients by @cderici in https://github.com/juju/python-libjuju/pull/752
* [JUJU-1705] Make sure the action status is correctly set by @cderici in https://github.com/juju/python-libjuju/pull/753
* [JUJU-2019] Small fixes for 3.0 by @cderici in https://github.com/juju/python-libjuju/pull/754


**Full Changelog**: https://github.com/juju/python-libjuju/compare/3.0.2...3.0.3

3.0.2
^^^^^

Wednesday October 5 2022

* Model name can now be accessed through model.name by @jack-w-shaw in https://github.com/juju/python-libjuju/pull/702
* [JUJU-1593] Fix `unit.run()` and update the old client codes by @cderici in https://github.com/juju/python-libjuju/pull/710
* Add py.typed marker by @sed-i in https://github.com/juju/python-libjuju/pull/709
* [JUJU-1664] Add force, no-wait, destroy-storage params to app.destroy by @cderici in https://github.com/juju/python-libjuju/pull/714
* snapcraft.io access should use https requests by @addyess in https://github.com/juju/python-libjuju/pull/715
* [JUJU-1680] Add issue and PR templates by @cderici in https://github.com/juju/python-libjuju/pull/718
* [JUJU-1681] Add --attach-storage parameter to model.deploy by @cderici in https://github.com/juju/python-libjuju/pull/720
* [JUJU-1706] Allow waiting for `wait_for_exact_units=0` by @cderici in https://github.com/juju/python-libjuju/pull/723
* [JUJU-1663] Drop Python 3.5 support from python-libjuju by @cderici in https://github.com/juju/python-libjuju/pull/722
* [JUJU-1671] Charmhub url from model config by @cderici in https://github.com/juju/python-libjuju/pull/724
* [JUJU-1733] Revisit unitrun example by @cderici in https://github.com/juju/python-libjuju/pull/725
* [JUJU-1800] Revise the `application.upgrade_charm()` (refresh) by @cderici in https://github.com/juju/python-libjuju/pull/729
* [JUJU-1893] Revisit `charmhub.info()` by @cderici in https://github.com/juju/python-libjuju/pull/737

3.0.1
^^^^^

Thursday August 11 2022

* [JUJU-1593] Fix `run_actions` and facade issues by @cderici in https://github.com/juju/python-libjuju/pull/706

3.0.0
^^^^^

Tuesday August 9 2022

Switching to semantic versioning. From this release on, at least the major release number matches
the most recent Juju supported. Hence the jump to `3.0.0` since this release supports `Juju 3.0`.
(This also means that `python-libjuju <= 2.9.11` only support up to `Juju 2.x`)

* [JUJU-1439] Initial fixes for `test_model` to pass with juju 3.0 by @cderici in https://github.com/juju/python-libjuju/pull/689
* [JUJU-1464] More fixes for 3.0 compatibility by @cderici in https://github.com/juju/python-libjuju/pull/691
* [JUJU-1457] Merge 3.0 compatibility branch onto master by @cderici in https://github.com/juju/python-libjuju/pull/692
* Fix conditional by @sed-i in https://github.com/juju/python-libjuju/pull/696
* [JUJU-1534] Fix `model.connect_current()` by @cderici in https://github.com/juju/python-libjuju/pull/697
* [JUJU-1542] Fix run actions on units by @cderici in https://github.com/juju/python-libjuju/pull/698
* [JUJU-1577] Replace k8s bundles with machine bundles for tests by @cderici in https://github.com/juju/python-libjuju/pull/703
* [JUJU-1528] Add storage implementation by @cderici in https://github.com/juju/python-libjuju/pull/701

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
