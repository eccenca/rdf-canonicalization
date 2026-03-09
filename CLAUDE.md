# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python library for RDF graph canonicalization and signing/verification. Package name: `graph-sign-and-verify-c4gai`. Main module: `graph_sign_and_verify_c4gai/`.

## Commands

This project uses [Task](https://taskfile.dev/) as the task runner and [Poetry](https://python-poetry.org/) for dependency management.

```bash
task                    # List all available tasks
poetry install          # Install dependencies

task check              # Run full test suite (linters + pytest)
task check:pytest       # Run unit tests only
task check:linters      # Run all linters (ruff, mypy, deptry, trivy)
task check:ruff         # Ruff lint + format check
task check:mypy         # Type checking
task format:fix         # Auto-format and fix lint issues
task build              # Build wheel/tarball
```

Run a single test file:
```bash
poetry run pytest tests/path/to/test_file.py
```

Run a single test by name:
```bash
poetry run pytest -k "test_name"
```

## Architecture

### Core Modules (`graph_sign_and_verify_c4gai/`)

**`rdf_canonicalization.py`** — Implements the RDFC-1.0 RDF Dataset Normalization algorithm:
- `IdentifierIssuer`: Assigns deterministic identifiers (`c14n0`, `c14n1`, ...) to blank nodes
- `RdfCanonicalization`: Main class; takes an `rdflib.Graph` and optional `max_run_time`
  - `normalize` (property): runs the full pipeline and returns canonical N-Triples string
  - Pipeline: `collect_blank_nodes()` → `issue_canonical_ids()` (simple/first-degree hashing) → `issue_n_degree_ids()` (for complex graphs with hash collisions) → `serialize_normalized_graph()`
  - Uses SHA-256 for hashing, permutation-based disambiguation for colliding blank node hashes

**`graphsignature.py`** — Simpler canonicalization + RSA signing/verification:
- `canonicalize_rdf(graph)`: serialize to N-Triples and sort lines (simpler than RDFC-1.0)
- `hash_rdf(canonical)`: SHA-256 of the canonical string
- `generate_key_pair()`: RSA-2048 key generation
- `sign_hash(private_key, hash)` / `verify_signature(public_key, hash, sig)`: RSA-PSS with SHA-256

### Tests (`tests/`)

- `tests/rdfc10/`: RDFC-1.0 test vectors (`testNNN-in.nq` input, `testNNN-rdfc10.nq` expected output, optional `testNNN-rdfc10map.json` blank node mapping)

### Examples (`examples/`)

- `graphsignature_example.py`: End-to-end sign/verify workflow using `graphsignature.py`
- `rdf_canonicalization_example.py`: Canonicalization using `RdfCanonicalization`
- `sign_example.py`: Basic RDF serialization to sorted N-Triples

## Known Limitations

The `issue_n_degree_ids()` path in `rdf_canonicalization.py` is non-deterministic due to Python set iteration order when multiple blank nodes have colliding first-degree hashes. This causes ~40 W3C test vectors (see `_KNOWN_FAILING` in `tests/test_rdf_canonicalization.py`) to be marked `xfail(strict=False)` — they may pass or fail depending on run order. This is a known bug, not a test infrastructure issue.

## Code Style

- Ruff with `select = ["ALL"]` — see `pyproject.toml` for ignored rules
- Line length: 100 characters
- Python ≥ 3.13 required
- Versioning: semantic versioning via `poetry-dynamic-versioning` (git tags)
- Changelog: Keep A Changelog format
- Use `pre-commit` to catch lint/format issues before committing