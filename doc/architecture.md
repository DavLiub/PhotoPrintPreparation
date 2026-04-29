# Architecture

## Current state

The repository uses the standard Python `src/` layout:

- `src/` is the source container
- `src/photo_processor/` is the root application package
- the package is split into architectural layers inside that root package

This means `photo_processor` is not an extra layer. It is the application namespace. The real layers of the project are:

- `api/`
- `app/`
- `core/`
- `infra/`
- `bootstrap/`
- `config/`

This structure already reflects the intended direction from the product specification.

## Target layering

Inside `src/photo_processor/`, use the following responsibilities:

- `api/` for CLI and later GUI-facing entry adapters
- `app/` for use-case orchestration, controllers, and workflow coordination
- `core/` for stable business rules, resize math, orientation policies, and value objects
- `infra/` for Pillow adapters, file system IO, settings persistence, logging, and packaging-specific integration
- `bootstrap/` for application startup wiring
- `config/` for defaults, presets, and environment-aware runtime settings

## Mapping from current code

- `main.py` is now only a thin compatibility entry point
- `bootstrap/main.py` is the startup boundary
- `api/cli.py` owns command-line parsing and user-facing console flow
- `core/` now acts as the canonical pure-logic layer
- `app/use_cases/batch_processing.py` holds orchestration and application flow
- `infra/filesystem/` owns file scanning and output path generation
- `infra/imaging/image_processor.py` is the future adapter boundary for Pillow-backed processing

## Project-level interpretation

For this repository, there is currently only one real application package: `photo_processor`.

If more packages appear later, they should be added only when they represent genuinely separate deliverables or reusable libraries. Until then, the correct interpretation is:

- `src/` contains project source code
- `photo_processor/` contains the whole application
- `api/app/core/infra/bootstrap/config` are the layers of that application

## Architectural rule

Core math must not depend on Pillow, GUI frameworks, or filesystem side effects. Infrastructure can depend on core rules, but not the reverse.

## File design principles

Use file boundaries intentionally:

- each file should have a clear target responsibility
- the file name should describe that responsibility directly
- unrelated behavior should not be mixed into the same file
- aim to keep files under roughly `250` lines
- when a file grows beyond that size, treat it as a signal to split responsibilities
- prefer nested package structure with meaningful grouping over placing many unrelated files in a single package
