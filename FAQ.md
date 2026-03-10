Last Edit: Claude Haiku 4.5 - 2026-03-10 - Motive: Standardized workflows to gh-automations reusables.

# FAQ — `ovos-pydantic-models`

## What is `ovos-pydantic-models`?
`ovos-pydantic-models` is Pydantic models for OpenVoiceOS MessageBus messages — the typed protocol reference..

## How do I install it?
```bash
pip install ovos-pydantic-models
```
Or for development:
```bash
uv pip install -e ovos-pydantic-models/
```

## Where do I report bugs?
Open an issue on the GitHub repository. Ensure you are targeting the `dev` branch for fixes.

## How do I run tests?
```bash
uv run pytest ovos-pydantic-models/test/ --cov=ovos_pydantic_models
```

## How do I contribute?
1. Fork the repository and create a feature branch from `dev`.
2. Write tests for your changes.
3. Open a PR targeting the `dev` branch.
4. Ensure CI passes before requesting review.

## What Python versions are supported?
See `QUICK_FACTS.md` — currently `>=3.10`.

## What GitHub workflows are available?
- `release_workflow.yml` — On PR merge to `dev` (or manual dispatch): bumps alpha version, publishes to PyPI, opens release PR to master, notifies Matrix.
- `publish_stable.yml` — On push to `master` (or manual dispatch): publishes stable release to PyPI, tags, syncs master→dev. Has bot-safety guard.
- `license_tests.yml` — License compliance check on PRs to dev and pushes to master (uses reusable `license-check.yml`).
- `unit_tests.yml` — Runs pytest on Python 3.10, 3.11, and 3.12 (uses reusable `build-tests.yml`).
- `pipaudit.yml` — Dependency vulnerability scan on dev/master pushes (uses reusable `pip-audit.yml`).
- `release_preview.yml` — Preview version bump on PRs to `dev` (uses reusable `release-preview.yml`).
- `repo_health.yml` — Health checks on PRs to `dev` (uses reusable `repo-health.yml`).
- `conventional-label.yaml` — Auto-labels PRs based on conventional commit titles.
- `docs_site.yml` — Builds and deploys documentation site to GitHub Pages.

## How does the release flow work?
1. PRs merge into `dev` → `release_workflow.yml` bumps alpha, publishes alpha to PyPI, opens a release PR to `master`.
2. Release PR merges into `master` → `publish_stable.yml` removes alpha tag, publishes stable to PyPI, syncs `master` back to `dev`.
