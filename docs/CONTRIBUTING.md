# Welcome to python-libjuju contributing guide <!-- omit in toc -->

Thank you for investing your time in contributing to our project! :confetti_ball: :sparkles:

In this guide, you will get an overview of the contribution workflow from opening an issue,
creating a PR, reviewing, and merging the PR.

Use the table of contents icon <img src="https://github.com/github/docs/raw/41b5e9addc77f16f945ba3429b90c8f130aac9c2/contributing/images/table-of-contents.png" width="25" height="25" /> in the top right corner of this document to get to a specific section of this guide quickly.

## New contributor guide

To get an overview of the project, read the [README](https://github.com/juju/python-libjuju/blob/master/docs/readme.rst). If you need a primer on git, check out [Set up Git](https://docs.github.com/en/get-started/quickstart/set-up-git).

Let's get to some specifics:

<!---
- [Finding ways to contribute to open source on GitHub](https://docs.github.com/en/get-started/exploring-projects-on-github/finding-ways-to-contribute-to-open-source-on-github)
- [Set up Git](https://docs.github.com/en/get-started/quickstart/set-up-git)
- [GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [Collaborating with pull requests](https://docs.github.com/en/github/collaborating-with-pull-requests)


## Getting started

To navigate our codebase with confidence, see [the introduction to working in the docs repository](/contributing/working-in-docs-repository.md) :confetti_ball:. For more information on how we write our markdown files, see [the GitHub Markdown reference](contributing/content-markup-reference.md).

Check to see what [types of contributions](/contributing/types-of-contributions.md) we accept before making changes. Some of them don't even require writing a single line of code :sparkles:.

-->


## Pull Request

Thanks for considering to contribute code to our project! We accept and welcome all kinds of PRs! :tada:

The process is very simple.
- Fork the project into your account.
- Clone your fork.
- Add an upstream remote: `git add upstream git@github.com:juju/python-libjuju.git`
- Check with `git remote -v`, origin should point to your fork, upstream should point to ours.
- If your changes are going to be on top of a specific branch (e.g., `2.9`), then fetch and switch to that.
- `git switch -c your-branch-name`
- Make your changes, create your commits.
- `git push -u origin your-branch-name`

And that's it, just follow the link that Git will produce. We kindly ask you to follow our PR template (at least keep the sections there), so it can be faster for us to review and move it forward.

#### What's next

So when you create the PR, a bot might spam some messages there for admins to review the PR. Don't panic, everything's good. Someone from our team needs to push a button to allow for the CI to run.

Some time after we see the tests are passing, someone from our team will review. Whoever reviews
it might ask for some changes, or some tests to be fixed, etc. Finally, the PR will be approved, and again,
someone from our team (probably the reviewer) will comment `/merge`, which triggers the Juju bot to start the merging process, which will automagically complete and merge your PR onto the desired branch. :confetti_ball:

#### Some quick notes:

- Don't forget to [link PR any issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) if you are solving any.
- Enable the checkbox to [allow maintainer edits](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/allowing-changes-to-a-pull-request-branch-created-from-a-fork) so the branch can be updated for a merge.
- A `/build` comment will trigger a fresh CI run.
- If you run into any merge issues, checkout this [git tutorial](https://github.com/skills/resolve-merge-conflicts) to help you resolve merge conflicts and other issues.

### Your PR is merged!

Congratulations :tada::tada: The Juju team thanks you :sparkles:.

Now that you are part of the Juju community, hop into our [public Mattermost channel](https://chat.charmhub.io/charmhub/channels/juju) and join the conversation!


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