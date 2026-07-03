# Requirements

## Overview

`reqc.py` is a single Python script that cross-references requirements defined in Markdown documentation files against `REQ:` markers in target files. It detects two categories of mismatches:

- **Missing coverage**: Requirements in docs with no matching target
- **Stale targets**: `REQ:` markers in target files with no matching doc requirement

The tool is designed to be lightweight with no external dependencies, using only the Python standard library. It is intended for use in CI/CD pipelines as well as local development workflows.

## CLI Interface

```
python reqc.py --reqs <reqs_dir> --targets <targets_dir> [--all]
```

| Argument        | Required | Description                                    |
|-----------------|----------|------------------------------------------------|
| `--reqs`, `-r`  | Yes     | Path to the requirements directory (`.md`)     |
| `--targets`, `-t` | Yes   | Path to the target directory (any file type)   |
| `--all`, `-a`   | No      | Show all targets, including already-implemented|

## Exit Codes

| Code | Meaning                              |
|------|--------------------------------------|
| 0    | All requirements matched, no issues  |
| 1    | Mismatches found (missing or stale)  |
| 2    | Fatal error (e.g., duplicate reqs)   |

## ArgParser Requirements

Uses Python's `argparse` module to define and parse command-line arguments. The parser is configured with two required positional-style arguments (`--reqs`, `--targets`) and one optional flag (`--all` / `-a`).

- Accept a --reqs argument with short form -r that specifies the path to the requirements directory
- Accept a --targets argument with short form -t that specifies the path to the target directory
- Accept an --all flag with short form -a that shows implemented targets in addition to missing and stale ones

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
- End a requirements section at any sub-heading, collecting only list items that appear before sub-headings

## DocRequirementExtractor Requirements

Recursively scans the reqs directory for `.md` files, invokes the MarkdownParser on each file, and collects the results into a list of named tuples containing the requirement text and its source file path with line number.

- Scan the reqs directory recursively for files with the .md extension
- Invoke the MarkdownParser on each discovered markdown file
- Pair each extracted doc requirement text with its source file path and line number (e.g. `filename.md:221`) as a DocRequirement named tuple

## TargetRequirementExtractor Requirements

Recursively scans the target directory for all files regardless of extension. For each file, it reads the content line by line and searches for lines containing the `REQ: ` prefix. The text after the prefix is extracted as a requirement and paired with its source file path and line number.

- Scan the target directory recursively with no file extension filtering
- Search for the prefix REQ followed by a colon and a space in target files, matching case-insensitively
- Accept REQ markers in any case variation such as req, Req, REQ, or ReQ
- Extract the text after the REQ prefix as the requirement text
- Strip leading and trailing whitespace from each extracted requirement text
- Strip trailing triple quotes from REQ entries to allow inline docstring markers
- Silently ignore empty REQ entries
- Skip REQ entries that contain the keyword to filter out false flags
- Pair each extracted target requirement text with its source file path and line number (e.g. `filename.py:42`) as a TargetRequirement named tuple

## DuplicateChecker Requirements

Validates that no requirement text appears more than once across all documentation files. It receives the list of doc requirements and checks for duplicates. If any are found, it raises an error with the duplicate text and the conflicting file paths.

- Detect when the same requirement text appears in multiple documentation files
- Detect when the same requirement text appears multiple times within a single documentation file
- Raise an error with the duplicate text and all conflicting source file paths

## RequirementMatcher Requirements

Cross-references doc requirements against target requirements using exact string comparison on the requirement text. It produces three categories: missing (in docs but not in targets), implemented (in both), and stale (in targets but not in docs).

- Perform exact string comparison for matching requirements between docs and targets
- Identify missing coverage as requirements in docs with no matching target
- Identify stale targets as requirements in targets with no matching doc requirement
- Identify implemented targets as requirements that appear in both docs and targets

## ReportGenerator Requirements

Formats and prints the cross-reference results to stdout. By default it prints only missing and stale items followed by a summary. When the `--all` flag is set, it also prints implemented items.

- Output missing coverage prefixed with MISSING and include the source doc file path with line number
- Output stale targets prefixed with STALE and include the source target file path with line number
- Output a summary with counts of total requirements in docs, total in targets, missing, and stale
- Show implemented targets prefixed with IMPLEMENTED when the all flag is provided

## Main Requirements

Orchestrates the full pipeline: parses arguments, validates directories, extracts requirements from docs and targets, checks for duplicates, matches requirements, generates the report, and sets the appropriate exit code.

- Validate that the --reqs directory exists and is readable
- Validate that the --targets directory exists and is readable
- Return exit code 0 when all requirements are matched with no missing or stale targets
- Return exit code 1 when mismatches are found with missing or stale targets
- Return exit code 2 when duplicate requirement text is detected across documentation files

## Example Output

### Default output (without `--all`):

```
--- Missing (requirements with no target) ---
  [MISSING] docs/example.md:12: The system shall authenticate users
  [MISSING] docs/example.md:15: The system shall log errors

--- Stale (targets with no requirement) ---
  [STALE] tests/test_auth.py:42: The system shall support LDAP
  [STALE] tests/test_old.py:88: The system shall support OAuth

--- Summary ---
  Requirements in docs:    4
  Requirements in targets: 4
  Missing:                 2
  Stale:                   2
```

### With `--all`:

```
--- Missing (requirements with no target) ---
  [MISSING] docs/example.md:12: The system shall authenticate users

--- Implemented ---
  [IMPLEMENTED] tests/test_auth.py:28: The system shall log errors

--- Stale (targets with no requirement) ---
  [STALE] tests/test_old.py:88: The system shall support LDAP

--- Summary ---
  Requirements in docs:    2
  Requirements in targets: 2
  Missing:                 1
  Stale:                   1
  Implemented:             1
```