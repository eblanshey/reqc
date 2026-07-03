# STDD - Spec Test Driven Development

## Overview

`stdd.py` is a single-file Python tool (stdlib only, no external dependencies) that cross-references requirements defined in Markdown documentation files against `REQ:` markers in a test directory. It detects two categories of mismatches:

- **Missing tests**: Requirements in docs with no matching test
- **Stale tests**: `REQ:` markers in test files with no matching doc requirement

## Project Structure

```
stdd/
├── stdd.py              # Single-file implementation (all components)
├── docs/
│   └── Requirements.md  # Source of truth for all requirements
├── tests/
│   ├── __init__.py
│   ├── test_argparser.py
│   ├── test_markdownparser.py
│   ├── test_docrequirementextractor.py
│   ├── test_testrequirementextractor.py
│   ├── test_duplicatechecker.py
│   ├── test_requirementmatcher.py
│   ├── test_reportgenerator.py
│   └── test_main.py
├── pyproject.toml
└── .python-version
```

## Components in stdd.py

| Component | Purpose |
|-----------|---------|
| `ArgParser` | CLI argument parsing (`--docs/-d`, `--tests/-t`, `--all/-a`) |
| `MarkdownParser` | Parses .md files, extracts requirements from headings containing "Requirements" or "Specifications" |
| `DocRequirementExtractor` | Recursively scans docs/ for .md files, invokes MarkdownParser |
| `TestRequirementExtractor` | Recursively scans tests/ for `REQ: ` markers in any file type |
| `DuplicateChecker` | Validates no duplicate requirement text across doc files |
| `RequirementMatcher` | Cross-references doc vs test requirements (exact string match) |
| `ReportGenerator` | Formats output (missing/stale/implemented + summary) |
| `main()` | Orchestrates pipeline, returns exit code 0/1/2 |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All requirements matched, no issues |
| 1 | Mismatches found (missing or stale) |
| 2 | Fatal error (duplicate requirements in docs) |

## Running Tests

```bash
uv run pytest tests/ -v
```

## Verifying Requirements Coverage

Every requirement in `docs/Requirements.md` must have a matching `REQ:` docstring in the tests. Run STDD against itself to verify:

```bash
uv run python stdd.py --docs docs --tests tests
```

This will show:
- **Missing tests** (requirements in docs with no test) — should be 0
- **Implemented tests** (requirements in both docs and tests) — should equal total doc requirements
- **Stale tests** (REQ markers in tests with no matching doc) — should be 0

Exit code 0 means full coverage. Exit code 1 means mismatches exist. Exit code 2 means duplicate requirements were found in docs.

## REQ: Docstring Convention

Every test function must have a docstring prefixed with `REQ:` that matches the exact requirement text from `docs/Requirements.md`:

```python
def test_something(self):
    """REQ: Accept a --docs argument with short form -d that specifies the path to the documentation directory"""
    ...
```

The `TestRequirementExtractor` strips trailing triple quotes (`"""` or `'''`) so these can be inline docstrings.

## Implementation Rules

- Single-file implementation in `stdd.py` — no splitting into modules
- Python 3.11+ only, stdlib only (no external dependencies)
- All requirements are defined in `docs/Requirements.md` — this is the source of truth
- Every requirement in `Requirements.md` must have at least one test with a matching `REQ:` docstring
- Named tuples: `DocRequirement(text, source)` and `TestRequirement(text, source)`
- `ReportGenerator.generate()` returns a string (does not print)
- `main()` returns an exit code (does not call `sys.exit()`)