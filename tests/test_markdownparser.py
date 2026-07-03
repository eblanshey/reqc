import pytest
from reqc import MarkdownParser


class TestMarkdownParser:
    def test_detects_requirements_heading(self):
        """REQ: Detect headings that contain the substring Requirements or Specifications with a case-sensitive match"""
        parser = MarkdownParser()
        content = """# Requirements

- Login must support OAuth2
- Password must be at least 8 chars
"""
        result = parser.parse(content)
        assert result == ["Login must support OAuth2", "Password must be at least 8 chars"]

    def test_detects_specifications_heading(self):
        """REQ: Detect headings that contain the substring Requirements or Specifications with a case-sensitive match"""
        parser = MarkdownParser()
        content = """# Specifications

- API must return JSON
- API must use HTTPS
"""
        result = parser.parse(content)
        assert result == ["API must return JSON", "API must use HTTPS"]

    def test_substring_anywhere_in_heading(self):
        """REQ: Allow the substring Requirements or Specifications to appear anywhere within the heading text"""
        parser = MarkdownParser()
        content = """## API Requirements v2

- Rate limiting at 100 req/min
- Throttle after 1000 req/hour
"""
        result = parser.parse(content)
        assert result == ["Rate limiting at 100 req/min", "Throttle after 1000 req/hour"]

    def test_extract_asterisk_list_items(self):
        """REQ: Support unordered list markers using a dash, an asterisk, or a plus sign"""
        parser = MarkdownParser()
        content = """# Requirements

* Item with asterisk
* Another asterisk item
"""
        result = parser.parse(content)
        assert result == ["Item with asterisk", "Another asterisk item"]

    def test_extract_plus_list_items(self):
        """REQ: Support unordered list markers using a dash, an asterisk, or a plus sign"""
        parser = MarkdownParser()
        content = """# Requirements

+ Item with plus
+ Another plus item
"""
        result = parser.parse(content)
        assert result == ["Item with plus", "Another plus item"]

    def test_extract_unordered_list_items_as_individual_requirements(self):
        """REQ: Extract unordered list items from a requirements section as individual requirements
        """
        parser = MarkdownParser()
        content = """# Requirements

- First requirement
- Second requirement
- Third requirement
"""
        result = parser.parse(content)
        assert len(result) == 3
        assert "First requirement" in result
        assert "Second requirement" in result
        assert "Third requirement" in result

    def test_nested_list_items_are_separate(self):
        """REQ: Treat all list items as separate requirements regardless of nesting depth"""
        parser = MarkdownParser()
        content = """# Requirements

- Top level item
  - Nested item one
    - Nested item two
- Another top level
"""
        result = parser.parse(content)
        assert result == ["Top level item", "Nested item one", "Nested item two", "Another top level"]

    def test_preserve_raw_markdown_formatting(self):
        """REQ: Preserve raw markdown formatting in requirement text"""
        parser = MarkdownParser()
        content = """# Requirements

- Must use **bold** for emphasis
- Call `api_endpoint` with token
"""
        result = parser.parse(content)
        assert result == ["Must use **bold** for emphasis", "Call `api_endpoint` with token"]

    def test_ignore_empty_list_items(self):
        """REQ: Silently ignore empty list items"""
        parser = MarkdownParser()
        content = """# Requirements

- Valid item
-
-   -
- Another valid item
"""
        result = parser.parse(content)
        assert result == ["Valid item", "Another valid item"]

    def test_skip_fenced_code_blocks(self):
        """REQ: Skip content inside fenced code blocks"""
        parser = MarkdownParser()
        content = """# Requirements

- Real requirement one

```
- Not a requirement
- Also not a requirement
```

- Real requirement two
"""
        result = parser.parse(content)
        assert result == ["Real requirement one", "Real requirement two"]

    def test_skip_blockquotes(self):
        """REQ: Skip content inside blockquotes"""
        parser = MarkdownParser()
        content = """# Requirements

- Real requirement one

> - Not a requirement
> - Also not a requirement

- Real requirement two
"""
        result = parser.parse(content)
        assert result == ["Real requirement one", "Real requirement two"]

    def test_end_section_at_equal_or_higher_heading(self):
        """REQ: End a requirements section at the next heading of equal or higher level"""
        parser = MarkdownParser()
        content = """## Requirements

- Requirement in section
  - Nested requirement

### Subsection

- Subsection item

## Other Section

- Should not be included
"""
        result = parser.parse(content)
        assert result == ["Requirement in section", "Nested requirement", "Subsection item"]

    def test_match_headings_any_level_h1_through_h6(self):
        """REQ: Match headings at any level from H1 through H6"""
        parser = MarkdownParser()
        for level in range(1, 7):
            heading = '#' * level + ' Requirements'
            content = f'{heading}\n\n- Item {level}\n'
            result = parser.parse(content)
            assert result == [f'Item {level}'], f'Failed for H{level}'

    def test_treat_each_line_independently_without_joining_multiline(self):
        """REQ: Treat each line within a list item independently without joining multiline content"""
        parser = MarkdownParser()
        content = """# Requirements

- Item line one
  continued line
- Second item
"""
        result = parser.parse(content)
        assert "Item line one" in result
        assert "Second item" in result

    def test_strip_leading_trailing_whitespace(self):
        """REQ: Strip leading and trailing whitespace from each requirement text"""
        parser = MarkdownParser()
        content = """# Requirements

-   Padded item  
- Normal item
"""
        result = parser.parse(content)
        assert result == ["Padded item", "Normal item"]