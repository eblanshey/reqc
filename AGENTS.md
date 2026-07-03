# reqc — Requirements Check

## Overview

`reqc.py` is a single-file Python tool (stdlib only, no external dependencies) that cross-references requirements defined in Markdown documentation files against `REQ:` markers in target files. It detects two categories of mismatches:

- **Missing coverage**: Requirements in docs with no matching target
- **Stale targets**: `REQ:` markers in target files with no matching doc requirement

## Project Structure

```
stdd/
├── reqc.py            # Single-file implementation (all components)
├── docs/
│   └── Requirements.md    # Source of truth for all requirements
├── tests/
│   ├── __init__.py
│   ├── test_argparser.py
│   ├── test_markdownparser.py
│   ├── test_docrequirementextractor.py
│   ├── test_targetrequirementextractor.py
│   ├── test_duplicatechecker.py
│   ├── test_requirementmatcher.py
│   ├── test_reportgenerator.py
│   └── test_main.py
├── pyproject.toml
└── .python-version
```

## Components in reqc.py

| Component | Purpose |
|-----------|---------|
| `ArgParser` | CLI argument parsing (`--reqs/-r`, `--targets/-t`, `--all/-a`) |
| `MarkdownParser` | Parses .md files, extracts requirements from headings containing "Requirements" or "Specifications" |
| `DocRequirementExtractor` | Recursively scans reqs/ for .md files, invokes MarkdownParser |
| `TargetRequirementExtractor` | Recursively scans targets/ for `REQ: ` markers in any file type |
| `DuplicateChecker` | Validates no duplicate requirement text across doc files |
| `RequirementMatcher` | Cross-references doc vs target requirements (exact string match) |
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

Every requirement in `docs/Requirements.md` must have a matching `REQ:` marker in the targets. Run reqc against itself to verify:

```bash
uv run python reqc.py --reqs docs --targets tests
```

This will show:
- **Missing** (requirements in docs with no target) — should be 0
- **Implemented** (requirements in both docs and targets) — should equal total doc requirements
- **Stale** (REQ markers in targets with no matching doc) — should be 0

Exit code 0 means full coverage. Exit code 1 means mismatches exist. Exit code 2 means duplicate requirements were found in docs.

## REQ: Marker Convention

Every target function must have a docstring prefixed with `REQ:` that matches the exact requirement text from `docs/Requirements.md`:

```python
def test_something(self):
    """REQ: Accept a --reqs argument with short form -r that specifies the path to the requirements directory"""
    ...
```

The `TargetRequirementExtractor` strips trailing triple quotes (`"""` or `'''`) so these can be inline docstrings.

## Implementation Rules

- Single-file implementation in `reqc.py` — no splitting into modules
- Python 3.11+ only, stdlib only (no external dependencies)
- All requirements are defined in `docs/Requirements.md` — this is the source of truth
- Every requirement in `Requirements.md` must have at least one target with a matching `REQ:` marker
- Named tuples: `DocRequirement(text, source)` and `TargetRequirement(text, source)`
- `ReportGenerator.generate()` returns a string (does not print)
- `main()` returns an exit code (does not call `sys.exit()`)