# pyspartn How to contribute

**pyspartn** is a volunteer project and we appreciate any contribution, from fixing a grammar mistake in a comment to extending device test coverage or implementing new functionality. Please read this section if you are contributing your work.

Being one of our contributors, you agree and confirm that:

* The work is all your own.
* Your work will be distributed under a BSD 3-Clause License once your pull request is merged.
* You submitted work fulfils or mostly fulfils our coding conventions, styles and standards.

Please help us keep our issue list small by adding fixes: #{$ISSUE_NO} to the commit message of pull requests that resolve open issues. GitHub will use this tag to auto close the issue when the PR is merged.

If you're adding or amending SPARTN payload definitions, it would be helpful to quote/hyperlink the specific documentation source and version. Bear in mind we are only able to implement functionality based on **public domain** sources (_unless we have an explicit dispensation from any copyright holder_).

## Coding conventions

* This is open source software. Code should be as simple and transparent as possible. Favour clarity over brevity.
* The code should be compatible with Python 3.8+.
* Avoid external library dependencies unless there's a compelling reason not to.
* We use and recommend Visual Studio Code with the Python extension for development and testing.
* Code should be documented in accordance with [Sphinx](https://www.sphinx-doc.org/en/master/) docstring conventions.
* Code should formatted using [black](https://pypi.org/project/black/) (>= 24.4).
* We use and recommend [pylint](https://pypi.org/project/pylint/) (>=3.0.1) for code analysis.
* We use and recommend [bandit](https://pypi.org/project/bandit/) (>=1.7.5) for security vulnerability analysis.
* Commits must be [signed](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits).

## Testing

We use python's native unittest framework for local unit testing, complemented by the GitHub Actions automated build and testing workflow. We endeavour to have at least 90% code coverage (_coverage is currently limited by available SPARTN test data sources_).

Please write unittest examples for new code you create and add them to the `/tests` folder following the naming convention `test_*.py`.

## Submitting changes

Please send a [GitHub Pull Request to pyspartn](https://github.com/semuconsulting/pyspartn/pulls) with a clear list of what you've done (read more about [pull requests](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/about-pull-requests)). Please follow our coding conventions (above) and make sure all of your commits are atomic (one feature per commit).

Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit
    > 
    > A paragraph describing what changed and its impact."



Thanks,

semuadmin