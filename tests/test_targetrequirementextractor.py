import os
import tempfile
import pytest
from reqc import TargetRequirementExtractor, TargetRequirement


class TestEmptyDirectory:
    def test_extract_returns_empty_list_for_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            extractor = TargetRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert result == []


class TestExtractREQ:
    def test_extract_finds_req_in_py_file(self):
        """REQ: Search for the prefix REQ followed by a colon and a space in target files, matching case-insensitively"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "test_example.py")
            with open(testfile, "w") as f:
                f.write('def test_foo():\n    # REQ: User can login\n    pass\n')  # req-ignore
            extractor = TargetRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "User can login"
            assert result[0].source == f"{testfile}:2"

    def test_extract_finds_req_in_txt_file(self):
        """REQ: Scan the target directory recursively with no file extension filtering"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "notes.txt")
            with open(testfile, "w") as f:
                f.write('REQ: System must handle errors\n')  # req-ignore
            extractor = TargetRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "System must handle errors"
            assert result[0].source == f"{testfile}:1"

    def test_extract_scans_subdirectories_recursively(self):
        """REQ: Scan the target directory recursively with no file extension filtering"""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "sub")
            os.makedirs(subdir)
            testfile = os.path.join(subdir, "test_deep.py")
            with open(testfile, "w") as f:
                f.write('REQ: Deep requirement found\n')  # req-ignore
            extractor = TargetRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "Deep requirement found"
            assert result[0].source == f"{testfile}:1"

    def test_extract_strips_leading_trailing_whitespace(self):
        """REQ: Strip leading and trailing whitespace from each extracted requirement text"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "test_ws.py")
            with open(testfile, "w") as f:
                f.write('REQ:    padded text   \n')  # req-ignore
            extractor = TargetRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "padded text"

    def test_extract_strips_trailing_triple_quotes(self):
        """REQ: Strip trailing triple quotes from REQ entries to allow inline docstring markers"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "test_quotes.py")
            with open(testfile, "w") as f:
                f.write('"""REQ: Requirement with trailing quotes"""\n')  # req-ignore
            extractor = TargetRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "Requirement with trailing quotes"

    def test_extract_ignores_empty_req_entries(self):
        """REQ: Silently ignore empty REQ entries"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "test_empty.py")
            with open(testfile, "w") as f:
                f.write('REQ: \nREQ:   \nREQ: Valid one\n')  # req-ignore
            extractor = TargetRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "Valid one"

    def test_extract_skips_req_ignore(self):
        """REQ: Skip REQ entries that contain the keyword to filter out false flags"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "test_skip.py")
            with open(testfile, "w") as f:
                f.write('REQ: Valid requirement\nREQ: Skip this req-ignore\nREQ: Another valid\n')
            extractor = TargetRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 2
            assert result[0].text == "Valid requirement"
            assert result[1].text == "Another valid"

    def test_extract_multiple_reqs_across_files(self):
        """REQ: Extract the text after the REQ prefix as the requirement text"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = os.path.join(tmpdir, "test_a.py")
            with open(file1, "w") as f:
                f.write('REQ: First req\nREQ: Second req\n')  # req-ignore
            file2 = os.path.join(tmpdir, "test_b.txt")
            with open(file2, "w") as f:
                f.write('REQ: Third req\n')  # req-ignore
            extractor = TargetRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 3
            texts = [r.text for r in result]
            assert "First req" in texts
            assert "Second req" in texts
            assert "Third req" in texts

    def test_pairs_requirement_with_source_file_path_and_line(self):
        """REQ: Pair each extracted target requirement text with its source file path and line number (e.g. `filename.py:42`) as a TargetRequirement named tuple"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "test_example.py")
            with open(testfile, "w") as f:
                f.write('REQ: User can login\n')  # req-ignore
            extractor = TargetRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert isinstance(result[0], TargetRequirement)
            assert result[0].text == "User can login"
            assert result[0].source == f"{testfile}:1"

    def test_extract_matches_req_case_insensitively(self):
        """REQ: Accept REQ markers in any case variation such as req, Req, REQ, or ReQ"""
        with tempfile.TemporaryDirectory() as tmpdir:
            testfile = os.path.join(tmpdir, "test_case.py")
            with open(testfile, "w") as f:
                f.write('REQ: Upper case\n')  # req-ignore
                f.write('req: Lower case\n')  # req-ignore
                f.write('Req: Mixed case\n')  # req-ignore
                f.write('ReQ: Weird case\n')  # req-ignore
            extractor = TargetRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 4
            texts = [r.text for r in result]
            assert "Upper case" in texts
            assert "Lower case" in texts
            assert "Mixed case" in texts
            assert "Weird case" in texts