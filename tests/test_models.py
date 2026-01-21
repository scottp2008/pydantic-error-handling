"""Unit tests for pydantic_errors models - NicePydanticError, field_path, etc."""

import pytest
from pydantic import BaseModel, field_validator

from pydantic_errors import verbose_errors, VerboseValidationError, NicePydanticError
from pydantic_errors.models.models import PydanticErrorsVerbose, PYDANTIC_FUNCTION_LOC_PATTERNS


class TestFieldPathFiltering:
    """Test that field_path correctly filters out validator patterns."""

    def test_simple_field_path(self):
        """Simple field name should pass through unchanged."""
        error_details = {
            "type": "string_type",
            "loc": ("name",),
            "msg": "Input should be a valid string",
            "input": 123,
        }
        error = PydanticErrorsVerbose(error_details)
        assert error.field_path == ("name",)

    def test_nested_field_path(self):
        """Nested fields should pass through unchanged."""
        error_details = {
            "type": "string_type",
            "loc": ("address", "city"),
            "msg": "Input should be a valid string",
            "input": 123,
        }
        error = PydanticErrorsVerbose(error_details)
        assert error.field_path == ("address", "city")

    def test_list_index_in_path(self):
        """List indices (integers) should be preserved."""
        error_details = {
            "type": "string_type",
            "loc": ("items", 0, "name"),
            "msg": "Input should be a valid string",
            "input": 123,
        }
        error = PydanticErrorsVerbose(error_details)
        assert error.field_path == ("items", 0, "name")

    def test_function_before_filtered(self):
        """function-before[...] validator patterns should be filtered out."""
        error_details = {
            "type": "value_error",
            "loc": ("serial_number", "function-before[serial_number_validator(), str]"),
            "msg": "Value error, too long",
            "input": "12345678901234567890",
        }
        error = PydanticErrorsVerbose(error_details)
        assert error.field_path == ("serial_number",)

    def test_function_after_filtered(self):
        """function-after[...] validator patterns should be filtered out."""
        error_details = {
            "type": "value_error",
            "loc": ("email", "function-after[validate_email(), str]"),
            "msg": "Value error, invalid email",
            "input": "bad",
        }
        error = PydanticErrorsVerbose(error_details)
        assert error.field_path == ("email",)

    def test_function_wrap_filtered(self):
        """function-wrap[...] validator patterns should be filtered out."""
        error_details = {
            "type": "value_error",
            "loc": ("data", "function-wrap[wrap_validator(), dict]"),
            "msg": "Value error",
            "input": {},
        }
        error = PydanticErrorsVerbose(error_details)
        assert error.field_path == ("data",)

    def test_function_plain_filtered(self):
        """function-plain[...] validator patterns should be filtered out."""
        error_details = {
            "type": "value_error",
            "loc": ("value", "function-plain[plain_validator(), int]"),
            "msg": "Value error",
            "input": 0,
        }
        error = PydanticErrorsVerbose(error_details)
        assert error.field_path == ("value",)

    def test_nested_with_validator_filtered(self):
        """Nested path with validator should filter only the validator part."""
        error_details = {
            "type": "value_error",
            "loc": ("users", 2, "email", "function-before[validate(), str]"),
            "msg": "Value error",
            "input": "bad",
        }
        error = PydanticErrorsVerbose(error_details)
        assert error.field_path == ("users", 2, "email")

    def test_empty_loc(self):
        """Empty loc should return empty tuple."""
        error_details = {
            "type": "value_error",
            "loc": (),
            "msg": "Value error",
            "input": {},
        }
        error = PydanticErrorsVerbose(error_details)
        assert error.field_path == ()


class TestNicePydanticError:
    """Test NicePydanticError structure and from_verbose conversion."""

    def test_from_verbose_basic(self):
        """NicePydanticError should capture all fields from PydanticErrorsVerbose."""
        error_details = {
            "type": "string_type",
            "loc": ("name",),
            "msg": "Input should be a valid string",
            "input": 123,
        }
        verbose = PydanticErrorsVerbose(error_details)
        verbose.verbose_error = "'name': Input should be a valid string. Received type: int, value: 123"
        
        nice = NicePydanticError.from_verbose(verbose)
        
        assert nice.field == "name"
        assert nice.field_path == ("name",)
        assert nice.message == "'name': Input should be a valid string. Received type: int, value: 123"
        assert nice.error_type == "string_type"
        assert nice.input_value == 123

    def test_from_verbose_with_filtered_path(self):
        """NicePydanticError should have clean field_path without validator cruft."""
        error_details = {
            "type": "value_error",
            "loc": ("serial", "function-before[validate(), str]"),
            "msg": "Too long",
            "input": "12345",
        }
        verbose = PydanticErrorsVerbose(error_details)
        verbose.verbose_error = "Too long"
        
        nice = NicePydanticError.from_verbose(verbose)
        
        # field has the full path (for display/debugging)
        assert nice.field == "serial.function-before[validate(), str]"
        # field_path is clean (for UI matching)
        assert nice.field_path == ("serial",)

    def test_model_dump_serializable(self):
        """NicePydanticError should be JSON serializable via model_dump."""
        error_details = {
            "type": "int_parsing",
            "loc": ("age",),
            "msg": "Input should be a valid integer",
            "input": "not a number",
        }
        verbose = PydanticErrorsVerbose(error_details)
        verbose.verbose_error = "'age': Input should be a valid integer"
        
        nice = NicePydanticError.from_verbose(verbose)
        dumped = nice.model_dump()
        
        assert dumped == {
            "field": "age",
            "field_path": ("age",),
            "message": "'age': Input should be a valid integer",
            "error_type": "int_parsing",
            "input_value": "not a number",
        }


class TestStructuredErrorsIntegration:
    """Test that structured_errors are populated correctly in VerboseValidationError."""

    def test_structured_errors_populated(self):
        """VerboseValidationError should have structured_errors list."""
        @verbose_errors
        class TestModel(BaseModel):
            name: str
            age: int

        with pytest.raises(VerboseValidationError) as exc_info:
            TestModel(name=123, age="bad")

        error = exc_info.value
        
        # Should have 2 structured errors
        assert len(error.structured_errors) == 2
        
        # Each should be a NicePydanticError
        for err in error.structured_errors:
            assert isinstance(err, NicePydanticError)

    def test_structured_errors_match_verbose_errors(self):
        """Each structured error message should match its verbose_error counterpart."""
        @verbose_errors
        class TestModel(BaseModel):
            name: str

        with pytest.raises(VerboseValidationError) as exc_info:
            TestModel(name=123)

        error = exc_info.value
        
        assert len(error.structured_errors) == 1
        assert len(error.verbose_errors) == 1
        
        # Messages should match
        assert error.structured_errors[0].message == error.verbose_errors[0]

    def test_structured_errors_with_validator(self):
        """Structured errors should have clean field_path even with validators."""
        @verbose_errors
        class TestModel(BaseModel):
            code: str

            @field_validator('code')
            @classmethod
            def validate_code(cls, v):
                if len(v) > 5:
                    raise ValueError("Code too long")
                return v

        with pytest.raises(VerboseValidationError) as exc_info:
            TestModel(code="123456789")

        error = exc_info.value
        
        assert len(error.structured_errors) == 1
        structured = error.structured_errors[0]
        
        # field_path should be clean (no validator cruft)
        assert structured.field_path == ("code",)
        # error_type should be value_error
        assert structured.error_type == "value_error"


class TestPydanticFunctionLocPatterns:
    """Test that the pattern list covers expected validator types."""

    def test_all_expected_patterns_present(self):
        """Ensure we have patterns for all known validator modes."""
        expected = ["function-before[", "function-after[", "function-wrap[", "function-plain["]
        for pattern in expected:
            assert pattern in PYDANTIC_FUNCTION_LOC_PATTERNS, f"Missing pattern: {pattern}"

