# Contributing to FastAgent

Thank you for your interest in contributing!

## Development setup

```bash
git clone https://github.com/aditya-dawadikar/FastAgent
cd FastAgent
pip install -e ".[dev]"
pre-commit install
```

## Running tests

```bash
pytest
```

## Running lint

```bash
ruff check src tests
ruff format src tests
mypy
```

## Making changes

1. Fork the repository and create a branch from `main`.
2. Write tests for any new behavior.
3. Ensure `pytest` and `ruff check` pass.
4. Update `CHANGELOG.md` under `[Unreleased]`.
5. Open a pull request — fill out the template.

## Commit style

Use imperative mood: `Add retry backoff`, `Fix timeout on Windows`, `Remove unused import`.

## Versioning

FastAgent follows [Semantic Versioning](https://semver.org/). Breaking changes require a major version bump.

## Releases

Releases are triggered by pushing a `vX.Y.Z` tag to `main`. The CI pipeline builds and publishes to PyPI automatically.
