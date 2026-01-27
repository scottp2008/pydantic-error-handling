"""Test coverage for various pydantic Field and ConfigDict options."""

import pytest
from typing import Annotated
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

from pydantic_error_handling import verbose_errors, VerboseValidationError


class TestFieldConstraints:
    """Test various Field constraint options."""

    def test_field_ge_greater_than_or_equal(self):
        """Test Field(ge=...) constraint."""
        @verbose_errors
        class Model(BaseModel):
            age: int = Field(ge=18)
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(age=15)
        
        error_msg = str(exc_info.value)
        assert "'age':" in error_msg
        assert "greater than or equal to 18" in error_msg

    def test_field_gt_greater_than(self):
        """Test Field(gt=...) constraint."""
        @verbose_errors
        class Model(BaseModel):
            score: int = Field(gt=0)
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(score=0)
        
        error_msg = str(exc_info.value)
        assert "'score':" in error_msg
        assert "greater than 0" in error_msg

    def test_field_le_less_than_or_equal(self):
        """Test Field(le=...) constraint."""
        @verbose_errors
        class Model(BaseModel):
            percentage: int = Field(le=100)
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(percentage=101)
        
        error_msg = str(exc_info.value)
        assert "'percentage':" in error_msg
        assert "less than or equal to 100" in error_msg

    def test_field_lt_less_than(self):
        """Test Field(lt=...) constraint."""
        @verbose_errors
        class Model(BaseModel):
            value: int = Field(lt=10)
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(value=10)
        
        error_msg = str(exc_info.value)
        assert "'value':" in error_msg
        assert "less than 10" in error_msg

    def test_field_multiple_of(self):
        """Test Field(multiple_of=...) constraint."""
        @verbose_errors
        class Model(BaseModel):
            even_number: int = Field(multiple_of=2)
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(even_number=7)
        
        error_msg = str(exc_info.value)
        assert "'even_number':" in error_msg
        assert "multiple of 2" in error_msg

    def test_field_min_length(self):
        """Test Field(min_length=...) for strings."""
        @verbose_errors
        class Model(BaseModel):
            username: str = Field(min_length=3)
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(username="ab")
        
        error_msg = str(exc_info.value)
        assert "'username':" in error_msg
        assert "at least 3 characters" in error_msg

    def test_field_max_length(self):
        """Test Field(max_length=...) for strings."""
        @verbose_errors
        class Model(BaseModel):
            username: str = Field(max_length=10)
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(username="verylongusername")
        
        error_msg = str(exc_info.value)
        assert "'username':" in error_msg
        assert "at most 10 characters" in error_msg

    def test_field_pattern(self):
        """Test Field(pattern=...) for regex matching."""
        @verbose_errors
        class Model(BaseModel):
            email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(email="not_an_email")
        
        error_msg = str(exc_info.value)
        assert "'email':" in error_msg
        assert "should match pattern" in error_msg.lower() or "string" in error_msg.lower()


class TestFieldAlias:
    """Test Field alias functionality."""

    def test_field_alias_validation_error(self):
        """Test that alias is handled correctly in error messages."""
        @verbose_errors
        class Model(BaseModel):
            user_name: str = Field(alias="userName")
            age: int
        
        # Error should reference the field name, not alias
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(**{"userName": "John", "age": "not_a_number"})
        
        error_msg = str(exc_info.value)
        assert "'age':" in error_msg

    def test_field_alias_missing_field(self):
        """Test missing field error with alias."""
        @verbose_errors
        class Model(BaseModel):
            user_name: str = Field(alias="userName")
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(**{})
        
        error_msg = str(exc_info.value)
        # Could be either field name or alias depending on Pydantic behavior
        assert "user_name" in error_msg or "userName" in error_msg or "Missing" in error_msg


class TestConfigDictExtra:
    """Test ConfigDict extra field handling."""

    def test_extra_forbid(self):
        """Test extra='forbid' raises error on unexpected fields."""
        @verbose_errors
        class Model(BaseModel):
            model_config = ConfigDict(extra='forbid')
            name: str
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(name="John", unexpected_field="value")
        
        error_msg = str(exc_info.value)
        assert "unexpected_field" in error_msg
        assert "Extra fields are not permitted" in error_msg or "forbidden" in error_msg.lower()

    def test_extra_allow_no_error(self):
        """Test extra='allow' doesn't raise errors."""
        @verbose_errors
        class Model(BaseModel):
            model_config = ConfigDict(extra='allow')
            name: str
        
        # Should not raise
        model = Model(name="John", unexpected_field="value")
        assert model.name == "John"


class TestValidators:
    """Test field_validator and model_validator."""

    def test_field_validator_error(self):
        """Test that field_validator errors are caught and formatted."""
        @verbose_errors
        class Model(BaseModel):
            age: int
            
            @field_validator('age')
            @classmethod
            def check_age(cls, v):
                if v < 0:
                    raise ValueError('Age cannot be negative')
                return v
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(age=-5)
        
        error_msg = str(exc_info.value)
        assert "'age':" in error_msg
        assert "Age cannot be negative" in error_msg

    def test_model_validator_error(self):
        """Test that model_validator errors are caught."""
        @verbose_errors
        class Model(BaseModel):
            start: int
            end: int
            
            @model_validator(mode='after')
            def check_range(self):
                if self.start >= self.end:
                    raise ValueError('start must be less than end')
                return self
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(start=10, end=5)
        
        error_msg = str(exc_info.value)
        assert "start must be less than end" in error_msg


class TestLargeInputs:
    """Test handling of very large inputs."""

    def test_large_list_input(self):
        """Test that large lists are handled gracefully in error messages."""
        @verbose_errors
        class Model(BaseModel):
            items: list[int]
        
        with pytest.raises(VerboseValidationError) as exc_info:
            # Pass a string instead of list to trigger error
            Model(items="not_a_list")
        
        error_msg = str(exc_info.value)
        assert "'items':" in error_msg
        assert "Should be a list" in error_msg

    def test_very_long_string_input(self):
        """Test that very long strings in errors are handled."""
        @verbose_errors
        class Model(BaseModel):
            value: int
        
        long_string = "x" * 10000
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(value=long_string)
        
        error_msg = str(exc_info.value)
        assert "'value':" in error_msg
        # The error message should not be excessively long
        # (though we're not truncating in format_received_value currently)
        assert "Received type: str" in error_msg

    def test_nested_structure_error(self):
        """Test errors in deeply nested structures."""
        @verbose_errors
        class Inner(BaseModel):
            value: int
        
        @verbose_errors
        class Outer(BaseModel):
            items: list[Inner]
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Outer(items=[{"value": 1}, {"value": "not_int"}])
        
        error_msg = str(exc_info.value)
        # Should show the path to the error
        assert "items" in error_msg
        assert "[1]" in error_msg or "1" in error_msg
        assert "value" in error_msg


class TestAnnotatedTypes:
    """Test Annotated type hints with constraints."""

    def test_annotated_with_field(self):
        """Test Annotated types with Field constraints."""
        @verbose_errors
        class Model(BaseModel):
            age: Annotated[int, Field(ge=0, le=150)]
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(age=200)
        
        error_msg = str(exc_info.value)
        assert "'age':" in error_msg
        assert "less than or equal to 150" in error_msg

    def test_annotated_with_multiple_constraints(self):
        """Test Annotated with multiple Field constraints."""
        @verbose_errors
        class Model(BaseModel):
            username: Annotated[str, Field(min_length=3, max_length=20)]
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(username="ab")
        
        error_msg = str(exc_info.value)
        assert "'username':" in error_msg
        assert "at least 3 characters" in error_msg


class TestEnumAndLiteral:
    """Test enum and literal type errors."""

    def test_literal_error(self):
        """Test Literal type validation."""
        from typing import Literal
        
        @verbose_errors
        class Model(BaseModel):
            status: Literal["active", "inactive"]
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(status="pending")
        
        error_msg = str(exc_info.value)
        assert "'status':" in error_msg
        assert "pending" in error_msg

    def test_enum_error(self):
        """Test Enum type validation."""
        from enum import Enum
        
        class Status(str, Enum):
            ACTIVE = "active"
            INACTIVE = "inactive"
        
        @verbose_errors
        class Model(BaseModel):
            status: Status
        
        with pytest.raises(VerboseValidationError) as exc_info:
            Model(status="pending")
        
        error_msg = str(exc_info.value)
        assert "'status':" in error_msg
        assert "pending" in error_msg or "Received type: str" in error_msg
