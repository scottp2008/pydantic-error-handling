"""
pydantic_error_handling - Human-readable verbose error messages for Pydantic validation errors.

Usage:
    from pydantic_error_handling import verbose_errors, VerboseValidationError

    @verbose_errors
    class MyModel(BaseModel):
        name: str
        age: int

    # Or manually process errors:
    from pydantic_error_handling import parse_error_details, clean
"""

from pydantic_error_handling._core import parse_error_details, clean, _process_error
from pydantic_error_handling.decorator import verbose_errors
from pydantic_error_handling.models.models import (
    ErrorType,
    NicePydanticError,
    PydanticErrorsVerbose,
    VerboseValidationError,
    VerboseValidationErrorData,
)

__all__ = [
    # Main API
    "verbose_errors",
    "parse_error_details",
    "clean",
    # Types/Classes
    "ErrorType",
    "NicePydanticError",
    "PydanticErrorsVerbose",
    "VerboseValidationError",
    "VerboseValidationErrorData",
    # Internal (for decorator)
    "_process_error",
]

