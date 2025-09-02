"""Tests for formatting functions."""

import pytest
from datetime import datetime

from medium_mcp.formatting import normalize_tag, convert_to_string


class TestNormalizeTag:
    """Test normalize_tag function."""

    def test_basic_tag_normalization(self):
        """Test basic tag normalization with spaces."""
        assert normalize_tag("data science") == "data-science"
        assert normalize_tag("machine learning") == "machine-learning"
        assert normalize_tag("artificial intelligence") == "artificial-intelligence"

    def test_uppercase_normalization(self):
        """Test normalization of uppercase tags."""
        assert normalize_tag("DATA SCIENCE") == "data-science"
        assert normalize_tag("AI") == "ai"
        assert normalize_tag("Machine Learning") == "machine-learning"
        assert normalize_tag("LLM") == "llm"

    def test_mixed_case_normalization(self):
        """Test normalization of mixed case tags."""
        assert normalize_tag("Data Science") == "data-science"
        assert normalize_tag("PyTorch Tutorial") == "pytorch-tutorial"
        assert normalize_tag("JavaScript Tips") == "javascript-tips"

    def test_multiple_spaces(self):
        """Test normalization with multiple spaces."""
        assert normalize_tag("deep  learning") == "deep--learning"
        assert normalize_tag("natural   language   processing") == "natural---language---processing"

    def test_already_normalized_tags(self):
        """Test tags that are already in correct format."""
        assert normalize_tag("data-science") == "data-science"
        assert normalize_tag("ai") == "ai"
        assert normalize_tag("machine-learning") == "machine-learning"

    def test_single_word_tags(self):
        """Test single word tags."""
        assert normalize_tag("python") == "python"
        assert normalize_tag("PYTHON") == "python"
        assert normalize_tag("JavaScript") == "javascript"

    def test_empty_and_none_tags(self):
        """Test empty and None tag handling."""
        assert normalize_tag("") == ""
        assert normalize_tag(None) == None

    def test_tags_with_special_characters(self):
        """Test tags with numbers and other characters."""
        assert normalize_tag("Python 3.11") == "python-3.11"
        assert normalize_tag("Web 2.0") == "web-2.0"
        assert normalize_tag("C++ Programming") == "c++-programming"

    def test_leading_trailing_spaces(self):
        """Test tags with leading/trailing spaces."""
        assert normalize_tag("  data science  ") == "--data-science--"
        assert normalize_tag(" python ") == "-python-"


class TestConvertToString:
    """Test convert_to_string function."""

    def test_none_values(self):
        """Test conversion of None values."""
        assert convert_to_string(None) == ""
        
    def test_empty_string(self):
        """Test conversion of empty string."""
        assert convert_to_string("") == ""

    def test_regular_strings(self):
        """Test conversion of regular strings."""
        assert convert_to_string("hello") == "hello"
        assert convert_to_string("test string") == "test string"

    def test_numbers(self):
        """Test conversion of numbers."""
        assert convert_to_string(42) == "42"
        assert convert_to_string(3.14) == "3.14"
        # 0 is falsy, so it returns empty string
        assert convert_to_string(0) == ""

    def test_boolean_values(self):
        """Test conversion of boolean values."""
        assert convert_to_string(True) == "True"
        # False is falsy, so it returns empty string
        assert convert_to_string(False) == ""

    def test_datetime_objects(self):
        """Test conversion of datetime objects."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        result = convert_to_string(dt)
        assert result == "2024-01-15T10:30:45"

    def test_objects_with_username(self):
        """Test conversion of objects with username attribute."""
        class MockUser:
            def __init__(self, username):
                self.username = username

        user = MockUser("testuser")
        assert convert_to_string(user) == "testuser"

        # Test with None username - falls back to str() since username is falsy
        user_none = MockUser(None)
        # This will use str() of the object since username is None (falsy)
        result = convert_to_string(user_none)
        assert "MockUser object" in result

        # Test with empty username - also falls back to str() since empty string is falsy
        user_empty = MockUser("")
        result = convert_to_string(user_empty)
        assert "MockUser object" in result

    def test_objects_with_isoformat(self):
        """Test conversion of objects with isoformat method."""
        class MockDate:
            def isoformat(self):
                return "2024-01-15"

        date_obj = MockDate()
        assert convert_to_string(date_obj) == "2024-01-15"

    def test_complex_objects(self):
        """Test conversion of complex objects."""
        class ComplexObject:
            def __init__(self, value):
                self.value = value
            
            def __str__(self):
                return f"ComplexObject({self.value})"

        obj = ComplexObject("test")
        assert convert_to_string(obj) == "ComplexObject(test)"

    def test_list_and_dict(self):
        """Test conversion of lists and dictionaries."""
        assert convert_to_string([1, 2, 3]) == "[1, 2, 3]"
        assert convert_to_string({"key": "value"}) == "{'key': 'value'}"

    def test_priority_username_over_str(self):
        """Test that username attribute takes priority over __str__."""
        class UserWithStr:
            def __init__(self, username):
                self.username = username
            
            def __str__(self):
                return "should not be used"

        user = UserWithStr("priorityuser")
        assert convert_to_string(user) == "priorityuser"

    def test_priority_isoformat_over_str(self):
        """Test that isoformat method takes priority over __str__."""
        class DateWithStr:
            def isoformat(self):
                return "2024-01-15T12:00:00"
            
            def __str__(self):
                return "should not be used"

        date_obj = DateWithStr()
        assert convert_to_string(date_obj) == "2024-01-15T12:00:00"