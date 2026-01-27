"""
pydantic_error_handling - Human-readable verbose error messages for Pydantic validation errors.

Usage:
    from pydantic_error_handling import verbose_errors, VerboseValidationError

    @verbose_errors
    class MyModel(BaseModel):
        name: str
        age: int

    or translate a ValidationError to a string/NicePydanticError via helper functions:
    from pydantic_error_handling import error_to_nice, error_to_string

    try:
        MyModel(name="John", age="twenty")
    except ValidationError as e:
        print(error_to_string(e))
        print(error_to_nice(e))

    # Or manually process errors:
    from pydantic_error_handling import parse_error_details, clean
"""

from pydantic_error_handling._core import (
    _process_error,
    clean,
    error_to_nice,
    error_to_string,
    nice_to_string,
    parse_error_details,
    verbose_to_nice,
)
from pydantic_error_handling.decorator import verbose_errors
from pydantic_error_handling.models.models import (
    ErrorType,
    NicePydanticError,
    PydanticErrorsVerbose,
    VerboseValidationError,
    VerboseValidationErrorData,
)

__all__ = [
    # Main API - Decorator, stable
    "verbose_errors",
    # Main API - Function Helpers, stable
    "error_to_nice",
    "error_to_string",
    "nice_to_string",
    # Utility functions 
    "clean",
    "parse_error_details",
    "verbose_to_nice",
    # Types/Classes
    "ErrorType",
    "NicePydanticError",
    "PydanticErrorsVerbose",
    "VerboseValidationError",
    "VerboseValidationErrorData",
    # Internal (for decorator)
    "_process_error",
]

