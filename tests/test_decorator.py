import pytest
import pydantic
from pydantic_errors import verbose_errors, VerboseValidationError


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
