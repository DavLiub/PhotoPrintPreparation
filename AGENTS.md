# Repository Guidelines

## Project Structure & Module Organization

This repository is currently document-focused. The primary source asset lives in [`source doc/PhotoProject_expanded.docx`](C:\Users\dliubinskii\Documents\PhotoPrintPreparation\source%20doc\PhotoProject_expanded.docx). Keep new working materials under `source doc/` unless a clearer top-level folder becomes necessary.

The repository also has a maintainer documentation area under [`doc/`](C:\Users\dliubinskii\Documents\PhotoPrintPreparation\doc), which should explain the current implementation, target architecture, algorithms, and alignment gaps between the codebase and the source specification.

## Source of Truth

Use [`source doc/PhotoProject_expanded.docx`](C:\Users\dliubinskii\Documents\PhotoPrintPreparation\source%20doc\PhotoProject_expanded.docx) as the main product source. It defines the current application scope and behavior, including supported image formats, output defaults, frame-fitting modes, orientation rules, EXIF handling, file-size limits, and batch-processing flow.

If repository files are added later and they conflict with the document, treat the `.docx` as authoritative until the spec is updated.

Use [`doc/README.md`](C:\Users\dliubinskii\Documents\PhotoPrintPreparation\doc\README.md) as the working entry point for implementation documentation. Update `doc/` when `src/` changes, and explicitly document any mismatch between current code and the `.docx` spec instead of silently drifting.

For `src/`, prefer a layered direction built around `api`, `app`, `core`, `infra`, plus `bootstrap` and `config` when startup wiring and runtime defaults become substantial.

If supporting files are added, group them by purpose:

- `source doc/` for editable source documents
- `doc/` for repository-maintained project documentation that should track the real codebase
- `assets/` for images or print references
- `exports/` for generated PDFs or final delivery files

Avoid mixing raw source files and generated outputs in the same directory.

## Build, Test, and Development Commands

There is no automated build or test pipeline yet. Use lightweight repository checks before submitting changes:

- `git status --short` to confirm intended file changes
- `git diff --stat` to review scope
- `git add AGENTS.md` or `git add "source doc/*"` to stage updates explicitly

When exports are introduced later, document the exact generation command here.

## Coding Style & Naming Conventions

Use clear, stable names for files and folders. Prefer descriptive names with spaces only when existing repository conventions already use them, as in `source doc/`. For new files, prefer one convention and keep it consistent, for example `print-layout-v2.pdf` or `cover_sheet_notes.md`.

For source code structure:

- each file should be purpose-focused and named after its actual responsibility
- do not mix unrelated functionality in one file
- prefer splitting files before they grow beyond roughly 250 lines
- if a file exceeds that size, treat it as a candidate for decomposition
- prefer deeper, well-grouped package structure over dumping many files into one package

For Markdown files:

- Use `#` headings with short sections
- Keep lines readable and instructions specific
- Prefer bullet lists for procedures and checklists

## Testing Guidelines

Because this project does not yet include automated tests, validation is manual:

- open edited documents and confirm formatting is intact
- verify linked assets resolve correctly
- review generated print/export output before committing

If scripts are added later, place tests beside them or under a dedicated `tests/` directory and document the run command here.

## Commit & Pull Request Guidelines

The repository has no commit history yet, so use a simple convention from the start: imperative, scope-first commit messages such as `docs: add contributor guide` or `assets: update print source document`.

Pull requests should include:

- a short summary of changed files
- the reason for the change
- screenshots or exported previews when visual layout changed
- any manual validation performed
