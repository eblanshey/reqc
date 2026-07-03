from stdd import RequirementMatcher, DocRequirement, TestRequirement


class TestRequirementMatcher:

    def test_empty_inputs(self):
        """Verify match returns empty lists when given no inputs."""
        matcher = RequirementMatcher()
        result = matcher.match([], [])
        assert result == {'missing': [], 'implemented': [], 'stale': []}

    def test_all_missing_no_tests(self):
        """REQ: Identify missing tests as requirements in docs with no matching test"""
        matcher = RequirementMatcher()
        doc_reqs = [
            DocRequirement('User can login', 'README.md'),
            DocRequirement('User can logout', 'README.md'),
        ]
        result = matcher.match(doc_reqs, [])
        assert result['missing'] == doc_reqs
        assert result['implemented'] == []
        assert result['stale'] == []

    def test_all_stale_no_docs(self):
        """REQ: Identify stale tests as requirements in tests with no matching doc requirement"""
        matcher = RequirementMatcher()
        test_reqs = [
            TestRequirement('Old feature', 'test_old.py'),
            TestRequirement('Removed feature', 'test_removed.py'),
        ]
        result = matcher.match([], test_reqs)
        assert result['missing'] == []
        assert result['implemented'] == []
        assert result['stale'] == test_reqs

    def test_all_matching(self):
        """REQ: Identify implemented tests as requirements that appear in both docs and tests"""
        matcher = RequirementMatcher()
        doc_reqs = [
            DocRequirement('Login', 'README.md'),
            DocRequirement('Logout', 'README.md'),
        ]
        test_reqs = [
            TestRequirement('Login', 'test_auth.py'),
            TestRequirement('Logout', 'test_auth.py'),
        ]
        result = matcher.match(doc_reqs, test_reqs)
        assert result['missing'] == []
        assert result['implemented'] == test_reqs
        assert result['stale'] == []

    def test_mixed_missing_implemented_stale(self):
        """REQ: Identify missing tests as requirements in docs with no matching test
        REQ: Identify stale tests as requirements in tests with no matching doc requirement
        REQ: Identify implemented tests as requirements that appear in both docs and tests"""
        matcher = RequirementMatcher()
        doc_reqs = [
            DocRequirement('Login', 'README.md'),
            DocRequirement('Dashboard', 'README.md'),
            DocRequirement('Settings', 'README.md'),
        ]
        test_reqs = [
            TestRequirement('Login', 'test_auth.py'),
            TestRequirement('Dashboard', 'test_dash.py'),
            TestRequirement('Old Feature', 'test_old.py'),
        ]
        result = matcher.match(doc_reqs, test_reqs)
        assert result['missing'] == [DocRequirement('Settings', 'README.md')]
        assert result['implemented'] == [
            TestRequirement('Login', 'test_auth.py'),
            TestRequirement('Dashboard', 'test_dash.py'),
        ]
        assert result['stale'] == [TestRequirement('Old Feature', 'test_old.py')]

    def test_exact_string_comparison_case_and_whitespace(self):
        """REQ: Perform exact string comparison for matching requirements between docs and tests"""
        matcher = RequirementMatcher()
        doc_reqs = [
            DocRequirement('Login', 'README.md'),
            DocRequirement('  Spaced  ', 'README.md'),
        ]
        test_reqs = [
            TestRequirement('login', 'test_auth.py'),
            TestRequirement('Login ', 'test_auth.py'),
            TestRequirement('  Spaced  ', 'test_auth.py'),
        ]
        result = matcher.match(doc_reqs, test_reqs)
        assert result['missing'] == [DocRequirement('Login', 'README.md')]
        assert result['implemented'] == [TestRequirement('  Spaced  ', 'test_auth.py')]
        assert result['stale'] == [
            TestRequirement('login', 'test_auth.py'),
            TestRequirement('Login ', 'test_auth.py'),
        ]