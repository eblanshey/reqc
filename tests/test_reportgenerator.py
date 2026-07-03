from collections import namedtuple
from stdd import ReportGenerator

DocRequirement = namedtuple('DocRequirement', ['text', 'source'])


class TestReportGeneratorMissing:
    def test_missing_tests_shown_with_prefix_and_source(self):
        """REQ: Output missing tests prefixed with MISSING and include the source doc file path"""
        gen = ReportGenerator()
        missing = [
            DocRequirement(text="The system shall authenticate users", source="docs/example.md"),
            DocRequirement(text="The system shall log errors", source="docs/example.md"),
        ]
        result = gen.generate(
            missing=missing,
            implemented=[],
            stale=[],
            total_docs=2,
            total_tests=0,
            all_flag=False,
        )
        assert "--- Missing Tests (requirements in docs with no test) ---" in result
        assert "[MISSING] docs/example.md: The system shall authenticate users" in result
        assert "[MISSING] docs/example.md: The system shall log errors" in result


class TestReportGeneratorStale:
    def test_stale_tests_shown_with_prefix_and_source(self):
        """REQ: Output stale tests prefixed with STALE and include the source test file path"""
        gen = ReportGenerator()
        TestRequirement = namedtuple('TestRequirement', ['text', 'source'])
        stale = [
            TestRequirement(text="The system shall support LDAP", source="tests/test_auth.py"),
            TestRequirement(text="The system shall support OAuth", source="tests/test_old.py"),
        ]
        result = gen.generate(
            missing=[],
            implemented=[],
            stale=stale,
            total_docs=0,
            total_tests=2,
            all_flag=False,
        )
        assert "--- Stale Tests (tests with no matching requirement) ---" in result
        assert "[STALE] tests/test_auth.py: The system shall support LDAP" in result
        assert "[STALE] tests/test_old.py: The system shall support OAuth" in result

    def test_all_categories_with_exact_format(self):
        """REQ: Output a summary with counts of total requirements in docs, total in tests, missing, and stale"""
        gen = ReportGenerator()
        TestRequirement = namedtuple('TestRequirement', ['text', 'source'])
        missing = [
            DocRequirement(text="The system shall authenticate users", source="docs/example.md"),
            DocRequirement(text="The system shall log errors", source="docs/example.md"),
        ]
        stale = [
            TestRequirement(text="The system shall support LDAP", source="tests/test_auth.py"),
            TestRequirement(text="The system shall support OAuth", source="tests/test_old.py"),
        ]
        result = gen.generate(
            missing=missing,
            implemented=[],
            stale=stale,
            total_docs=4,
            total_tests=4,
            all_flag=False,
        )
        expected = (
            "--- Missing Tests (requirements in docs with no test) ---\n"
            "  [MISSING] docs/example.md: The system shall authenticate users\n"
            "  [MISSING] docs/example.md: The system shall log errors\n"
            "\n"
            "--- Stale Tests (tests with no matching requirement) ---\n"
            "  [STALE] tests/test_auth.py: The system shall support LDAP\n"
            "  [STALE] tests/test_old.py: The system shall support OAuth\n"
            "\n"
            "--- Summary ---\n"
            "  Requirements in docs:  4\n"
            "  Requirements in tests: 4\n"
            "  Missing tests:         2\n"
            "  Stale tests:           2\n"
        )
        assert result == expected


class TestReportGeneratorAllFlag:
    def test_all_flag_shows_implemented_section(self):
        """REQ: Show implemented tests prefixed with IMPLEMENTED when the all flag is provided"""
        gen = ReportGenerator()
        TestRequirement = namedtuple('TestRequirement', ['text', 'source'])
        missing = [
            DocRequirement(text="The system shall authenticate users", source="docs/example.md"),
        ]
        implemented = [
            TestRequirement(text="The system shall log errors", source="tests/test_auth.py"),
        ]
        stale = [
            TestRequirement(text="The system shall support LDAP", source="tests/test_old.py"),
        ]
        result = gen.generate(
            missing=missing,
            implemented=implemented,
            stale=stale,
            total_docs=2,
            total_tests=2,
            all_flag=True,
        )
        expected = (
            "--- Missing Tests (requirements in docs with no test) ---\n"
            "  [MISSING] docs/example.md: The system shall authenticate users\n"
            "\n"
            "--- Implemented Tests ---\n"
            "  [IMPLEMENTED] tests/test_auth.py: The system shall log errors\n"
            "\n"
            "--- Stale Tests (tests with no matching requirement) ---\n"
            "  [STALE] tests/test_old.py: The system shall support LDAP\n"
            "\n"
            "--- Summary ---\n"
            "  Requirements in docs:  2\n"
            "  Requirements in tests: 2\n"
            "  Missing tests:         1\n"
            "  Stale tests:           1\n"
            "  Implemented tests:     1\n"
        )
        assert result == expected

    def test_all_flag_false_hides_implemented(self):
        gen = ReportGenerator()
        TestRequirement = namedtuple('TestRequirement', ['text', 'source'])
        implemented = [
            TestRequirement(text="The system shall log errors", source="tests/test_auth.py"),
        ]
        result = gen.generate(
            missing=[],
            implemented=implemented,
            stale=[],
            total_docs=1,
            total_tests=1,
            all_flag=False,
        )
        assert "[IMPLEMENTED]" not in result
        assert "Implemented tests" not in result

    def test_all_flag_exact_format_from_spec(self):
        """REQ: Show implemented tests prefixed with IMPLEMENTED when the all flag is provided"""
        gen = ReportGenerator()
        TestRequirement = namedtuple('TestRequirement', ['text', 'source'])
        missing = [
            DocRequirement(text="The system shall authenticate users", source="docs/example.md"),
        ]
        implemented = [
            TestRequirement(text="The system shall log errors", source="tests/test_auth.py"),
        ]
        stale = [
            TestRequirement(text="The system shall support LDAP", source="tests/test_old.py"),
        ]
        result = gen.generate(
            missing=missing,
            implemented=implemented,
            stale=stale,
            total_docs=2,
            total_tests=2,
            all_flag=True,
        )
        expected = (
            "--- Missing Tests (requirements in docs with no test) ---\n"
            "  [MISSING] docs/example.md: The system shall authenticate users\n"
            "\n"
            "--- Implemented Tests ---\n"
            "  [IMPLEMENTED] tests/test_auth.py: The system shall log errors\n"
            "\n"
            "--- Stale Tests (tests with no matching requirement) ---\n"
            "  [STALE] tests/test_old.py: The system shall support LDAP\n"
            "\n"
            "--- Summary ---\n"
            "  Requirements in docs:  2\n"
            "  Requirements in tests: 2\n"
            "  Missing tests:         1\n"
            "  Stale tests:           1\n"
            "  Implemented tests:     1\n"
        )
        assert result == expected


class TestReportGeneratorMissingOnly:
    def test_missing_only_no_stale_section(self):
        """REQ: Output missing tests prefixed with MISSING and include the source doc file path"""
        gen = ReportGenerator()
        missing = [
            DocRequirement(text="The system shall authenticate users", source="docs/example.md"),
        ]
        result = gen.generate(
            missing=missing,
            implemented=[],
            stale=[],
            total_docs=1,
            total_tests=0,
            all_flag=False,
        )
        expected = (
            "--- Missing Tests (requirements in docs with no test) ---\n"
            "  [MISSING] docs/example.md: The system shall authenticate users\n"
            "\n"
            "--- Summary ---\n"
            "  Requirements in docs:  1\n"
            "  Requirements in tests: 0\n"
            "  Missing tests:         1\n"
            "  Stale tests:           0\n"
        )
        assert result == expected


class TestReportGeneratorStaleOnly:
    def test_stale_only_no_missing_section(self):
        """REQ: Output stale tests prefixed with STALE and include the source test file path"""
        gen = ReportGenerator()
        TestRequirement = namedtuple('TestRequirement', ['text', 'source'])
        stale = [
            TestRequirement(text="The system shall support LDAP", source="tests/test_old.py"),
        ]
        result = gen.generate(
            missing=[],
            implemented=[],
            stale=stale,
            total_docs=0,
            total_tests=1,
            all_flag=False,
        )
        expected = (
            "--- Stale Tests (tests with no matching requirement) ---\n"
            "  [STALE] tests/test_old.py: The system shall support LDAP\n"
            "\n"
            "--- Summary ---\n"
            "  Requirements in docs:  0\n"
            "  Requirements in tests: 1\n"
            "  Missing tests:         0\n"
            "  Stale tests:           1\n"
        )
        assert result == expected


class TestReportGeneratorCleanState:
    def test_clean_state_no_missing_no_stale(self):
        """REQ: Output a summary with counts of total requirements in docs, total in tests, missing, and stale"""
        gen = ReportGenerator()
        TestRequirement = namedtuple('TestRequirement', ['text', 'source'])
        implemented = [
            TestRequirement(text="The system shall authenticate users", source="tests/test_auth.py"),
        ]
        result = gen.generate(
            missing=[],
            implemented=implemented,
            stale=[],
            total_docs=1,
            total_tests=1,
            all_flag=False,
        )
        assert "--- Missing Tests" not in result
        assert "--- Stale Tests" not in result
        assert "--- Summary ---" in result
        assert "Missing tests:         0" in result
        assert "Stale tests:           0" in result


class TestReportGeneratorReturnType:
    def test_generate_returns_string(self):
        gen = ReportGenerator()
        result = gen.generate(
            missing=[],
            implemented=[],
            stale=[],
            total_docs=0,
            total_tests=0,
            all_flag=False,
        )
        assert isinstance(result, str)


class TestReportGeneratorEmpty:
    def test_empty_inputs_produces_summary_only(self):
        """REQ: Output a summary with counts of total requirements in docs, total in tests, missing, and stale"""
        gen = ReportGenerator()
        result = gen.generate(
            missing=[],
            implemented=[],
            stale=[],
            total_docs=0,
            total_tests=0,
            all_flag=False,
        )
        assert "--- Summary ---" in result
        assert "Requirements in docs:  0" in result
        assert "Requirements in tests: 0" in result
        assert "Missing tests:         0" in result
        assert "Stale tests:           0" in result