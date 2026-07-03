import os
import tempfile
import pytest
from reqc import DocRequirementExtractor, DocRequirement


class TestExtract:
    def test_empty_directory_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            extractor = DocRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert result == []

    def test_parses_md_file_and_returns_requirements(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "requirements.md")
            with open(md_file, "w") as f:
                f.write("# Requirements\n\n- REQ1: The system shall authenticate users\n- REQ2: The system shall log events\n")
            extractor = DocRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 2
            assert result[0].text == "REQ1: The system shall authenticate users"
            assert result[0].source == md_file
            assert result[1].text == "REQ2: The system shall log events"
            assert result[1].source == md_file

    def test_ignores_non_md_files(self):
        """REQ: Scan the reqs directory recursively for files with the .md extension"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "requirements.md")
            with open(md_file, "w") as f:
                f.write("# Requirements\n\n- REQ1: The system shall authenticate users\n")
            txt_file = os.path.join(tmpdir, "notes.txt")
            with open(txt_file, "w") as f:
                f.write("- REQ_FAKE: Should not appear\n")
            extractor = DocRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "REQ1: The system shall authenticate users"

    def test_scans_nested_directories_recursively(self):
        """REQ: Scan the reqs directory recursively for files with the .md extension"""
        with tempfile.TemporaryDirectory() as tmpdir:
            top_file = os.path.join(tmpdir, "top.md")
            with open(top_file, "w") as f:
                f.write("# Requirements\n\n- REQ1: Top level requirement\n")
            nested_dir = os.path.join(tmpdir, "sub", "deep")
            os.makedirs(nested_dir)
            nested_file = os.path.join(nested_dir, "nested.md")
            with open(nested_file, "w") as f:
                f.write("# Requirements\n\n- REQ2: Nested requirement\n")
            extractor = DocRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 2
            assert result[0].text == "REQ1: Top level requirement"
            assert result[0].source == top_file
            assert result[1].text == "REQ2: Nested requirement"
            assert result[1].source == nested_file

    def test_uses_custom_parser(self):
        """REQ: Invoke the MarkdownParser on each discovered markdown file"""
        class CustomParser:
            def parse(self, content):
                return ["CUSTOM_PARSED"]
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "test.md")
            with open(md_file, "w") as f:
                f.write("some content\n")
            extractor = DocRequirementExtractor(parser=CustomParser())
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert result[0].text == "CUSTOM_PARSED"
            assert result[0].source == md_file


class TestConstructor:
    def test_creates_default_parser_when_none(self):
        extractor = DocRequirementExtractor()
        assert extractor.parser is not None

    def test_uses_provided_parser(self):
        class FakeParser:
            pass
        fake = FakeParser()
        extractor = DocRequirementExtractor(parser=fake)
        assert extractor.parser is fake

    def test_pairs_requirement_with_source_file_path(self):
        """REQ: Pair each extracted doc requirement text with its source file path as a DocRequirement named tuple"""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = os.path.join(tmpdir, "reqs.md")
            with open(md_file, "w") as f:
                f.write("# Requirements\n\n- My requirement\n")
            extractor = DocRequirementExtractor()
            result = extractor.extract(tmpdir)
            assert len(result) == 1
            assert isinstance(result[0], DocRequirement)
            assert result[0].text == "My requirement"
            assert result[0].source == md_file