"""reqcheck - Requirements coverage audit tool."""

import argparse
import os
import re
import sys
from collections import namedtuple

DocRequirement = namedtuple('DocRequirement', ['text', 'source'])
TargetRequirement = namedtuple('TargetRequirement', ['text', 'source'])


class ArgParser:
    def parse_args(self, args=None):
        parser = argparse.ArgumentParser(
            description='reqcheck - Requirements coverage audit tool',
            epilog=(
                'Cross-references requirements in Markdown documentation against REQ: markers\n'
                'in target files to detect missing coverage and stale targets.\n'
                '\n'
                'Output:\n'
                '  [MISSING]   Requirements in docs with no matching target\n'
                '  [STALE]     REQ markers in targets with no matching doc requirement\n'
                '  [IMPLEMENTED]  Matched requirements (shown with --all/-a)\n'
                '  Summary section with counts for each category\n'
                '\n'
                'Ignoring target requirements:\n'
                '  Include req-ignore in a REQ: line to skip it, e.g.:\n'
                '    REQ: some requirement text (req-ignore)\n'
                '\n'
                'Examples:\n'
                '  reqcheck.py -r docs -t tests\n'
                '  reqcheck.py --reqs docs --targets tests --all\n'
                '\n'
                'Exit codes:\n'
                '  0  All requirements matched, no issues\n'
                '  1  Mismatches found (missing or stale targets)\n'
                '  2  Fatal error (duplicate requirements in docs)'
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument('--reqs', '-r', required=False, help='Path to the requirements directory containing .md files')
        parser.add_argument('--targets', '-t', required=False, help='Path to the target directory to scan for REQ: markers')
        parser.add_argument('--all', '-a', action='store_true', default=False, help='Also show implemented (matched) targets in output')
        parsed = parser.parse_args(args)
        if not parsed.reqs and not parsed.targets:
            parser.print_help()
            sys.exit(0)
        if not parsed.reqs or not parsed.targets:
            parser.error('the following arguments are required: --reqs/-r and --targets/-t')
        return parsed


class MarkdownParser:
    def parse(self, content: str) -> list[tuple[str, int]]:
        lines = content.split('\n')
        requirements = []
        in_requirements = False
        in_code_block = False
        req_heading_level = 0

        for i, line in enumerate(lines):
            line_num = i + 1
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
                elif in_requirements:
                    in_requirements = False
                continue

            if in_requirements:
                match = re.match(r'^(\s*)[-*+]\s+(.*)', line)
                if match:
                    text = match.group(2).strip()
                    if text and text not in ('-', '*', '+'):
                        requirements.append((text, line_num))

        return requirements


class DocRequirementExtractor:
    def __init__(self, parser=None):
        self.parser = parser if parser is not None else MarkdownParser()

    def extract(self, reqs_dir: str) -> list[DocRequirement]:
        requirements = []
        for root, _dirs, files in os.walk(reqs_dir):
            for filename in files:
                if filename.endswith('.md'):
                    filepath = os.path.join(root, filename)
                    with open(filepath, 'r') as f:
                        content = f.read()
                    parsed = self.parser.parse(content)
                    for text, line_num in parsed:
                        source = f"{filepath}:{line_num}"
                        requirements.append(DocRequirement(text=text, source=source))
        return requirements


class TargetRequirementExtractor:
    def extract(self, targets_dir: str) -> list[TargetRequirement]:
        results = []
        for root, dirs, files in os.walk(targets_dir):
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for filename in files:
                filepath = os.path.join(root, filename)
                with open(filepath, "r", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        lower = line.lower()
                        if "req: " in lower:
                            idx = lower.index("req: ")
                            text = line[idx + 5:].strip()
                            text = text.removesuffix('"""').removesuffix("'''")
                            if text and 'req-ignore' not in text:
                                source = f"{filepath}:{line_num}"
                                results.append(TargetRequirement(text=text, source=source))
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
    def match(self, doc_reqs, target_reqs):
        """Cross-reference doc and target requirements.

        Returns dict with keys:
        - 'missing': list of DocRequirement (in docs, no matching target)
        - 'implemented': list of TargetRequirement (in both docs and targets)
        - 'stale': list of TargetRequirement (in targets, no matching doc)
        """
        target_texts = {tr.text for tr in target_reqs}
        doc_texts = {dr.text for dr in doc_reqs}
        missing = [dr for dr in doc_reqs if dr.text not in target_texts]
        implemented = [tr for tr in target_reqs if tr.text in doc_texts]
        stale = [tr for tr in target_reqs if tr.text not in doc_texts]
        return {'missing': missing, 'implemented': implemented, 'stale': stale}


class ReportGenerator:
    def generate(self, missing, implemented, stale, total_reqs, total_targets, all_flag=False):
        lines = []
        first_section = True

        if missing:
            if not first_section:
                lines.append("")
            lines.append("--- Missing (requirements with no target) ---")
            for req in missing:
                lines.append(f"  [MISSING] {req.source}: {req.text}")
            first_section = False

        if all_flag and implemented:
            if not first_section:
                lines.append("")
            lines.append("--- Implemented ---")
            for req in implemented:
                lines.append(f"  [IMPLEMENTED] {req.source}: {req.text}")
            first_section = False

        if stale:
            if not first_section:
                lines.append("")
            lines.append("--- Stale (targets with no matching requirement) ---")
            for req in stale:
                lines.append(f"  [STALE] {req.source}: {req.text}")
            first_section = False

        if not first_section:
            lines.append("")

        lines.append("--- Summary ---")
        lines.append(f"  Requirements:  {total_reqs}")
        lines.append(f"  Targets:       {total_targets}")
        lines.append(f"  Missing:       {len(missing)}")
        lines.append(f"  Stale:         {len(stale)}")
        if all_flag:
            lines.append(f"  Implemented:   {len(implemented)}")
        return "\n".join(lines) + "\n"


def main(argv=None):
    parser = ArgParser()
    args = parser.parse_args(argv)

    if not os.path.isdir(args.reqs):
        raise FileNotFoundError(f"Reqs directory not found: {args.reqs}")

    if not os.path.isdir(args.targets):
        raise FileNotFoundError(f"Targets directory not found: {args.targets}")

    dre = DocRequirementExtractor()
    doc_reqs = dre.extract(args.reqs)

    tre = TargetRequirementExtractor()
    target_reqs = tre.extract(args.targets)

    dc = DuplicateChecker()
    try:
        dc.check(doc_reqs)
    except DuplicateRequirementError as e:
        print(f"ERROR: {e}")
        return 2

    rm = RequirementMatcher()
    result = rm.match(doc_reqs, target_reqs)

    rg = ReportGenerator()
    report = rg.generate(
        result['missing'], result['implemented'], result['stale'],
        len(doc_reqs), len(target_reqs), args.all
    )
    print(report)

    if result['missing'] or result['stale']:
        return 1
    return 0


def main_cli():
    sys.exit(main())


if __name__ == "__main__":
    main_cli()