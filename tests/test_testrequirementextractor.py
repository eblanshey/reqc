import os
import tempfile
import pytest
from stdd import TestRequirementExtractor, TestRequirement


class TestEmptyDirectory:
    def test_extract_returns_empty_list_for_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            extractor = TestRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert result == []


class TestExtractREQ:
    def test_extract_finds_req_in_py_file(self):
        """REQ: Search for the exact prefix REQ followed by a colon and a space in test files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "test_example.py")
            with open(testfile, "w") as f:
                f.write('def test_foo():\n    # REQ: User can login\n    pass\n')
            extractor = TestRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "User can login"
            assert result[0].source == testfile

    def test_extract_finds_req_in_txt_file(self):
        """REQ: Scan the test directory recursively with no file extension filtering"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "notes.txt")
            with open(testfile, "w") as f:
                f.write('REQ: System must handle errors\n')
            extractor = TestRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "System must handle errors"

    def test_extract_scans_subdirectories_recursively(self):
        """REQ: Scan the test directory recursively with no file extension filtering"""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "sub")
            os.makedirs(subdir)
            testfile = os.path.join(subdir, "test_deep.py")
            with open(testfile, "w") as f:
                f.write('REQ: Deep requirement found\n')
            extractor = TestRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "Deep requirement found"
            assert result[0].source == testfile

    def test_extract_strips_leading_trailing_whitespace(self):
        """REQ: Strip leading and trailing whitespace from each extracted requirement text"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "test_ws.py")
            with open(testfile, "w") as f:
                f.write('REQ:    padded text   \n')
            extractor = TestRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "padded text"

    def test_extract_strips_trailing_triple_quotes(self):
        """REQ: Strip trailing triple quotes from REQ entries to allow inline docstring markers"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "test_quotes.py")
            with open(testfile, "w") as f:
                f.write('"""REQ: Requirement with trailing quotes"""\n')
            extractor = TestRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "Requirement with trailing quotes"

    def test_extract_ignores_empty_req_entries(self):
        """REQ: Silently ignore empty REQ entries"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "test_empty.py")
            with open(testfile, "w") as f:
                f.write('REQ: \nREQ:   \nREQ: Valid one\n')
            extractor = TestRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "Valid one"

    def test_extract_multiple_reqs_across_files(self):
        """REQ: Extract the text after the REQ prefix as the requirement text"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = os.path.join(tmpdir, "test_a.py")
            with open(file1, "w") as f:
                f.write('REQ: First req\nREQ: Second req\n')
            file2 = os.path.join(tmpdir, "test_b.txt")
            with open(file2, "w") as f:
                f.write('REQ: Third req\n')
            extractor = TestRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 3
            texts = [r.text for r in result]
            assert "First req" in texts
            assert "Second req" in texts
            assert "Third req" in texts

    def test_pairs_requirement_with_source_file_path(self):
        """REQ: Pair each extracted test requirement text with its source file path as a TestRequirement named tuple"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "test_example.py")
            with open(testfile, "w") as f:
                f.write('REQ: User can login\n')
            extractor = TestRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert isinstance(result[0], TestRequirement)
            assert result[0].text == "User can login"
            assert result[0].source == testfile