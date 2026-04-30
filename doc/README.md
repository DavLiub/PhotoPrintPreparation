# Project Documentation

## Purpose

This directory contains the working project documentation for the repository. It is the maintainer-facing explanation of the current implementation, the target architecture, and the alignment path to the product specification in `source doc/PhotoProject_expanded.docx`.

## Source hierarchy

Use the following order when updating documentation or code:

1. `source doc/PhotoProject_expanded.docx` defines product scope and expected behavior.
2. `doc/` explains how that scope is mapped into architecture, data, algorithms, and implementation stages.
3. `src/` is the executable truth of what is implemented right now.

If `src/` and `source doc/` diverge, document the gap here instead of hiding it.

## Documents

- `architecture.md` describes current and target package layering.
- `implementation.md` describes what is implemented now and what remains planned.
- `math-algorithms.md` explains frame fitting, orientation choice, padding, and crop math.
- `data-model.md` explains the core data structures and their intended evolution.

## Documentation rules

- Keep documentation in English unless a Russian note is needed for product clarification.
- Separate `current state` from `target state`.
- Prefer concrete paths, module names, and formulas over abstract prose.
- Update `doc/` whenever `src/` changes in a way that affects architecture or behavior.
- When the application version changes, update `pyproject.toml` and `src/photo_processor/config/app_info.py` in the same change.
- Treat version bumps as:
  - patch for fixes and packaging corrections
  - minor for new user-visible functionality
  - major for breaking changes in workflow or compatibility
