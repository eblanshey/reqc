from reqc import RequirementMatcher, DocRequirement, TargetRequirement


class TestRequirementMatcher:

    def test_empty_inputs(self):
        """Verify match returns empty lists when given no inputs."""
        matcher = RequirementMatcher()
        result = matcher.match([], [])
        assert result == {'missing': [], 'implemented': [], 'stale': []}

    def test_all_missing_no_targets(self):
        """REQ: Identify missing coverage as requirements in docs with no matching target"""
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
        """REQ: Identify stale targets as requirements in targets with no matching doc requirement"""
        matcher = RequirementMatcher()
        target_reqs = [
            TargetRequirement('Old feature', 'test_old.py'),
            TargetRequirement('Removed feature', 'test_removed.py'),
        ]
        result = matcher.match([], target_reqs)
        assert result['missing'] == []
        assert result['implemented'] == []
        assert result['stale'] == target_reqs

    def test_all_matching(self):
        """REQ: Identify implemented targets as requirements that appear in both docs and targets"""
        matcher = RequirementMatcher()
        doc_reqs = [
            DocRequirement('Login', 'README.md'),
            DocRequirement('Logout', 'README.md'),
        ]
        target_reqs = [
            TargetRequirement('Login', 'test_auth.py'),
            TargetRequirement('Logout', 'test_auth.py'),
        ]
        result = matcher.match(doc_reqs, target_reqs)
        assert result['missing'] == []
        assert result['implemented'] == target_reqs
        assert result['stale'] == []

    def test_mixed_missing_implemented_stale(self):
        """REQ: Identify missing coverage as requirements in docs with no matching target
        REQ: Identify stale targets as requirements in targets with no matching doc requirement
        REQ: Identify implemented targets as requirements that appear in both docs and targets"""
        matcher = RequirementMatcher()
        doc_reqs = [
            DocRequirement('Login', 'README.md'),
            DocRequirement('Dashboard', 'README.md'),
            DocRequirement('Settings', 'README.md'),
        ]
        target_reqs = [
            TargetRequirement('Login', 'test_auth.py'),
            TargetRequirement('Dashboard', 'test_dash.py'),
            TargetRequirement('Old Feature', 'test_old.py'),
        ]
        result = matcher.match(doc_reqs, target_reqs)
        assert result['missing'] == [DocRequirement('Settings', 'README.md')]
        assert result['implemented'] == [
            TargetRequirement('Login', 'test_auth.py'),
            TargetRequirement('Dashboard', 'test_dash.py'),
        ]
        assert result['stale'] == [TargetRequirement('Old Feature', 'test_old.py')]

    def test_exact_string_comparison_case_and_whitespace(self):
        """REQ: Perform exact string comparison for matching requirements between docs and targets"""
        matcher = RequirementMatcher()
        doc_reqs = [
            DocRequirement('Login', 'README.md'),
            DocRequirement('  Spaced  ', 'README.md'),
        ]
        target_reqs = [
            TargetRequirement('login', 'test_auth.py'),
            TargetRequirement('Login ', 'test_auth.py'),
            TargetRequirement('  Spaced  ', 'test_auth.py'),
        ]
        result = matcher.match(doc_reqs, target_reqs)
        assert result['missing'] == [DocRequirement('Login', 'README.md')]
        assert result['implemented'] == [TargetRequirement('  Spaced  ', 'test_auth.py')]
        assert result['stale'] == [
            TargetRequirement('login', 'test_auth.py'),
            TargetRequirement('Login ', 'test_auth.py'),
        ]