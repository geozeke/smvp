# Codex Instructions

## Project Overview

`smvp` is a small Python CLI that sends the contents of a text
or HTML file as a multipart email body over SMTP with STARTTLS.

## Working Rules

- Keep changes focused and minimal.
- Use snake case for variable names (all words lowercase).
- Do not traverse or modify `.venv/`.
- Prefer reading `README.md`, `pyproject.toml`, and files under
  `src/smvp/` first.
- Use `rg` for searches and `just` or `uv` for common
  project tasks when needed.
- Use strict NumPy-style docstrings for all function, class, and
  module docstrings.
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
- `src/smvp/utilities.py`: environment validation, content
  conversion, MIME assembly, and SMTP delivery.
- `scripts/`: release and maintenance helpers.

## Validation

- For syntax checks, prefer
  `python3 -m py_compile src/smvp/*.py`.
- Unit tests live in `tests/` and run with `uv run pytest`.
- If dependencies are available, use the existing `uv`/`just`
  workflow instead of inventing a new one.

## Notes

- Treat SMTP credentials and any local secrets as sensitive.
- Runtime support targets Windows and Linux; repo tooling remains
  Linux-only.
