"""Tests for utility functions."""

import pytest

from medium_mcp.utils import safe_getattr


class TestSafeGetattr:
    """Test safe_getattr function."""

    def test_existing_attribute(self):
        """Test getting an existing attribute."""
        class TestObject:
            def __init__(self):
                self.name = "test"
                self.value = 42

        obj = TestObject()
        assert safe_getattr(obj, "name", "default") == "test"
        assert safe_getattr(obj, "value", 0) == 42

    def test_missing_attribute_with_default(self):
        """Test getting a missing attribute returns default."""
        class TestObject:
            pass

        obj = TestObject()
        assert safe_getattr(obj, "missing", "default") == "default"
        assert safe_getattr(obj, "nonexistent", 42) == 42
        assert safe_getattr(obj, "undefined", None) is None

    def test_none_attribute_value(self):
        """Test attribute that exists but has None value."""
        class TestObject:
            def __init__(self):
                self.nullable_field = None
                self.valid_field = "value"

        obj = TestObject()
        # When attribute is None, should return the default
        assert safe_getattr(obj, "nullable_field", "default") == "default"
        assert safe_getattr(obj, "valid_field", "default") == "value"

    def test_different_default_types(self):
        """Test various default value types."""
        class TestObject:
            pass

        obj = TestObject()
        
        # String default
        assert safe_getattr(obj, "missing", "default_string") == "default_string"
        
        # Integer default
        assert safe_getattr(obj, "missing", 100) == 100
        
        # List default
        assert safe_getattr(obj, "missing", []) == []
        
        # Dict default
        assert safe_getattr(obj, "missing", {}) == {}
        
        # Boolean default
        assert safe_getattr(obj, "missing", True) is True
        assert safe_getattr(obj, "missing", False) is False

    def test_zero_and_empty_values(self):
        """Test that zero and empty values are preserved when not None."""
        class TestObject:
            def __init__(self):
                self.zero_value = 0
                self.empty_string = ""
                self.empty_list = []
                self.empty_dict = {}
                self.false_value = False

        obj = TestObject()
        
        # These should return the actual values, not defaults
        assert safe_getattr(obj, "zero_value", 42) == 0
        assert safe_getattr(obj, "empty_string", "default") == ""
        assert safe_getattr(obj, "empty_list", ["default"]) == []
        assert safe_getattr(obj, "empty_dict", {"key": "value"}) == {}
        assert safe_getattr(obj, "false_value", True) is False

    def test_with_builtin_types(self):
        """Test safe_getattr with built-in Python types."""
        # String
        assert safe_getattr("hello", "upper", None) is not None  # method exists
        assert safe_getattr("hello", "nonexistent", "default") == "default"
        
        # List
        assert safe_getattr([1, 2, 3], "append", None) is not None  # method exists
        assert safe_getattr([1, 2, 3], "nonexistent", "default") == "default"
        
        # Dict
        assert safe_getattr({"key": "value"}, "keys", None) is not None  # method exists
        assert safe_getattr({"key": "value"}, "nonexistent", "default") == "default"

    def test_with_none_object(self):
        """Test safe_getattr when object itself is None."""
        # safe_getattr uses getattr() which handles None gracefully, returning default
        result = safe_getattr(None, "any_attr", "default")
        assert result == "default"

    def test_attribute_with_none_then_valid_value(self):
        """Test that None values are properly handled vs missing attributes."""
        class TestObject:
            def __init__(self):
                self.sometimes_none = None
                
        obj = TestObject()
        
        # Attribute exists but is None - should return default
        assert safe_getattr(obj, "sometimes_none", "fallback") == "fallback"
        
        # Now set a valid value
        obj.sometimes_none = "valid_value"
        assert safe_getattr(obj, "sometimes_none", "fallback") == "valid_value"

    def test_dynamic_attributes(self):
        """Test with dynamically added attributes."""
        class DynamicObject:
            pass

        obj = DynamicObject()
        
        # Initially missing
        assert safe_getattr(obj, "dynamic_attr", "default") == "default"
        
        # Add attribute dynamically
        obj.dynamic_attr = "dynamic_value"
        assert safe_getattr(obj, "dynamic_attr", "default") == "dynamic_value"
        
        # Set to None
        obj.dynamic_attr = None
        assert safe_getattr(obj, "dynamic_attr", "default") == "default"

    def test_property_attributes(self):
        """Test with property attributes."""
        class PropertyObject:
            def __init__(self):
                self._value = "hidden_value"
                self._none_value = None
            
            @property
            def value(self):
                return self._value
            
            @property  
            def none_property(self):
                return self._none_value

        obj = PropertyObject()
        
        # Property with value
        assert safe_getattr(obj, "value", "default") == "hidden_value"
        
        # Property returning None
        assert safe_getattr(obj, "none_property", "default") == "default"
        
        # Missing property
        assert safe_getattr(obj, "missing_property", "default") == "default"

    def test_complex_default_objects(self):
        """Test with complex default objects."""
        class TestObject:
            pass

        obj = TestObject()
        
        class ComplexDefault:
            def __init__(self, value):
                self.value = value

        default_obj = ComplexDefault("complex")
        result = safe_getattr(obj, "missing", default_obj)
        
        assert result is default_obj
        assert result.value == "complex"