# reqc — Requirements Check

Pronounced "rexi", `reqc` is a simple single-file Python tool that keeps your requirements as the human-readable source of truth. It cross-references requirements in Markdown documentation against `REQ:` markers in target files. It works on any codebase, any language — requirements live in Markdown, and `REQ:` markers are just text in your source or tests. It catches drift between what you've specified and what you've implemented.

## How It Works

Requirements are simply bullet points under any Markdown heading that contains the word "Requirements" or "Specifications". That's it — no special syntax, no custom file formats.

You can organize them however you like. Embed them in your regular project docs, create a dedicated spec directory, or anything in between. If using Object Oriented Programming (OOP), for example, you can design your objects and specify requirements for each one. Group by object, feature, by module, by user story — `reqc` doesn't care. It just needs a heading containing "Requirements" or "Specifications" and some bullet points beneath it.

The exact text of each requirement must appear as a `REQ:` marker somewhere in your target files. Targets are typically code comments in your source, or — if you practice TDD — comments in your unit tests. This creates a spec-test-driven-development workflow:

1. Update the spec in your docs
2. Write a test with a matching `REQ:` marker
3. Implement the code to make the test pass

Every requirement has a matching test. Every test traces back to a documented requirement. Over time, this produces a codebase where documentation, tests, and implementation stay in sync.

No external dependencies. Python 3.11+, stdlib only.

## Usage

```bash
python reqc.py --reqs <reqs_dir> --targets <targets_dir> [--all]
```

| Argument        | Required | Description                                  |
|-----------------|----------|----------------------------------------------|
| `--reqs`, `-r`  | Yes     | Path to the requirements directory (`.md`)   |
| `--targets`, `-t` | Yes   | Path to the target directory (any file type) |
| `--all`, `-a`   | No      | Also show implemented (matched) targets      |

`reqc` reports two kinds of mismatches:

- **Missing coverage** — a requirement in docs with no matching `REQ:` marker in targets
- **Stale targets** — a `REQ:` marker in targets with no matching requirement in docs

## Example

**docs/auth.md:**

```markdown
## Authentication Requirements

- Login must support OAuth2
- Login must support API key authentication
- Sessions must expire after 30 minutes of inactivity
- Password reset tokens must expire after 15 minutes
```

**tests/test_auth.py:**

```python
class TestAuth:
    def test_login_oauth2(self):
        """REQ: Login must support OAuth2"""
        # ...

    def test_login_api_key(self):
        """REQ: Login must support API key authentication"""
        # ...

    def test_session_expiry(self):
        """REQ: Sessions must expire after 30 minutes of inactivity"""
        # ...
```

```bash
$ python reqc.py --reqs docs --targets tests
--- Missing (requirements with no target) ---
  [MISSING] docs/auth.md: Password reset tokens must expire after 15 minutes

--- Summary ---
  Requirements:  4
  Targets:       3
  Missing:       1
  Stale:         0
```

Exit code 1 — missing coverage detected.

`reqc` uses itself. The requirements in [docs/Requirements.md](docs/Requirements.md) are enforced by `REQ:` markers in the [tests/](tests/) directory. Run `python reqc.py --reqs docs --targets tests` to verify full coverage.

## AI Agent Instructions

`reqc` works well with AI agents. Add the following to your AGENTS.md file. Customize it to your needs.

> Run `reqc --reqs <reqs_dir> --targets <targets_dir>` after writing or modifying requirements to verify coverage. Every requirement listed under a "Requirements" or "Specifications" heading in your Markdown docs must have a corresponding `REQ:` marker in a target file with matching text. This workflow enforces specs-first development: always update requirements in docs before writing targets, since documentation is the source of truth. If the tool reports missing coverage, add target files with `REQ: <exact requirement text>` markers. The `REQ:` marker must live in real content that exercises the specified behaviour — a marker alone is not sufficient. If the tool reports stale targets, either add the requirement back to docs if it's still valid, or delete the target and corresponding feature if the functionality is no longer needed.

## Exit Codes

| Code | Meaning                                    |
|------|--------------------------------------------|
| 0    | All requirements matched, no issues        |
| 1    | Mismatches found (missing or stale)        |
| 2    | Fatal error (e.g., duplicate requirements) |

## Skipping False Positives

If a `REQ:` marker appears in fixture data (string literals) rather than as an actual requirement marker, append `req-ignore` to the line to skip it:

```python
f.write('REQ: Some fixture data\n')  # req-ignore
```

## Running Tests

```bash
uv run pytest tests/ -v
```

## Verifying Requirements Coverage

Run reqc against itself:

```bash
uv run python reqc.py --reqs docs --targets tests
```

Exit code 0 means full coverage.