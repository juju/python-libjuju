# Welcome to python-libjuju contributing guide <!-- omit in toc -->

Thank you for investing your time in contributing to our project! :confetti_ball: :sparkles:

In this guide, you will get an overview of the contribution workflow from opening an issue,
creating a PR, reviewing, and merging the PR.

To get an overview of the project, read the [README](https://github.com/juju/python-libjuju/blob/master/docs/readme.rst).

Discussions are very welcome in our Juju community, join our [public Mattermost channel](https://chat.charmhub.io/charmhub/channels/juju).

## Tooling

- `uv`, https://docs.astral.sh/uv/
- `pre-commit`, https://pre-commit.com/
- Python 3.8 ~ 3.13, https://www.python.org/downloads/

## Repository Settings

- Commit titles must follow [conventional commit format](https://www.conventionalcommits.org/), see [types and scopes](https://github.com/juju/juju/blob/main/doc/conventional-commits.md).
- Commits have to be signed, see [GitHub advice](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits); you can [use your SSH key](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification#ssh-commit-signature-verification).
- For Warthogs, CLA is assumed when commits are authored with your `@canonical.com` email.
- For others, please sign the CLA at https://launchpad.net/ and read [further details](https://ubuntu.com/legal/contributors/faq) here.

## Bot Commands

When a pull request has been reviewed, passes basic tests and the branch is up to date, a maintainer will trigger the Jenkins merge flow by adding a comment `/merge`.

Likewise, a `/build` comment can be used to trigger a fresh CI run in Jenkins.

## Issues

### Create a new issue

If you spot a problem, [search](https://docs.github.com/en/github/searching-for-information-on-github/searching-on-github/searching-issues-and-pull-requests#search-by-the-title-body-or-comments)
in the [issues page](https://github.com/juju/python-libjuju/issues) to see if an issue already exists about what you're interested in.
If a related issue doesn't exist, then go ahead and file a [new issue](https://github.com/juju/python-libjuju/issues/new?assignees=&labels=bug&projects=&template=BugReport.yml)
with our issue template. On the issue form, the most important fields for us are the `Python-libjuju version`, `Juju version`, and
the `Reproduce/Test` fields to quickly act on it. The `Repdouce/Test` section is especially important, as it makes it much easier to diagnose
problems and test solutions. Please try to distill your issue and reduce it to a smaller piece of code.

> **_NOTE:_** Please refrain from saying "here's my repository/project/charm that uses
python-libjuju, get that and run this integration test, and you'll see the issue".

### Submit a feature request

If you're reporting some missing feature, or some functionality that you'd like to have in python-libjuju, feel free to use our
[feature request form](https://github.com/juju/python-libjuju/issues/new?assignees=&labels=wishlisted&projects=&template=FeatureRequest.yml)
to report it to us, and we'll make it happen for you. Make sure to fill out the `Code I'd Like to Run` section, so once your feature is implemented we can turn it into a test
to make sure everything's working exactly as planned.

### Issue Workflow

After an issue is created, it's in the `untriaged` state. Once a week, we walk through every open issue and triage them.
An issue is triaged when it has the track label (e.g. `2.9`, `3.2`). And once it's assigned to a milestone, that means we're committing to it, i.e., someone's actively working on it.

Scan through our [existing issues](https://github.com/juju/python-libjuju/issues) to find one that interests you.
You can narrow down the search using `labels` as filters. See our [Labels](https://github.com/juju/python-libjuju/labels) for more information on that.
As a general rule, we don’t assign issues to anyone. If you find an issue to work on, you are welcome to open a PR with a fix.


## Supporting a new Juju release

When new versions of Juju are released, there may be api (facade) changes, and python-libjuju needs to be updated to support them.

Every Juju build facilitates this with the inclusion of a json schema file (found in the Juju codebase under apiserver/facades/schema.json).
Juju's continuous integration testing ensures that this file is always kept up to date.

Some Juju releases may not feature any api changes at all.
Supporting many of the possible changes to the api is taken care of by python-libjuju's code generation.
The process for python-libjuju to take care of a Juju release is as follows.

### 1. Check previous release was handled correctly

If version X.Y.Z has just been released, where `Z` is 1 or more, then there should be:
1. A line in python-libjuju's `juju/client/SCHEMAS.md` starting with `X.Y.(Z-1)`
2. A schema file named `juju/client/schemas-juju-X.Y.(Z-1).json`

For example, if `3.4.17` was just released, we'd expect there to already be a line SCHEMAS.md starting with `3.4.16`, and a `schemas-juju-3.4.16.json` file.

If this is not the case, then you'll need to check what the latest release that has been handled is, and follow the process below for each release that hasn't been handled yet!


### 2. Adding the schema file for a Juju release

Now we know what release we're taking care of. Follow these steps to include the new schema file in python-libjuju:

### First release in a series

Is this the first release in a minor version series?

That is, an `X.Y.0` release, for example `3.6.0`?

1. Copy the X.Y.0 Juju release's `apiserver/facades/schema.json` file to `juju/client/schemas-juju-X.Y.0.json`
2. Add a new section to `juju/client/SCHEMAS.md`: `# X.Y`
3. Add a new line to that section: `X.Y.0`. For example, you might have:
```
# 3.6
3.6.0
```

Note: you should also remove any pre-release schemas, which have the naming format `schemas-juju.X.Y-rcN.json`, where `N` is the release candidate version.

### Subsequent releases

Otherwise, this is an `X.Y.Z` release where `Z` is 1 or more.

Here we have to check: is the `X.Y.Z` Juju release's `schema.json` file different from python-libjuju's `schemas-juju-X.Y.(Z-1).json`?

You could, for instance, run a command like:
```
diff $JUJU_RELEASE_SCHEMA $PREVIOUS_PYTHONLIBJUJU_SCHEMA
```

If there are **_any_ differences**, then:

1. Copy the X.Y.Z Juju release's `apiserver/facades/schema.json` file to `juju/client/schemas-juju-X.Y.Z.json`
2. Add a new line to the `# X.Y` section in `juju/client/SCHEMAS.md`:
```
X.Y.Z
```

If there are **<ins>no</ins> differences**, then:

1. Rename the `schemas-juju-X.Y.(Z-1).json` file to `schemas-juju-X.Y.Z.json` - or equivalently, remove the `schemas-juju-X.Y.(Z-1).json` file and add Juju's `schema.json` as `schemas-juju-X.Y.Z.json`

2. Add a new line to the `# X.Y` section in `juju/client/SCHEMAS.md`:

```
X.Y.Z (identical to $PREV)
````

Where `$PREV` is either `X.Y.(Z-1)`, or if `X.Y.(Z-1)` was also identical to a previous release, then that release number instead. You can see examples of this in `SCHEMAS.md`.

To analyse the differences in detail, you may use tooling and parsed schemata at https://github.com/dimaqq/juju-schema-analysis.

### 3. Generate python-libjuju client code from new schema

In the python-libjuju root directory, run `make client`.

This will run code generation and update the `juju/client/_definitions.py`, `juju/client/_client.py` and `juju/client/_client{N}.py`files as needed.

The `_client{N}.py` files, like `_client1.py` and `_client19.py` contain definitions for specific facade numbers (1 and 19 in this case). Running `make client` might result in the creation of some new numbered files.


### 4. Validate with newly generated code

Run the tests under `tests/validate`, for example:
```
python -m pytest tests/validate -vv
```

If the `test_client_facades` test fails, it means that the `client_facades` dictionary in python-libjuju's `juju/client/connection.py` doesn't match the new facades from code generation with the new schema file. In this case, we would expect some differences, so you can update the `client_facades` dictionary based on the output of the test so that it passes.


### 5. Open a PR

Check any changed files into version control, as well as any new `_client{N}.py` and `schemas-juju-X.Y.Z.json` files, and open a PR. A good PR title would be `chore: add schemas for juju X.Y.Z`.

Tests on this PR might fail. These failures will need to be investigated. One possible cause of failures would be if python-libjuju requires additional changes to support a new facade version. If this is the case, a potential solution is to manually move the problematic facade number from `client_facades` to `excluded_facade_versions`, and open an issue about supporting that facade.

You can run the integration tests locally, but they can be a bit unpredictable. You could also just push to your fork to have them run on github, but if you open a PR then the other maintainers can help out.
