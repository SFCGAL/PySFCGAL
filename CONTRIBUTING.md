# Contributing Guidelines

First off, thanks for considering to contribute to this project!

These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Git hooks

We use git hooks through [pre-commit](https://pre-commit.com/) to enforce and automatically check some "rules". Please install them (`pre-commit install`) before to push any commit.

See the relevant configuration file: `.pre-commit-config.yaml`.

## Code Style

Make sure your code *roughly* follows [PEP-8](https://www.python.org/dev/peps/pep-0008/) and keeps things consistent with the rest of the code:

- sorted imports: [isort](https://pycqa.github.io/isort/) is used to sort imports
- static analysis: [flake8](https://flake8.pycqa.org/en/latest/) is used to catch some dizziness and keep the source code healthy.
- static typing: [mypy](https://www.mypy-lang.org/) is used to have static type checks.

## Commit linter

We use the linter [commitizen](https://github.com/commitizen-tools/commitizen) with the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) configuration (the default one).

The commit message writing process can be guided by using `cz commit` instead of `git commit`.

## Run unit tests

In order to run unit tests, please consider installing the dependencies that are referenced in the requirement folder:

```bash
pip install -r requirements/unit_tests.txt
```

In particular, we use `icontract` in this context (this dependency is set as an extra dependency, as it might be unpackaged on some environments). The unit tests are run through `pytest`. This testing mode is actually used in the CI.

## Build documentation

The project documentation is built with [MkDocs](https://www.mkdocs.org/).

For more information on how to build documentation, see this [section](https://sfcgal.gitlab.io/pysfcgal/build/#how-to-build-the-documentation) in build page.
