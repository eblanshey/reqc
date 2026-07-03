import pytest
from reqc import ArgParser


class TestArgParser:

    def test_parse_args_returns_reqs_attribute(self):
        parser = ArgParser()
        result = parser.parse_args(['--reqs', './docs', '--targets', './tests'])
        assert hasattr(result, 'reqs')

    def test_reqs_stores_provided_path(self):
        """REQ: Accept a --reqs argument with short form -r that specifies the path to the requirements directory"""
        parser = ArgParser()
        result = parser.parse_args(['--reqs', './mydocs', '--targets', './tests'])
        assert result.reqs == './mydocs'

    def test_r_short_flag_works(self):
        """REQ: Accept a --reqs argument with short form -r that specifies the path to the requirements directory"""
        parser = ArgParser()
        result = parser.parse_args(['-r', './short', '--targets', './tests'])
        assert result.reqs == './short'

    def test_targets_stores_provided_path(self):
        """REQ: Accept a --targets argument with short form -t that specifies the path to the target directory"""
        parser = ArgParser()
        result = parser.parse_args(['--reqs', './docs', '--targets', './mytargets'])
        assert result.targets == './mytargets'

    def test_t_short_flag_works(self):
        """REQ: Accept a --targets argument with short form -t that specifies the path to the target directory"""
        parser = ArgParser()
        result = parser.parse_args(['--reqs', './docs', '-t', './short'])
        assert result.targets == './short'

    def test_all_defaults_to_false(self):
        parser = ArgParser()
        result = parser.parse_args(['--reqs', './docs', '--targets', './tests'])
        assert result.all is False

    def test_all_flag_sets_true(self):
        """REQ: Accept an --all flag with short form -a that shows implemented targets in addition to missing and stale ones"""
        parser = ArgParser()
        result = parser.parse_args(['--reqs', './docs', '--targets', './tests', '--all'])
        assert result.all is True

    def test_a_short_flag_works(self):
        """REQ: Accept an --all flag with short form -a that shows implemented targets in addition to missing and stale ones"""
        parser = ArgParser()
        result = parser.parse_args(['--reqs', './docs', '--targets', './tests', '-a'])
        assert result.all is True

    def test_reqs_required_error_when_missing(self):
        parser = ArgParser()
        with pytest.raises(SystemExit):
            parser.parse_args(['--targets', './tests'])

    def test_targets_required_error_when_missing(self):
        parser = ArgParser()
        with pytest.raises(SystemExit):
            parser.parse_args(['--reqs', './docs'])