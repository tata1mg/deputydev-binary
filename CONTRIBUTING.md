# Contributing to DeputyDev Binary

Thanks for your interest in improving DeputyDev Binary! This guide explains the project layout, local development workflows, code style, and how to submit changes.

If you’re new to this codebase, start with the README and in-code docstrings. Any previously separate docs pages are no longer required.


## Project layout (quick tour)

- app/ — Service source code
  - clients/ — External service integrations (e.g., OneDev, generic web client)
  - dataclasses/ — Data transfer objects for diff application and codebase search
  - models/ — Request/response DTOs used by routes and services
    - dtos/
      - url_dtos/ — URL processing models (Pydantic)
      - collection_dtos/ — Collections and persistence models
  - repository/ — Data access layer and repositories (e.g., URL content)
  - routes/ — API endpoint handlers (auth, search, diff, MCP, etc.)
  - services/ — Business logic layer (search, diff, URL, MCP, caching, reranker, review)
  - utils/ — Shared utilities, constants, error/response helpers
  - service.py — Main application entrypoint
- ripgrep/ — Embedded ripgrep binary/assets used by search utilities
- pyproject.toml — Project metadata, dependencies, Python version
- ruff.toml — Lint/format rules
- .pre-commit-config.yaml — Hooks (Ruff, uv-lock)
- uv.lock — Dependency lockfile
- README.md — Overview, prerequisites, and local setup
- CODE_OF_CONDUCT.md — Community standards

Important: This codebase expects type hints and adheres to strict lint rules (Ruff includes ANN* checks). Keep public-facing APIs (HTTP endpoints) stable and documented in the README.


## Prerequisites and local setup

To avoid duplication, prerequisites (Python versions, uv) and setup steps live in README.md. Follow the README for installing dependencies, enabling pre-commit, and running local checks.


## Install and build

See README.md for the authoritative setup and build instructions (uv sync, pre-commit install, Ruff commands, binary build with Nuitka). This document focuses on contribution workflows and standards.


## Code style and quality

Type hints and style
- Type hints are required for function parameters and return types (public and private). Annotate *args/**kwargs when used.
- Keep modules cohesive and small. Extract shared helpers to app/utils when appropriate.
- Avoid top-level side effects on import; prefer explicit functions/classes.

Ruff (lint and format)
- Format: uv run ruff format .
- Lint: uv run ruff check .
- Config: ruff.toml (line-length 120, import ordering, PEP8 naming, complexity checks, no print statements, prefer pathlib, type-hint checks, etc.)

Pre-commit
- Install: pre-commit install
- Run all hooks: pre-commit run --all-files

Logging and errors
- Use existing error handling utilities under app/utils (e.g., route_error_handler) and structured logging per logging_config.py.
- Raise/propagate meaningful exceptions; return safe error responses from routes.

Public APIs (HTTP endpoints)
- Keep endpoints stable and documented in README.md. Avoid breaking changes; if required, coordinate with maintainers.


## Working on core functionality

Routes
- Add or modify endpoints under app/routes/.
- Keep route modules focused; delegate logic to services.

Services
- Implement business logic in app/services/ (codebase search, URL processing, diff application, caching, reranker, review, MCP, etc.).
- Keep services modular and reusable; avoid cross-cutting side effects.

DTOs and models
- Use Pydantic models for request/response DTOs under app/models/dtos/ and app/dataclasses/ where applicable.
- Validate inputs early in routes/services; prefer explicit types.

Clients
- Place external integrations under app/clients/ (e.g., OneDev, generic web client). Centralize common behaviors.

Repositories
- Follow patterns in app/repository/ for data access and persistence.

Constants and configuration
- Add shared constants under app/utils/constants.py or app/utils/constant/ as appropriate.
- If you introduce new configuration knobs, document them in README.md.


## Running checks and debugging

- uv run ruff format .
- uv run ruff check .
- pre-commit run --all-files

If you add a test suite (recommended for non-trivial features):
- Use pytest in a tests/ directory.
- Add minimal fixtures and keep tests fast and deterministic.


## Submitting changes

1) Fork-based workflow (default; non-maintainers)
- Non-maintainers cannot create branches on the upstream repository.
- Fork this repository to your own workspace/account.
- In your fork, create a branch using the same conventions: feat/…, fix/…, chore/…, docs/…
- Push to your fork and open a Pull Request against the upstream default branch (usually main). If unsure, target main.
- Enable "Allow edits by maintainers" on the PR (if your platform supports it).

2) Maintainers-only workflow (optional)
- Maintainers may create branches directly in the upstream repository.
- Branch naming: feat/…, fix/…, chore/…, docs/…

3) Ensure quality gates pass
- Local lint/format pass (ruff format, ruff check)
- Pre-commit hooks pass
- Update README.md if you introduce user-visible changes or configuration
- Add tests or usage notes for behavioral changes

4) Commit messages
- Prefer clear, conventional-style messages (feat:, fix:, chore:, docs:, refactor:)

5) Open a Pull Request
- Describe the motivation, what changed, and how you validated it
- Link related issues
- Avoid bumping the version; maintainers handle releases


## Versioning and release notes

- Project version is defined in pyproject.toml.
- Coordinate version bumps with maintainers; do not change the version in PRs unless asked.
- If a CHANGELOG.md is used, add/update entries describing user-facing changes.


## Security and privacy

- Do not commit secrets or tokens. Use local environment configuration as needed (document in README if applicable).
- Be mindful of logs; avoid including sensitive data in logs.


## Code of Conduct

By participating, you agree to abide by our Code of Conduct. See CODE_OF_CONDUCT.md at the repository root.


## Troubleshooting

- Python version errors: Ensure your Python matches the range in pyproject.toml (>=3.11, <3.12).
- Missing tools: Ensure uv, pre-commit, and ruff are installed and available.
- Lockfile updates: If dependencies change, run uv lock (or rely on the uv-lock pre-commit hook) and commit uv.lock.
- Lint issues: Run uv run ruff format . then uv run ruff check . to see remaining violations.
- Binary build issues: Refer to README’s Nuitka build steps and ensure the binary has execute permissions.


## Questions?

Open an issue or start a discussion in the repository. Thanks again for contributing to DeputyDev Binary!