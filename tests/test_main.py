"""Tests for reqc.main()"""
import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile

from reqc import main, DuplicateRequirementError, DocRequirement, TargetRequirement as TReq


class TestMainParsesArgs:
    def test_main_calls_argparser(self):
        """Verify main() invokes ArgParser and calls parse_args with the provided argv."""
        with patch('reqc.ArgParser') as MockParser:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock()
            mock_args.reqs = '/fake/reqs'
            mock_args.targets = '/fake/targets'
            mock_args.all = False
            mock_parser_instance.parse_args.return_value = mock_args
            MockParser.return_value = mock_parser_instance

            with patch('os.path.isdir', return_value=True):
                with patch('reqc.DocRequirementExtractor') as MockDre:
                    MockDre.return_value.extract.return_value = []
                    with patch('reqc.TargetRequirementExtractor') as MockTre:
                        MockTre.return_value.extract.return_value = []
                        with patch('reqc.DuplicateChecker') as MockDc:
                            MockDc.return_value.check.return_value = None
                            with patch('reqc.RequirementMatcher') as MockRm:
                                MockRm.return_value.match.return_value = {
                                    'missing': [], 'implemented': [], 'stale': []
                                }
                                with patch('reqc.ReportGenerator') as MockRg:
                                    MockRg.return_value.generate.return_value = ''
                                    with patch('builtins.print'):
                                        result = main([])

            MockParser.assert_called_once()
            mock_parser_instance.parse_args.assert_called_once_with([])


class TestMainValidatesReqsDir:
    def test_main_raises_file_not_found_for_missing_reqs_dir(self):
        """REQ: Validate that the --reqs directory exists and is readable"""
        with patch('reqc.ArgParser') as MockParser:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock()
            mock_args.reqs = '/nonexistent/reqs'
            mock_args.targets = '/fake/targets'
            mock_args.all = False
            mock_parser_instance.parse_args.return_value = mock_args
            MockParser.return_value = mock_parser_instance

            with patch('os.path.isdir', return_value=False):
                with pytest.raises(FileNotFoundError) as exc_info:
                    main([])

            assert 'reqs' in str(exc_info.value).lower()


class TestMainValidatesTargetsDir:
    def test_main_raises_file_not_found_for_missing_targets_dir(self):
        """REQ: Validate that the --targets directory exists and is readable"""
        with patch('reqc.ArgParser') as MockParser:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock()
            mock_args.reqs = '/fake/reqs'
            mock_args.targets = '/nonexistent/targets'
            mock_args.all = False
            mock_parser_instance.parse_args.return_value = mock_args
            MockParser.return_value = mock_parser_instance

            with patch('os.path.isdir', side_effect=[True, False]):
                with pytest.raises(FileNotFoundError) as exc_info:
                    main([])

            assert 'targets' in str(exc_info.value).lower()


class TestMainExitCodeZero:
    def test_main_returns_zero_when_all_requirements_matched(self):
        """REQ: Return exit code 0 when all requirements are matched with no missing or stale targets"""
        with patch('reqc.ArgParser') as MockParser:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock()
            mock_args.reqs = '/fake/reqs'
            mock_args.targets = '/fake/targets'
            mock_args.all = False
            mock_parser_instance.parse_args.return_value = mock_args
            MockParser.return_value = mock_parser_instance

            with patch('os.path.isdir', return_value=True):
                with patch('reqc.DocRequirementExtractor') as MockDre:
                    mock_dre = MagicMock()
                    mock_dre.extract.return_value = [
                        DocRequirement('req1', 'file.md')
                    ]
                    MockDre.return_value = mock_dre
                    with patch('reqc.TargetRequirementExtractor') as MockTre:
                        mock_tre = MagicMock()
                        mock_tre.extract.return_value = [
                            TReq('req1', 'target_file.py')
                        ]
                        MockTre.return_value = mock_tre
                        with patch('reqc.DuplicateChecker') as MockDc:
                            MockDc.return_value.check.return_value = None
                            with patch('reqc.RequirementMatcher') as MockRm:
                                mock_rm = MagicMock()
                                mock_rm.match.return_value = {
                                    'missing': [],
                                    'implemented': ['req1'],
                                    'stale': []
                                }
                                MockRm.return_value = mock_rm
                                with patch('reqc.ReportGenerator') as MockRg:
                                    MockRg.return_value.generate.return_value = 'Report'
                                    with patch('builtins.print'):
                                        result = main([])

            assert result == 0
            mock_dre.extract.assert_called_once_with('/fake/reqs')
            mock_tre.extract.assert_called_once_with('/fake/targets')
            MockDc.assert_called_once()
            mock_rm.match.assert_called_once()
            MockRg.assert_called_once()


class TestMainExitCodeOne:
    def test_main_returns_one_when_missing_requirements(self):
        """REQ: Return exit code 1 when mismatches are found with missing or stale targets"""
        with patch('reqc.ArgParser') as MockParser:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock()
            mock_args.reqs = '/fake/reqs'
            mock_args.targets = '/fake/targets'
            mock_args.all = False
            mock_parser_instance.parse_args.return_value = mock_args
            MockParser.return_value = mock_parser_instance

            with patch('os.path.isdir', return_value=True):
                with patch('reqc.DocRequirementExtractor') as MockDre:
                    mock_dre = MagicMock()
                    mock_dre.extract.return_value = [
                        DocRequirement('req1', 'file.md'),
                        DocRequirement('req2', 'file.md')
                    ]
                    MockDre.return_value = mock_dre
                    with patch('reqc.TargetRequirementExtractor') as MockTre:
                        mock_tre = MagicMock()
                        mock_tre.extract.return_value = [
                            TReq('req1', 'target_file.py')
                        ]
                        MockTre.return_value = mock_tre
                        with patch('reqc.DuplicateChecker') as MockDc:
                            MockDc.return_value.check.return_value = None
                            with patch('reqc.RequirementMatcher') as MockRm:
                                mock_rm = MagicMock()
                                mock_rm.match.return_value = {
                                    'missing': ['req2'],
                                    'implemented': ['req1'],
                                    'stale': []
                                }
                                MockRm.return_value = mock_rm
                                with patch('reqc.ReportGenerator') as MockRg:
                                    MockRg.return_value.generate.return_value = 'Report'
                                    with patch('builtins.print'):
                                        result = main([])

            assert result == 1

    def test_main_returns_one_when_stale_targets(self):
        """REQ: Return exit code 1 when mismatches are found with missing or stale targets"""
        with patch('reqc.ArgParser') as MockParser:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock()
            mock_args.reqs = '/fake/reqs'
            mock_args.targets = '/fake/targets'
            mock_args.all = False
            mock_parser_instance.parse_args.return_value = mock_args
            MockParser.return_value = mock_parser_instance

            with patch('os.path.isdir', return_value=True):
                with patch('reqc.DocRequirementExtractor') as MockDre:
                    mock_dre = MagicMock()
                    mock_dre.extract.return_value = [
                        DocRequirement('req1', 'file.md')
                    ]
                    MockDre.return_value = mock_dre
                    with patch('reqc.TargetRequirementExtractor') as MockTre:
                        mock_tre = MagicMock()
                        mock_tre.extract.return_value = [
                            TReq('req1', 'target_file.py'),
                            TReq('old_req', 'target_file.py')
                        ]
                        MockTre.return_value = mock_tre
                        with patch('reqc.DuplicateChecker') as MockDc:
                            MockDc.return_value.check.return_value = None
                            with patch('reqc.RequirementMatcher') as MockRm:
                                mock_rm = MagicMock()
                                mock_rm.match.return_value = {
                                    'missing': [],
                                    'implemented': ['req1'],
                                    'stale': ['old_req']
                                }
                                MockRm.return_value = mock_rm
                                with patch('reqc.ReportGenerator') as MockRg:
                                    MockRg.return_value.generate.return_value = 'Report'
                                    with patch('builtins.print'):
                                        result = main([])

            assert result == 1


class TestMainExitCodeTwo:
    def test_main_returns_two_when_duplicate_requirements(self):
        """REQ: Return exit code 2 when duplicate requirement text is detected across documentation files"""
        with patch('reqc.ArgParser') as MockParser:
            mock_parser_instance = MagicMock()
            mock_args = MagicMock()
            mock_args.reqs = '/fake/reqs'
            mock_args.targets = '/fake/targets'
            mock_args.all = False
            mock_parser_instance.parse_args.return_value = mock_args
            MockParser.return_value = mock_parser_instance

            with patch('os.path.isdir', return_value=True):
                with patch('reqc.DocRequirementExtractor') as MockDre:
                    mock_dre = MagicMock()
                    mock_dre.extract.return_value = [
                        DocRequirement('req1', 'file1.md'),
                        DocRequirement('req1', 'file2.md')
                    ]
                    MockDre.return_value = mock_dre
                    with patch('reqc.TargetRequirementExtractor') as MockTre:
                        mock_tre = MagicMock()
                        mock_tre.extract.return_value = []
                        MockTre.return_value = mock_tre
                        with patch('reqc.DuplicateChecker') as MockDc:
                            mock_dc = MagicMock()
                            mock_dc.check.side_effect = DuplicateRequirementError(
                                'Duplicate requirement: req1'
                            )
                            MockDc.return_value = mock_dc
                            with patch('reqc.RequirementMatcher') as MockRm:
                                with patch('reqc.ReportGenerator') as MockRg:
                                    with patch('builtins.print'):
                                        result = main([])

            assert result == 2
            mock_dc.check.assert_called_once()
            MockRm.assert_not_called()
            MockRg.assert_not_called()