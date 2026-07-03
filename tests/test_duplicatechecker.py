from reqc import DuplicateChecker, DuplicateRequirementError, DocRequirement


class TestDuplicateChecker:
    def test_empty_requirements_does_not_raise(self):
        checker = DuplicateChecker()
        checker.check([])

    def test_no_duplicates_does_not_raise(self):
        checker = DuplicateChecker()
        requirements = [
            DocRequirement("Requirement A", "doc1.md"),
            DocRequirement("Requirement B", "doc2.md"),
        ]
        checker.check(requirements)

    def test_duplicate_across_files_raises(self):
        """REQ: Detect when the same requirement text appears in multiple documentation files"""
        checker = DuplicateChecker()
        requirements = [
            DocRequirement("Same requirement", "doc1.md"),
            DocRequirement("Same requirement", "doc2.md"),
        ]
        try:
            checker.check(requirements)
            assert False, "Expected DuplicateRequirementError"
        except DuplicateRequirementError as e:
            assert "Same requirement" in str(e)
            assert "doc1.md" in str(e)
            assert "doc2.md" in str(e)

    def test_duplicate_within_single_file_raises(self):
        """REQ: Detect when the same requirement text appears multiple times within a single documentation file"""
        checker = DuplicateChecker()
        requirements = [
            DocRequirement("Same requirement", "doc1.md"),
            DocRequirement("Same requirement", "doc1.md"),
        ]
        try:
            checker.check(requirements)
            assert False, "Expected DuplicateRequirementError"
        except DuplicateRequirementError as e:
            assert "Same requirement" in str(e)
            assert str(e).count("doc1.md") == 2

    def test_multiple_different_duplicates_raises(self):
        """REQ: Detect when the same requirement text appears in multiple documentation files"""
        checker = DuplicateChecker()
        requirements = [
            DocRequirement("Req A", "doc1.md"),
            DocRequirement("Req B", "doc2.md"),
            DocRequirement("Req A", "doc3.md"),
            DocRequirement("Req B", "doc4.md"),
        ]
        try:
            checker.check(requirements)
            assert False, "Expected DuplicateRequirementError"
        except DuplicateRequirementError as e:
            assert "Req A" in str(e)

    def test_error_message_contains_duplicate_text_and_paths(self):
        """REQ: Raise an error with the duplicate text and all conflicting source file paths"""
        checker = DuplicateChecker()
        requirements = [
            DocRequirement("Login must use OAuth", "docs/auth.md"),
            DocRequirement("Login must use OAuth", "docs/security.md"),
        ]
        try:
            checker.check(requirements)
            assert False, "Expected DuplicateRequirementError"
        except DuplicateRequirementError as e:
            assert "Login must use OAuth" in str(e)
            assert "docs/auth.md" in str(e)
            assert "docs/security.md" in str(e)

    def test_three_occurrences_reports_all_sources(self):
        """REQ: Raise an error with the duplicate text and all conflicting source file paths"""
        checker = DuplicateChecker()
        requirements = [
            DocRequirement("Must encrypt", "doc1.md"),
            DocRequirement("Must encrypt", "doc2.md"),
            DocRequirement("Must encrypt", "doc3.md"),
        ]
        try:
            checker.check(requirements)
            assert False, "Expected DuplicateRequirementError"
        except DuplicateRequirementError as e:
            assert "Must encrypt" in str(e)
            assert "doc1.md" in str(e)
            assert "doc2.md" in str(e)
            assert "doc3.md" in str(e)