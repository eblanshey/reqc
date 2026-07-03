"""STDD - Spec Test Driven Development tool."""

import argparse
import os
import re
import sys
from collections import namedtuple

DocRequirement = namedtuple('DocRequirement', ['text', 'source'])
TestRequirement = namedtuple('TestRequirement', ['text', 'source'])


class ArgParser:
    def parse_args(self, args=None):
        parser = argparse.ArgumentParser(
            description='STDD - Spec Test Driven Development tool',
            epilog=(
                'Cross-references requirements in Markdown documentation against REQ: markers\n'
                'in test files to detect missing tests and stale test coverage.\n'
                '\n'
                'Output:\n'
                '  [MISSING]   Requirements in docs with no matching test\n'
                '  [STALE]     REQ markers in tests with no matching doc requirement\n'
                '  [IMPLEMENTED]  Matched requirements (shown with --all/-a)\n'
                '  Summary section with counts for each category\n'
                '\n'
                'Examples:\n'
                '  stdd.py -d docs -t tests\n'
                '  stdd.py --docs docs --tests tests --all\n'
                '\n'
                'Exit codes:\n'
                '  0  All requirements matched, no issues\n'
                '  1  Mismatches found (missing or stale tests)\n'
                '  2  Fatal error (duplicate requirements in docs)'
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument('--docs', '-d', required=False, help='Path to the documentation directory containing .md files')
        parser.add_argument('--tests', '-t', required=False, help='Path to the test directory to scan for REQ: markers')
        parser.add_argument('--all', '-a', action='store_true', default=False, help='Also show implemented (matched) tests in output')
        parsed = parser.parse_args(args)
        if not parsed.docs and not parsed.tests:
            parser.print_help()
            sys.exit(0)
        if not parsed.docs or not parsed.tests:
            parser.error('the following arguments are required: --docs/-d and --tests/-t')
        return parsed


class MarkdownParser:
    def parse(self, content: str) -> list[str]:
        lines = content.split('\n')
        requirements = []
        in_requirements = False
        in_code_block = False
        req_heading_level = 0

        for line in lines:
            stripped = line.strip()
            if stripped == '```':
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            heading_match = re.match(r'^(#{1,6})\s', line)
            if heading_match:
                level = len(heading_match.group(1))
                if 'Requirements' in line or 'Specifications' in line:
                    in_requirements = True
                    req_heading_level = level
                elif in_requirements and level <= req_heading_level:
                    in_requirements = False
                continue

            if in_requirements:
                match = re.match(r'^(\s*)[-*+]\s+(.*)', line)
                if match:
                    text = match.group(2).strip()
                    if text and text not in ('-', '*', '+'):
                        requirements.append(text)

        return requirements


class DocRequirementExtractor:
    def __init__(self, parser=None):
        self.parser = parser if parser is not None else MarkdownParser()

    def extract(self, docs_dir: str) -> list[DocRequirement]:
        requirements = []
        for root, _dirs, files in os.walk(docs_dir):
            for filename in files:
                if filename.endswith('.md'):
                    filepath = os.path.join(root, filename)
                    with open(filepath, 'r') as f:
                        content = f.read()
                    parsed = self.parser.parse(content)
                    for text in parsed:
                        requirements.append(DocRequirement(text=text, source=filepath))
        return requirements


class TestRequirementExtractor:
    def extract(self, tests_dir: str) -> list[TestRequirement]:
        results = []
        for root, dirs, files in os.walk(tests_dir):
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for filename in files:
                filepath = os.path.join(root, filename)
                with open(filepath, "r", errors="ignore") as f:
                    for line in f:
                        lower = line.lower()
                        if "req: " in lower:
                            idx = lower.index("req: ")
                            text = line[idx + 5:].strip()
                            text = text.removesuffix('"""').removesuffix("'''")
                            if text and 'req-ignore' not in text:
                                results.append(TestRequirement(text=text, source=filepath))
        return results


class DuplicateRequirementError(Exception):
    """Raised when duplicate requirements are detected."""
    pass


class DuplicateChecker:
    def check(self, requirements: list[DocRequirement]) -> None:
        seen = {}
        for req in requirements:
            if req.text in seen:
                seen[req.text].append(req.source)
            else:
                seen[req.text] = [req.source]
        for text, sources in seen.items():
            if len(sources) > 1:
                raise DuplicateRequirementError(
                    f"Duplicate requirement: {text!r} found in {sources}"
                )


class RequirementMatcher:
    def match(self, doc_reqs, test_reqs):
        """Cross-reference doc and test requirements.

        Returns dict with keys:
        - 'missing': list of DocRequirement (in docs, no matching test)
        - 'implemented': list of TestRequirement (in both docs and tests)
        - 'stale': list of TestRequirement (in tests, no matching doc)
        """
        test_texts = {tr.text for tr in test_reqs}
        doc_texts = {dr.text for dr in doc_reqs}
        missing = [dr for dr in doc_reqs if dr.text not in test_texts]
        implemented = [tr for tr in test_reqs if tr.text in doc_texts]
        stale = [tr for tr in test_reqs if tr.text not in doc_texts]
        return {'missing': missing, 'implemented': implemented, 'stale': stale}


class ReportGenerator:
    def generate(self, missing, implemented, stale, total_docs, total_tests, all_flag=False):
        lines = []
        first_section = True

        if missing:
            if not first_section:
                lines.append("")
            lines.append("--- Missing Tests (requirements in docs with no test) ---")
            for req in missing:
                lines.append(f"  [MISSING] {req.source}: {req.text}")
            first_section = False

        if all_flag and implemented:
            if not first_section:
                lines.append("")
            lines.append("--- Implemented Tests ---")
            for req in implemented:
                lines.append(f"  [IMPLEMENTED] {req.source}: {req.text}")
            first_section = False

        if stale:
            if not first_section:
                lines.append("")
            lines.append("--- Stale Tests (tests with no matching requirement) ---")
            for req in stale:
                lines.append(f"  [STALE] {req.source}: {req.text}")
            first_section = False

        lines.append("")
        lines.append("--- Summary ---")
        lines.append(f"  Requirements in docs:  {total_docs}")
        lines.append(f"  Requirements in tests: {total_tests}")
        lines.append(f"  Missing tests:         {len(missing)}")
        lines.append(f"  Stale tests:           {len(stale)}")
        if all_flag:
            lines.append(f"  Implemented tests:     {len(implemented)}")
        return "\n".join(lines) + "\n"


def main(argv=None):
    parser = ArgParser()
    args = parser.parse_args(argv)

    if not os.path.isdir(args.docs):
        raise FileNotFoundError(f"Docs directory not found: {args.docs}")

    if not os.path.isdir(args.tests):
        raise FileNotFoundError(f"Tests directory not found: {args.tests}")

    dre = DocRequirementExtractor()
    doc_reqs = dre.extract(args.docs)

    tre = TestRequirementExtractor()
    test_reqs = tre.extract(args.tests)

    dc = DuplicateChecker()
    try:
        dc.check(doc_reqs)
    except DuplicateRequirementError as e:
        print(f"ERROR: {e}")
        return 2

    rm = RequirementMatcher()
    result = rm.match(doc_reqs, test_reqs)

    rg = ReportGenerator()
    report = rg.generate(
        result['missing'], result['implemented'], result['stale'],
        len(doc_reqs), len(test_reqs), args.all
    )
    print(report)

    if result['missing'] or result['stale']:
        return 1
    return 0


def main_cli():
    sys.exit(main())


if __name__ == "__main__":
    main_cli()