from collections import namedtuple
from reqc import ReportGenerator

DocRequirement = namedtuple('DocRequirement', ['text', 'source'])


class TestReportGeneratorMissing:
    def test_missing_shown_with_prefix_and_source(self):
        """REQ: Output missing coverage prefixed with MISSING and include the source doc file path"""
        gen = ReportGenerator()
        missing = [
            DocRequirement(text="The system shall authenticate users", source="docs/example.md"),
            DocRequirement(text="The system shall log errors", source="docs/example.md"),
        ]
        result = gen.generate(
            missing=missing,
            implemented=[],
            stale=[],
            total_reqs=2,
            total_targets=0,
            all_flag=False,
        )
        assert "--- Missing (requirements with no target) ---" in result
        assert "[MISSING] docs/example.md: The system shall authenticate users" in result
        assert "[MISSING] docs/example.md: The system shall log errors" in result


class TestReportGeneratorStale:
    def test_stale_shown_with_prefix_and_source(self):
        """REQ: Output stale targets prefixed with STALE and include the source target file path"""
        gen = ReportGenerator()
        TargetRequirement = namedtuple('TargetRequirement', ['text', 'source'])
        stale = [
            TargetRequirement(text="The system shall support LDAP", source="tests/test_auth.py"),
            TargetRequirement(text="The system shall support OAuth", source="tests/test_old.py"),
        ]
        result = gen.generate(
            missing=[],
            implemented=[],
            stale=stale,
            total_reqs=0,
            total_targets=2,
            all_flag=False,
        )
        assert "--- Stale (targets with no matching requirement) ---" in result
        assert "[STALE] tests/test_auth.py: The system shall support LDAP" in result
        assert "[STALE] tests/test_old.py: The system shall support OAuth" in result

    def test_all_categories_with_exact_format(self):
        """REQ: Output a summary with counts of total requirements in docs, total in targets, missing, and stale"""
        gen = ReportGenerator()
        TargetRequirement = namedtuple('TargetRequirement', ['text', 'source'])
        missing = [
            DocRequirement(text="The system shall authenticate users", source="docs/example.md"),
            DocRequirement(text="The system shall log errors", source="docs/example.md"),
        ]
        stale = [
            TargetRequirement(text="The system shall support LDAP", source="tests/test_auth.py"),
            TargetRequirement(text="The system shall support OAuth", source="tests/test_old.py"),
        ]
        result = gen.generate(
            missing=missing,
            implemented=[],
            stale=stale,
            total_reqs=4,
            total_targets=4,
            all_flag=False,
        )
        expected = (
            "--- Missing (requirements with no target) ---\n"
            "  [MISSING] docs/example.md: The system shall authenticate users\n"
            "  [MISSING] docs/example.md: The system shall log errors\n"
            "\n"
            "--- Stale (targets with no matching requirement) ---\n"
            "  [STALE] tests/test_auth.py: The system shall support LDAP\n"
            "  [STALE] tests/test_old.py: The system shall support OAuth\n"
            "\n"
            "--- Summary ---\n"
            "  Requirements:  4\n"
            "  Targets:       4\n"
            "  Missing:       2\n"
            "  Stale:         2\n"
        )
        assert result == expected


class TestReportGeneratorAllFlag:
    def test_all_flag_shows_implemented_section(self):
        """REQ: Show implemented targets prefixed with IMPLEMENTED when the all flag is provided"""
        gen = ReportGenerator()
        TargetRequirement = namedtuple('TargetRequirement', ['text', 'source'])
        missing = [
            DocRequirement(text="The system shall authenticate users", source="docs/example.md"),
        ]
        implemented = [
            TargetRequirement(text="The system shall log errors", source="tests/test_auth.py"),
        ]
        stale = [
            TargetRequirement(text="The system shall support LDAP", source="tests/test_old.py"),
        ]
        result = gen.generate(
            missing=missing,
            implemented=implemented,
            stale=stale,
            total_reqs=2,
            total_targets=2,
            all_flag=True,
        )
        expected = (
            "--- Missing (requirements with no target) ---\n"
            "  [MISSING] docs/example.md: The system shall authenticate users\n"
            "\n"
            "--- Implemented ---\n"
            "  [IMPLEMENTED] tests/test_auth.py: The system shall log errors\n"
            "\n"
            "--- Stale (targets with no matching requirement) ---\n"
            "  [STALE] tests/test_old.py: The system shall support LDAP\n"
            "\n"
            "--- Summary ---\n"
            "  Requirements:  2\n"
            "  Targets:       2\n"
            "  Missing:       1\n"
            "  Stale:         1\n"
            "  Implemented:   1\n"
        )
        assert result == expected

    def test_all_flag_false_hides_implemented(self):
        gen = ReportGenerator()
        TargetRequirement = namedtuple('TargetRequirement', ['text', 'source'])
        implemented = [
            TargetRequirement(text="The system shall log errors", source="tests/test_auth.py"),
        ]
        result = gen.generate(
            missing=[],
            implemented=implemented,
            stale=[],
            total_reqs=1,
            total_targets=1,
            all_flag=False,
        )
        assert "[IMPLEMENTED]" not in result
        assert "Implemented" not in result

    def test_all_flag_exact_format_from_spec(self):
        """REQ: Show implemented targets prefixed with IMPLEMENTED when the all flag is provided"""
        gen = ReportGenerator()
        TargetRequirement = namedtuple('TargetRequirement', ['text', 'source'])
        missing = [
            DocRequirement(text="The system shall authenticate users", source="docs/example.md"),
        ]
        implemented = [
            TargetRequirement(text="The system shall log errors", source="tests/test_auth.py"),
        ]
        stale = [
            TargetRequirement(text="The system shall support LDAP", source="tests/test_old.py"),
        ]
        result = gen.generate(
            missing=missing,
            implemented=implemented,
            stale=stale,
            total_reqs=2,
            total_targets=2,
            all_flag=True,
        )
        expected = (
            "--- Missing (requirements with no target) ---\n"
            "  [MISSING] docs/example.md: The system shall authenticate users\n"
            "\n"
            "--- Implemented ---\n"
            "  [IMPLEMENTED] tests/test_auth.py: The system shall log errors\n"
            "\n"
            "--- Stale (targets with no matching requirement) ---\n"
            "  [STALE] tests/test_old.py: The system shall support LDAP\n"
            "\n"
            "--- Summary ---\n"
            "  Requirements:  2\n"
            "  Targets:       2\n"
            "  Missing:       1\n"
            "  Stale:         1\n"
            "  Implemented:   1\n"
        )
        assert result == expected


class TestReportGeneratorMissingOnly:
    def test_missing_only_no_stale_section(self):
        """REQ: Output missing coverage prefixed with MISSING and include the source doc file path"""
        gen = ReportGenerator()
        missing = [
            DocRequirement(text="The system shall authenticate users", source="docs/example.md"),
        ]
        result = gen.generate(
            missing=missing,
            implemented=[],
            stale=[],
            total_reqs=1,
            total_targets=0,
            all_flag=False,
        )
        expected = (
            "--- Missing (requirements with no target) ---\n"
            "  [MISSING] docs/example.md: The system shall authenticate users\n"
            "\n"
            "--- Summary ---\n"
            "  Requirements:  1\n"
            "  Targets:       0\n"
            "  Missing:       1\n"
            "  Stale:         0\n"
        )
        assert result == expected


class TestReportGeneratorStaleOnly:
    def test_stale_only_no_missing_section(self):
        """REQ: Output stale targets prefixed with STALE and include the source target file path"""
        gen = ReportGenerator()
        TargetRequirement = namedtuple('TargetRequirement', ['text', 'source'])
        stale = [
            TargetRequirement(text="The system shall support LDAP", source="tests/test_old.py"),
        ]
        result = gen.generate(
            missing=[],
            implemented=[],
            stale=stale,
            total_reqs=0,
            total_targets=1,
            all_flag=False,
        )
        expected = (
            "--- Stale (targets with no matching requirement) ---\n"
            "  [STALE] tests/test_old.py: The system shall support LDAP\n"
            "\n"
            "--- Summary ---\n"
            "  Requirements:  0\n"
            "  Targets:       1\n"
            "  Missing:       0\n"
            "  Stale:         1\n"
        )
        assert result == expected


class TestReportGeneratorCleanState:
    def test_clean_state_no_missing_no_stale(self):
        """REQ: Output a summary with counts of total requirements in docs, total in targets, missing, and stale"""
        gen = ReportGenerator()
        TargetRequirement = namedtuple('TargetRequirement', ['text', 'source'])
        implemented = [
            TargetRequirement(text="The system shall authenticate users", source="tests/test_auth.py"),
        ]
        result = gen.generate(
            missing=[],
            implemented=implemented,
            stale=[],
            total_reqs=1,
            total_targets=1,
            all_flag=False,
        )
        assert "--- Missing" not in result
        assert "--- Stale" not in result
        assert "--- Summary ---" in result
        assert "Missing:       0" in result
        assert "Stale:         0" in result


class TestReportGeneratorReturnType:
    def test_generate_returns_string(self):
        gen = ReportGenerator()
        result = gen.generate(
            missing=[],
            implemented=[],
            stale=[],
            total_reqs=0,
            total_targets=0,
            all_flag=False,
        )
        assert isinstance(result, str)


class TestReportGeneratorEmpty:
    def test_empty_inputs_produces_summary_only(self):
        """REQ: Output a summary with counts of total requirements in docs, total in targets, missing, and stale"""
        gen = ReportGenerator()
        result = gen.generate(
            missing=[],
            implemented=[],
            stale=[],
            total_reqs=0,
            total_targets=0,
            all_flag=False,
        )
        assert "--- Summary ---" in result
        assert "Requirements:  0" in result
        assert "Targets:       0" in result
        assert "Missing:       0" in result
        assert "Stale:         0" in result