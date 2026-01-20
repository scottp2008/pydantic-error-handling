"""
pydantic_errors - Human-readable verbose error messages for Pydantic validation errors.

Usage:
    from pydantic_errors import verbose_errors, VerboseValidationError

    @verbose_errors
    class MyModel(BaseModel):
        name: str
        age: int

    # Or manually process errors:
    from pydantic_errors import parse_error_details, clean
"""

from pydantic_errors._core import parse_error_details, clean, _process_error
from pydantic_errors.decorator import verbose_errors
from pydantic_errors.models.models import (
    ErrorType,
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
    "PydanticErrorsVerbose",
    "VerboseValidationError",
    "VerboseValidationErrorData",
    # Internal (for decorator)
    "_process_error",
]

