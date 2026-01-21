"""Quick test to verify custom omit_patterns works"""
from pydantic import BaseModel
from pydantic_error_handling import verbose_errors, VerboseValidationError
import pytest


# Test 1: Without custom patterns
@verbose_errors
class ModelWithoutCustom(BaseModel):
    name: str


# Test 2: With custom patterns
@verbose_errors(omit_patterns=["Problem", "Issue"])
class ModelWithCustom(BaseModel):
    name: str


def test_basic_decorator_still_works():
    """Ensure @verbose_errors without parentheses still works"""
    with pytest.raises(VerboseValidationError) as exc_info:
        ModelWithoutCustom(name=123)
    
    assert exc_info.value.error_count() == 1
    assert "name" in exc_info.value.verbose_errors[0]
    print("✓ Basic decorator works")


def test_decorator_with_custom_patterns():
    """Ensure @verbose_errors(omit_patterns=[...]) works"""
    with pytest.raises(VerboseValidationError) as exc_info:
        ModelWithCustom(name=456)
    
    assert exc_info.value.error_count() == 1
    assert "name" in exc_info.value.verbose_errors[0]
    print("✓ Decorator with custom patterns works")


def test_custom_patterns_filter_field_path():
    """Verify custom patterns actually filter from field_path"""
    from pydantic_error_handling.models.models import PydanticErrorsVerbose
    
    # Simulate an error with "Problem" in the loc
    error_dict = {
        "type": "string_type",
        "loc": ("Problem", "field_name"),
        "msg": "Input should be a valid string",
        "input": 123,
    }
    
    # Without custom patterns
    error_without = PydanticErrorsVerbose(error_dict)
    assert error_without.field_path == ("Problem", "field_name")
    
    # With custom patterns
    error_with = PydanticErrorsVerbose(error_dict, omit_patterns=["Problem"])
    assert error_with.field_path == ("field_name",)  # "Problem" filtered out!
    
    print("✓ Custom patterns filter field_path correctly")


if __name__ == "__main__":
    test_basic_decorator_still_works()
    test_decorator_with_custom_patterns()
    test_custom_patterns_filter_field_path()
    print("\n🎉 All custom pattern tests passed!")
