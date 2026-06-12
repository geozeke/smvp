# Codex Instructions

## Project Overview

`smvp` is a small Python CLI that sends the contents of a text
or HTML file as a multipart email body over SMTP with STARTTLS.

## Working Rules

- Keep changes focused and minimal.
- Use snake case for variable names (all words lowercase).
- Do not traverse or modify `.venv/`.
- Do not traverse cache or generated-state directories such as
  `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `__pycache__/`,
  or `.cache/` unless the task explicitly requires it.
- Prefer reading `README.md`, `pyproject.toml`, and files under
  `src/smvp/` first.
- Use `rg` for searches and `just` or `uv` for common
  project tasks when needed.
- Use project-local `UV_CACHE_DIR=.uv-cache` for `uv` workflows when
  practical.
- Prefer `pathlib.Path` objects over raw path strings where
  practical.
- Prefer truthiness checks like `if value:` and `if not value:` over
  explicit empty or `None` comparisons when they are semantically
  equivalent.
- Use strict NumPy-style docstrings for all function, class, and
  module docstrings.
- Always format new or changed Python code with `uv run ruff format .`
  or `just format`.
- When asked to review or modify `.gitignore`, also check
  whether Git global excludes are configured (for example,
  `git config --global core.excludesfile`) and factor that
  into recommendations.
- Preserve the existing simple CLI structure unless a change
  clearly requires a larger refactor.
- Wrap Markdown prose to 72 characters when practical, but do
  not break links, code spans, tables, or other formatting
  that would be harmed by wrapping.

## Code Areas

- `src/smvp/app.py`: CLI argument parsing and input
  validation.
- `src/smvp/__main__.py`: runnable module entry point for
  `python -m smvp`.
- `src/smvp/utilities.py`: environment validation, content
  conversion, MIME assembly, and SMTP delivery.
- `scripts/`: release and maintenance helpers.

## Documentation

- When making changes, ensure documentation and metadata remain
  consistent. This includes documents in instructions/ and todo/ (if
  they exist), and files like README.md and AGENTS.md. Also include
  argparse messages, docstrings, and code comments.

## Release Workflow

- Update code and documentation before preparing a release.
- Create a release branch, such as `release/v0.4.2`,
  `release/v0.4.3-beta.1`, or `release/v0.4.3-rc.1`.
- Run `just bump <version>` to update `CHANGELOG.md`,
  `pyproject.toml`, and `uv.lock`. Versions may include a leading
  `v`; beta and release candidate versions must use SemVer
  prerelease labels such as `0.4.3-beta.1` or `0.4.3-rc.1`.
- Commit the release changes, open a pull request, and merge it after
  checks pass.
- Update local `main` with `git pull --ff-only origin main`.
- Run `just tag-release` for only the version tag, or
  `just tag-release-latest` when the mutable `latest` tag should also
  move.
- Pushing a `v...` version tag starts the GitHub Actions release
  workflow, which creates a GitHub Release from matching notes in
  `CHANGELOG.md` or the appropriate `changelogs/v<major>.<minor>.x.md`
  archive. The workflow uses GitHub Actions' built-in `GITHUB_TOKEN`
  with `contents: write`.
- The `latest` tag is mutable and must not be treated as an immutable
  release record. Use it only when that version should become the
  default install target. Do not move `latest` for beta or release
  candidate versions unless that prerelease should explicitly become
  the default install target.
- PyPI publishing remains a separate manual workflow through
  `just publish-test` and `just publish-production`.

## Dependency Upgrade Workflow

- Run `just upgrade` only from a clean worktree.
- The command calls `scripts/upgrade_dependencies.sh`, checks for
  outdated first-order dependencies, upgrades only those packages, and
  creates one local `deps: Dependency Upgrades` commit when first-order
  locked dependency versions changed.
- The commit body lists each first-order dependency version change as
  `old -> new`.
- The command never pushes. Review the local commit before manually
  pushing it.
- If no first-order dependency versions changed, no commit is created
  and dependency files changed only by transitive updates are restored.
- Use `deps:` as the shared dependency-upgrade changelog prefix.
- Use `deprecate:` or `deprecated:` for deprecated changelog entries.

## Validation

- For syntax checks, prefer
  `python3 -m py_compile src/smvp/*.py`.
- Unit tests live in `tests/` and run with `uv run pytest`.
- Common validation tasks are `just lint`, `just test`,
  `just typecheck`, and `just build`.
- If dependencies are available, use the existing `uv`/`just`
  workflow instead of inventing a new one.

## Notes

- Treat SMTP credentials and any local secrets as sensitive.
- Runtime support targets Windows and Linux; repo tooling remains
  Linux-only.
