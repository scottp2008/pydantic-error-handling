import pytest
import pydantic
from pydantic_error_handling import verbose_errors, VerboseValidationError


@verbose_errors
class ExampleModel(pydantic.BaseModel):
    name: str
    age: int
    email: str
    value: int = pydantic.Field(gt=5, lt=15)


class TestDecoratorHappyPath:
    """Test that valid data works normally with the decorator."""

    def test_valid_kwargs(self):
        model = ExampleModel(name="John Doe", age=30, email="john@example.com", value=10)
        assert model.name == "John Doe"
        assert model.age == 30
        assert model.value == 10

    def test_valid_json(self):
        json_blob = '{"name": "Jane", "age": 25, "email": "jane@example.com", "value": 10}'
        model = ExampleModel.model_validate_json(json_blob)
        assert model.name == "Jane"
        assert model.age == 25


class TestDecoratorRaisesVerboseError:
    """Test that invalid data raises VerboseValidationError with proper messages."""

    def test_wrong_type_raises_verbose_error(self):
        with pytest.raises(VerboseValidationError) as exc_info:
            ExampleModel(name="John", age="not an int", email="john@example.com", value=10)

        # Check we got a VerboseValidationError
        error = exc_info.value
        assert isinstance(error, VerboseValidationError)
        
        # Check we have verbose error messages
        assert len(error.verbose_errors) == 1
        assert "'age':" in error.verbose_errors[0]
        assert "Received type: str" in error.verbose_errors[0]

    def test_constraint_violation_raises_verbose_error(self):
        with pytest.raises(VerboseValidationError) as exc_info:
            ExampleModel(name="John", age=30, email="john@example.com", value=100)  # value > 15

        error = exc_info.value
        assert len(error.verbose_errors) == 1
        assert "'value':" in error.verbose_errors[0]
        assert "less than 15" in error.verbose_errors[0]

    def test_missing_field_raises_verbose_error(self):
        with pytest.raises(VerboseValidationError) as exc_info:
            ExampleModel(age=30, email="john@example.com", value=10)  # missing name

        error = exc_info.value
        assert len(error.verbose_errors) == 1
        assert "Missing required field: name" in error.verbose_errors[0]

    def test_multiple_errors(self):
        with pytest.raises(VerboseValidationError) as exc_info:
            ExampleModel(name=123, age="bad", email="test@example.com", value=10)

        error = exc_info.value
        assert len(error.verbose_errors) == 2  # name wrong type, age wrong type

    def test_invalid_json_raises_verbose_error(self):
        bad_json = '{"name": "John", "age": 30, email: "missing quotes"}'
        
        with pytest.raises(VerboseValidationError) as exc_info:
            ExampleModel.model_validate_json(bad_json)

        error = exc_info.value
        assert len(error.verbose_errors) == 1
        assert "Invalid JSON" in error.verbose_errors[0]

    def test_to_dict_for_api_response(self):
        with pytest.raises(VerboseValidationError) as exc_info:
            ExampleModel(name=123, age="bad", email="test@example.com", value=10)

        error = exc_info.value
        result = error.to_dict()
        
        assert "detail" in result
        assert isinstance(result["detail"], list)
        assert len(result["detail"]) == 2
        assert "'name':" in result["detail"][0] or "'name':" in result["detail"][1]


class TestModelValidateMethod:
    """Test that model_validate() is properly wrapped (lines 48-51 in decorator.py)."""

    def test_model_validate_with_valid_dict(self):
        """Test model_validate() with valid data."""
        data = {"name": "Alice", "age": 28, "email": "alice@example.com", "value": 8}
        model = ExampleModel.model_validate(data)
        assert model.name == "Alice"
        assert model.age == 28
        assert model.value == 8

    def test_model_validate_with_invalid_type(self):
        """Test model_validate() raises VerboseValidationError on type error."""
        data = {"name": "Bob", "age": "not_a_number", "email": "bob@example.com", "value": 7}
        
        with pytest.raises(VerboseValidationError) as exc_info:
            ExampleModel.model_validate(data)
        
        error = exc_info.value
        assert isinstance(error, VerboseValidationError)
        assert len(error.verbose_errors) == 1
        assert "'age':" in error.verbose_errors[0]
        assert "Received type: str" in error.verbose_errors[0]

    def test_model_validate_with_missing_field(self):
        """Test model_validate() raises VerboseValidationError on missing field."""
        data = {"age": 35, "email": "charlie@example.com", "value": 9}  # missing 'name'
        
        with pytest.raises(VerboseValidationError) as exc_info:
            ExampleModel.model_validate(data)
        
        error = exc_info.value
        assert len(error.verbose_errors) == 1
        assert "Missing required field: name" in error.verbose_errors[0]

    def test_model_validate_with_constraint_violation(self):
        """Test model_validate() raises VerboseValidationError on constraint error."""
        data = {"name": "Dave", "age": 40, "email": "dave@example.com", "value": 2}  # value < 5
        
        with pytest.raises(VerboseValidationError) as exc_info:
            ExampleModel.model_validate(data)
        
        error = exc_info.value
        assert len(error.verbose_errors) == 1
        assert "'value':" in error.verbose_errors[0]
        assert "greater than 5" in error.verbose_errors[0]

    def test_model_validate_with_multiple_errors(self):
        """Test model_validate() handles multiple validation errors."""
        data = {"name": 999, "age": "invalid", "email": "eve@example.com", "value": 10}
        
        with pytest.raises(VerboseValidationError) as exc_info:
            ExampleModel.model_validate(data)
        
        error = exc_info.value
        assert len(error.verbose_errors) == 2
        # Should have errors for both 'name' and 'age'
        error_str = " ".join(error.verbose_errors)
        assert "'name':" in error_str
        assert "'age':" in error_str


class TestVerboseValidationErrorMethods:
    """Test VerboseValidationError utility methods (line 224 in models.py)."""

    def test_errors_method_returns_original_errors(self):
        """Test that .errors() returns the original Pydantic error details."""
        with pytest.raises(VerboseValidationError) as exc_info:
            ExampleModel(name=123, age="bad", email="test@example.com", value=10)
        
        error = exc_info.value
        original_errors = error.errors()
        
        # Should return list of error dicts
        assert isinstance(original_errors, list)
        assert len(original_errors) == 2
        
        # Each error should have standard Pydantic error dict structure
        for err in original_errors:
            assert "type" in err
            assert "loc" in err
            assert "msg" in err
            assert "input" in err

    def test_error_count_method(self):
        """Test that error_count() returns correct number of errors."""
        with pytest.raises(VerboseValidationError) as exc_info:
            ExampleModel(name=123, age="bad", email="test@example.com", value=10)
        
        error = exc_info.value
        assert error.error_count() == 2
        assert error.error_count() == len(error.verbose_errors)
