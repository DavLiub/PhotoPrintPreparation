# Architecture

## Current state

The repository currently contains a core-first Python package under `src/photo_processor/`:

- `main.py` as the CLI bootstrap
- `models/` for settings and processing result structures
- `core/` for resize and orientation logic plus batch orchestration
- `services/` for file scanning and output path generation
- `utils/` for low-level unit conversion helpers

This is enough for `0.1` core prototyping, but it does not yet match the target layered structure from the product specification.

## Target layering

The preferred package direction for `src/` is:

- `api/` for CLI and later GUI-facing entry adapters
- `app/` for use-case orchestration, controllers, and workflow coordination
- `core/` for stable business rules, resize math, orientation policies, and value objects
- `infra/` for Pillow adapters, file system IO, settings persistence, logging, and packaging-specific integration
- `bootstrap/` for application startup wiring
- `config/` for defaults, presets, and environment-aware runtime settings

## Mapping from current code

- `main.py` should eventually move toward `bootstrap/` plus `api/cli.py`
- `core/` now acts as the canonical pure-logic layer
- `app/use_cases/batch_processing.py` holds orchestration that used to live in `core/batch_processor.py`
- filesystem helpers moved toward `infra/filesystem/`
- `infra/imaging/image_processor.py` is the future adapter boundary for Pillow-backed processing

## Architectural rule

Core math must not depend on Pillow, GUI frameworks, or filesystem side effects. Infrastructure can depend on core rules, but not the reverse.
