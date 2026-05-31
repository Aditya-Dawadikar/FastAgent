# Publishing Guide

FastAgent uses **OIDC Trusted Publishing** — no PyPI API tokens are stored in GitHub secrets.
GitHub exchanges a short-lived OIDC token directly with PyPI at publish time.

---

## One-time setup

### 1. Configure Trusted Publishing on PyPI

Go to **pypi.org → Your account → Publishing → Add a new pending publisher**.

| Field          | Value                          |
| -------------- | ------------------------------ |
| PyPI project   | `fastagent`                    |
| Owner          | `aditya-dawadikar`             |
| Repository     | `FastAgent`                    |
| Workflow file  | `publish.yml`                  |
| Environment    | `pypi`                         |

Repeat the same steps on **test.pypi.org**, using environment name `testpypi`.

### 2. Create GitHub Environments

In the GitHub repo: **Settings → Environments → New environment**.

Create two environments:

- `testpypi` — no required reviewers
- `pypi` — add yourself as a **required reviewer** so every production publish needs a manual approval

### 3. That's it

No secrets to rotate. No tokens to store.

---

## Releasing a new version

1. Bump `__version__` in `src/fastagent/__init__.py`.
2. Update `CHANGELOG.md` — move entries from `[Unreleased]` to the new version block.
3. Commit and push to `main`.
4. Tag and push:

```bash
git tag v0.2.0
git push origin v0.2.0
```

The pipeline runs automatically:

```
test → verify-version → build → publish-testpypi → publish-pypi → github-release
```

Each stage gates the next. If your `pypi` environment has a required reviewer, GitHub will pause before the production publish and wait for approval.

---

## Pipeline stages

| Stage               | Purpose                                                     |
| ------------------- | ----------------------------------------------------------- |
| `test`              | Full pytest suite must pass on the tagged commit            |
| `verify-version`    | Git tag (e.g. `v0.2.0`) must match `__version__` in code   |
| `build`             | `hatch build` produces sdist + wheel; `twine check --strict` validates both |
| `publish-testpypi`  | Uploads to test.pypi.org; catches metadata or upload errors |
| `publish-pypi`      | Uploads to pypi.org; only runs if TestPyPI succeeded        |
| `github-release`    | Creates a GitHub Release with auto-generated release notes and the built artifacts attached |

---

## Supported tag formats

| Tag example    | Type              |
| -------------- | ----------------- |
| `v1.2.3`       | Stable release    |
| `v1.2.3rc1`    | Release candidate |
| `v1.2.3.post1` | Post-release      |
