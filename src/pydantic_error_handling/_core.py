"""Core logic for transforming Pydantic validation errors into verbose messages."""

from functools import partial
from typing import Callable

import pydantic
from pydantic_error_handling.models.models import (
    ErrorType,
    NicePydanticError,
    PydanticErrorsVerbose,
    VerboseValidationError,
    VerboseValidationErrorData,
)
from pydantic_error_handling import error_handling

# Type alias for error handler functions
ErrorHandler = Callable[[PydanticErrorsVerbose], str]

# Registry mapping ErrorType to handler function
ERROR_HANDLERS: dict[ErrorType, ErrorHandler] = {
    # Bytes errors
    ErrorType.BYTES_TOO_SHORT: partial(error_handling.too_short_error, unit="bytes"),
    ErrorType.BYTES_TOO_LONG: partial(error_handling.too_long_error, unit="bytes"),

    # Collection errors
    ErrorType.LIST_TYPE: partial(error_handling.verbose_type_error, expected_type=list),
    ErrorType.SET_TYPE: partial(error_handling.verbose_type_error, expected_type=set),
    ErrorType.TUPLE_TYPE: partial(error_handling.verbose_type_error, expected_type=tuple),
    ErrorType.DICT_TYPE: partial(error_handling.verbose_type_error, expected_type=dict),
    ErrorType.FROZEN_SET_TYPE: partial(error_handling.verbose_type_error, expected_type=frozenset),
    ErrorType.TOO_SHORT: partial(error_handling.too_short_error, unit="items"),
    ErrorType.TOO_LONG: partial(error_handling.too_long_error, unit="items"),
    
    # Datetime parsing errors
    ErrorType.DATE_FROM_DATETIME_PARSING: error_handling.datetime_parsing_error,
    ErrorType.DATETIME_FROM_DATE_PARSING: error_handling.datetime_parsing_error,
    ErrorType.TIME_PARSING: error_handling.datetime_parsing_error,
    ErrorType.TIME_DELTA_PARSING: error_handling.datetime_parsing_error,
    
    # Datetime constraint errors
    ErrorType.DATE_PAST: error_handling.verbose_error_str_generic,
    ErrorType.DATE_FUTURE: error_handling.verbose_error_str_generic,
    ErrorType.DATETIME_PAST: error_handling.verbose_error_str_generic,
    ErrorType.DATETIME_FUTURE: error_handling.verbose_error_str_generic,
    ErrorType.TIMEZONE_AWARE: error_handling.verbose_error_str_generic,
    ErrorType.TIMEZONE_NAIVE: error_handling.verbose_error_str_generic,
    
    # Decimal errors
    ErrorType.DECIMAL_PARSING: error_handling.verbose_error_str_generic,
    ErrorType.DECIMAL_MAX_DIGITS: error_handling.verbose_error_str_generic,
    ErrorType.DECIMAL_MAX_PLACES: error_handling.verbose_error_str_generic,
    
    # Enum errors
    ErrorType.ENUM: error_handling.verbose_error_str_generic,
    ErrorType.LITERAL_ERROR: error_handling.verbose_error_str_generic,
    
    # Extra field errors
    ErrorType.EXTRA_FORBIDDEN: error_handling.extra_forbidden_error,
    
    # JSON errors
    ErrorType.JSON_INVALID: error_handling.json_invalid_error,
    
    # Missing errors
    ErrorType.MISSING: error_handling.missing_error,
    
    # Numeric errors
    ErrorType.GREATER_THAN: error_handling.verbose_error_str_generic,
    ErrorType.GREATER_THAN_EQUAL: error_handling.verbose_error_str_generic,
    ErrorType.LESS_THAN: error_handling.verbose_error_str_generic,
    ErrorType.LESS_THAN_EQUAL: error_handling.verbose_error_str_generic,
    ErrorType.MULTIPLE_OF: error_handling.verbose_error_str_generic,
    
    # String errors
    ErrorType.STRING_TYPE: error_handling.verbose_error_str_generic,
    ErrorType.STRING_TOO_SHORT: partial(error_handling.too_short_error, unit="characters"),
    ErrorType.STRING_TOO_LONG: partial(error_handling.too_long_error, unit="characters"),
    ErrorType.STRING_PATTERN_MISMATCH: error_handling.verbose_error_str_generic,
    
    # Type/parsing errors
    ErrorType.INT_PARSING: error_handling.verbose_error_str_generic,
    ErrorType.FLOAT_PARSING: error_handling.verbose_error_str_generic,
    ErrorType.BOOL_PARSING: error_handling.verbose_error_str_generic,
    ErrorType.BYTES_TYPE: error_handling.verbose_error_str_generic,
    ErrorType.CALLABLE_TYPE: error_handling.verbose_error_str_generic,
    ErrorType.MODEL_TYPE: error_handling.verbose_error_str_generic,
    ErrorType.NONE_REQUIRED: error_handling.verbose_error_str_generic,
        
    # Union errors
    ErrorType.UNION_TAG_INVALID: error_handling.union_tag_invalid_error,
    ErrorType.UNION_TAG_NOT_FOUND: error_handling.union_tag_not_found_error,
    
    # URL errors
    ErrorType.URL_PARSING: error_handling.url_parsing_error,
    ErrorType.URL_SCHEME: error_handling.verbose_error_str_generic,

    # UUID errors
    ErrorType.UUID_PARSING: error_handling.uuid_parsing_error,
    
    # Validation errors
    ErrorType.VALUE_ERROR: error_handling.validation_error,
    ErrorType.ASSERTION_ERROR: error_handling.validation_error,
    ErrorType.FROZEN_INSTANCE: error_handling.frozen_instance_error,
}


def parse_error_details(error: pydantic.ValidationError) -> list[PydanticErrorsVerbose]:
    """Parse a ValidationError and return list of verbose error details."""
    typed_error = VerboseValidationErrorData(error)
    return [clean(error) for error in typed_error.errors]

def verbose_to_nice(verbose_error: PydanticErrorsVerbose) -> NicePydanticError:
    """Convert a PydanticErrorsVerbose to a NicePydanticError."""
    return NicePydanticError.from_verbose(verbose_error)

def error_to_nice(error: pydantic.ValidationError) -> list[NicePydanticError]:
    """Convert a ValidationError to a list of NicePydanticErrors."""
    verbose = parse_error_details(error)
    return [verbose_to_nice(error) for error in verbose]

def nice_to_string(nice_error: NicePydanticError) -> str:
    """Convert a NicePydanticError to a string."""
    return f"{nice_error.message}"

def error_to_string(verbose_error: pydantic.ValidationError) -> str:
    """Convert a PydanticErrorsVerbose to a string."""
    verbose = parse_error_details(verbose_error)
    nice = [verbose_to_nice(error) for error in verbose]
    return "\n".join(nice_to_string(n) for n in nice)


def clean(error_details: PydanticErrorsVerbose) -> PydanticErrorsVerbose:
    """Route error to appropriate handler and set verbose_error."""
    error_type = error_details.formatted_type
    
    handler = ERROR_HANDLERS.get(error_type)
    if handler:
        error_details.verbose_error = handler(error_details)
    
    return error_details


def _process_error(error: pydantic.ValidationError, omit_patterns: list[str] | None = None) -> VerboseValidationError:
    """Process a ValidationError into a VerboseValidationError."""
    omit_patterns = omit_patterns or []
    verbose_errors: list[str] = []
    structured_errors: list[NicePydanticError] = []
    
    for e in error.errors():
        cleaned = clean(PydanticErrorsVerbose(e, omit_patterns=omit_patterns))
        verbose_errors.append(cleaned.verbose_error or cleaned.msg)
        structured_errors.append(NicePydanticError.from_verbose(cleaned))

    return VerboseValidationError(error, verbose_errors, structured_errors)
