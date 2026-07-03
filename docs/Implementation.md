# Implementation Plan: STDD (Spec Test Driven Development)

## Overview

`stdd.py` is a single Python script that cross-references requirements defined in Markdown documentation files against `REQ:` markers in a test directory. It detects two categories of mismatches:

- **Missing tests**: Requirements in docs with no matching test
- **Stale tests**: `REQ:` markers in test files with no matching doc requirement

The tool is designed to be lightweight with no external dependencies, using only the Python standard library. It is intended for use in CI/CD pipelines as well as local development workflows.

## CLI Interface

```
python stdd.py --docs <docs_dir> --tests <tests_dir> [--all]
```

| Argument      | Required | Description                                    |
|---------------|----------|------------------------------------------------|
| `--docs`, `-d` | Yes     | Path to the documentation directory (`.md`)    |
| `--tests`, `-t` | Yes    | Path to the test directory (any file type)     |
| `--all`, `-a` | No     | Show all tests, including already-implemented  |

## Exit Codes

| Code | Meaning                              |
|------|--------------------------------------|
| 0    | All requirements matched, no issues  |
| 1    | Mismatches found (missing or stale)  |
| 2    | Fatal error (e.g., duplicate reqs)   |

## ArgParser Requirements

Uses Python's `argparse` module to define and parse command-line arguments. The parser is configured with two required positional-style arguments (`--docs`, `--tests`) and one optional flag (`--all` / `-a`).

- Accept a --docs argument with short form -d that specifies the path to the documentation directory
- Accept a --tests argument with short form -t that specifies the path to the test directory
- Accept an --all flag with short form -a that shows implemented tests in addition to missing and stale ones

## MarkdownParser Requirements

Parses a single Markdown file and extracts requirement texts from sections whose headings contain `Requirements` or `Specifications`. It tracks heading levels to determine section boundaries, skips fenced code blocks and blockquotes, and returns a list of raw requirement strings.

- Detect headings that contain the substring Requirements or Specifications with a case-sensitive match
- Match headings at any level from H1 through H6
- Allow the substring Requirements or Specifications to appear anywhere within the heading text
- Extract unordered list items from a requirements section as individual requirements
- Support unordered list markers using a dash, an asterisk, or a plus sign
- Treat all list items as separate requirements regardless of nesting depth
- Treat each line within a list item independently without joining multiline content
- Strip leading and trailing whitespace from each requirement text
- Preserve raw markdown formatting in requirement text
- Silently ignore empty list items
- Skip content inside fenced code blocks
- Skip content inside blockquotes
- End a requirements section at the next heading of equal or higher level

## DocRequirementExtractor Requirements

Recursively scans the docs directory for `.md` files, invokes the MarkdownParser on each file, and collects the results into a list of named tuples containing the requirement text and its source file path.

- Scan the docs directory recursively for files with the .md extension
- Invoke the MarkdownParser on each discovered markdown file
- Pair each extracted doc requirement text with its source file path as a DocRequirement named tuple

## TestRequirementExtractor Requirements

Recursively scans the test directory for all files regardless of extension. For each file, it reads the content line by line and searches for lines containing the `REQ: ` prefix. The text after the prefix is extracted as a requirement and paired with its source file path.

- Scan the test directory recursively with no file extension filtering
- Search for the exact prefix REQ followed by a colon and a space in test files
- Extract the text after the REQ prefix as the requirement text
- Strip leading and trailing whitespace from each extracted requirement text
- Strip trailing triple quotes from REQ entries to allow inline docstring markers
- Silently ignore empty REQ entries
- Pair each extracted test requirement text with its source file path as a TestRequirement named tuple

## DuplicateChecker Requirements

Validates that no requirement text appears more than once across all documentation files. It receives the list of doc requirements and checks for duplicates. If any are found, it raises an error with the duplicate text and the conflicting file paths.

- Detect when the same requirement text appears in multiple documentation files
- Detect when the same requirement text appears multiple times within a single documentation file
- Raise an error with the duplicate text and all conflicting source file paths

## RequirementMatcher Requirements

Cross-references doc requirements against test requirements using exact string comparison on the requirement text. It produces three categories: missing (in docs but not in tests), implemented (in both), and stale (in tests but not in docs).

- Perform exact string comparison for matching requirements between docs and tests
- Identify missing tests as requirements in docs with no matching test
- Identify stale tests as requirements in tests with no matching doc requirement
- Identify implemented tests as requirements that appear in both docs and tests

## ReportGenerator Requirements

Formats and prints the cross-reference results to stdout. By default it prints only missing and stale items followed by a summary. When the `--all` flag is set, it also prints implemented items.

- Output missing tests prefixed with MISSING and include the source doc file path
- Output stale tests prefixed with STALE and include the source test file path
- Output a summary with counts of total requirements in docs, total in tests, missing, and stale
- Show implemented tests prefixed with IMPLEMENTED when the all flag is provided

## Main Requirements

Orchestrates the full pipeline: parses arguments, validates directories, extracts requirements from docs and tests, checks for duplicates, matches requirements, generates the report, and sets the appropriate exit code.

- Validate that the --docs directory exists and is readable
- Validate that the --tests directory exists and is readable
- Return exit code 0 when all requirements are matched with no missing or stale tests
- Return exit code 1 when mismatches are found with missing or stale tests
- Return exit code 2 when duplicate requirement text is detected across documentation files

## Example Output

### Default output (without `--all`):

```
--- Missing Tests (requirements in docs with no test) ---
  [MISSING] docs/example.md: The system shall authenticate users
  [MISSING] docs/example.md: The system shall log errors

--- Stale Tests (tests with no matching requirement) ---
  [STALE] tests/test_auth.py: The system shall support LDAP
  [STALE] tests/test_old.py: The system shall support OAuth

--- Summary ---
  Requirements in docs:  4
  Requirements in tests: 4
  Missing tests:         2
  Stale tests:           2
```

### With `--all`:

```
--- Missing Tests (requirements in docs with no test) ---
  [MISSING] docs/example.md: The system shall authenticate users

--- Implemented Tests ---
  [IMPLEMENTED] tests/test_auth.py: The system shall log errors

--- Stale Tests (tests with no matching requirement) ---
  [STALE] tests/test_old.py: The system shall support LDAP

--- Summary ---
  Requirements in docs:  2
  Requirements in tests: 2
  Missing tests:         1
  Stale tests:           1
  Implemented tests:     1
```