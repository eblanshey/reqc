import pytest
from stdd import ArgParser


class TestArgParser:

    def test_parse_args_returns_docs_attribute(self):
        parser = ArgParser()
        result = parser.parse_args(['--docs', './docs', '--tests', './tests'])
        assert hasattr(result, 'docs')

    def test_docs_stores_provided_path(self):
        """REQ: Accept a --docs argument with short form -d that specifies the path to the documentation directory"""
        parser = ArgParser()
        result = parser.parse_args(['--docs', './mydocs', '--tests', './tests'])
        assert result.docs == './mydocs'

    def test_d_short_flag_works(self):
        """REQ: Accept a --docs argument with short form -d that specifies the path to the documentation directory"""
        parser = ArgParser()
        result = parser.parse_args(['-d', './short', '--tests', './tests'])
        assert result.docs == './short'

    def test_tests_stores_provided_path(self):
        """REQ: Accept a --tests argument with short form -t that specifies the path to the test directory"""
        parser = ArgParser()
        result = parser.parse_args(['--docs', './docs', '--tests', './mytests'])
        assert result.tests == './mytests'

    def test_t_short_flag_works(self):
        """REQ: Accept a --tests argument with short form -t that specifies the path to the test directory"""
        parser = ArgParser()
        result = parser.parse_args(['--docs', './docs', '-t', './short'])
        assert result.tests == './short'

    def test_all_defaults_to_false(self):
        parser = ArgParser()
        result = parser.parse_args(['--docs', './docs', '--tests', './tests'])
        assert result.all is False

    def test_all_flag_sets_true(self):
        """REQ: Accept an --all flag with short form -a that shows implemented tests in addition to missing and stale ones"""
        parser = ArgParser()
        result = parser.parse_args(['--docs', './docs', '--tests', './tests', '--all'])
        assert result.all is True

    def test_a_short_flag_works(self):
        """REQ: Accept an --all flag with short form -a that shows implemented tests in addition to missing and stale ones"""
        parser = ArgParser()
        result = parser.parse_args(['--docs', './docs', '--tests', './tests', '-a'])
        assert result.all is True

    def test_docs_required_error_when_missing(self):
        parser = ArgParser()
        with pytest.raises(SystemExit):
            parser.parse_args(['--tests', './tests'])

    def test_tests_required_error_when_missing(self):
        parser = ArgParser()
        with pytest.raises(SystemExit):
            parser.parse_args(['--docs', './docs'])