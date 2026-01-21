"""Core logic for transforming Pydantic validation errors into verbose messages."""

from typing import Callable

import pydantic
from pydantic_errors.models.models import (
    ErrorType,
    NicePydanticError,
    PydanticErrorsVerbose,
    VerboseValidationError,
    VerboseValidationErrorData,
)
from pydantic_errors.error_handling import (
    collection_errors,
    datetime_errors,
    email_url_errors,
    extra_field_errors,
    json_errors,
    missing_errors,
    shared,
    type_errors,
    union_errors,
    uuid_errors,
    validation_errors,
)

# Type alias for error handler functions
ErrorHandler = Callable[[PydanticErrorsVerbose], str]

# Registry mapping ErrorType to handler function
ERROR_HANDLERS: dict[ErrorType, ErrorHandler] = {
    # Collection errors
    ErrorType.LIST_TYPE: collection_errors.list_type_error,
    ErrorType.SET_TYPE: collection_errors.set_type_error,
    ErrorType.TUPLE_TYPE: collection_errors.tuple_type_error,
    ErrorType.DICT_TYPE: collection_errors.dict_type_error,
    ErrorType.FROZEN_SET_TYPE: collection_errors.frozen_set_type_error,
    ErrorType.TOO_SHORT: collection_errors.too_short_error,
    ErrorType.TOO_LONG: collection_errors.too_long_error,
    
    # Datetime parsing errors
    ErrorType.DATE_FROM_DATETIME_PARSING: datetime_errors.date_from_datetime_parsing_error,
    ErrorType.DATETIME_FROM_DATE_PARSING: datetime_errors.datetime_from_date_parsing_error,
    ErrorType.TIME_PARSING: datetime_errors.time_parsing_error,
    ErrorType.TIME_DELTA_PARSING: datetime_errors.time_delta_parsing_error,
    
    # Datetime constraint errors (generic)
    ErrorType.DATE_PAST: shared.verbose_error_str_generic,
    ErrorType.DATE_FUTURE: shared.verbose_error_str_generic,
    ErrorType.DATETIME_PAST: shared.verbose_error_str_generic,
    ErrorType.DATETIME_FUTURE: shared.verbose_error_str_generic,
    ErrorType.TIMEZONE_AWARE: shared.verbose_error_str_generic,
    ErrorType.TIMEZONE_NAIVE: shared.verbose_error_str_generic,
    
    # Decimal errors (generic)
    ErrorType.DECIMAL_PARSING: shared.verbose_error_str_generic,
    ErrorType.DECIMAL_MAX_DIGITS: shared.verbose_error_str_generic,
    ErrorType.DECIMAL_MAX_PLACES: shared.verbose_error_str_generic,
    
    # URL errors
    ErrorType.URL_PARSING: email_url_errors.url_parsing_error,
    ErrorType.URL_SCHEME: shared.verbose_error_str_generic,
    
    # Enum errors (generic)
    ErrorType.ENUM: shared.verbose_error_str_generic,
    ErrorType.LITERAL_ERROR: shared.verbose_error_str_generic,
    
    # Extra field errors
    ErrorType.EXTRA_FORBIDDEN: extra_field_errors.extra_forbidden_error,
    
    # JSON errors
    ErrorType.JSON_INVALID: json_errors.json_invalid_error,
    
    # Missing errors
    ErrorType.MISSING: missing_errors.missing_error,
    
    # Numeric errors (generic)
    ErrorType.GREATER_THAN: shared.verbose_error_str_generic,
    ErrorType.GREATER_THAN_EQUAL: shared.verbose_error_str_generic,
    ErrorType.LESS_THAN: shared.verbose_error_str_generic,
    ErrorType.LESS_THAN_EQUAL: shared.verbose_error_str_generic,
    ErrorType.MULTIPLE_OF: shared.verbose_error_str_generic,
    
    # String errors
    ErrorType.STRING_TYPE: shared.verbose_error_str_generic,
    ErrorType.STRING_TOO_SHORT: type_errors.string_too_short_error,
    ErrorType.STRING_TOO_LONG: type_errors.string_too_long_error,
    ErrorType.STRING_PATTERN_MISMATCH: shared.verbose_error_str_generic,
    
    # Type/parsing errors (generic)
    ErrorType.INT_PARSING: shared.verbose_error_str_generic,
    ErrorType.FLOAT_PARSING: shared.verbose_error_str_generic,
    ErrorType.BOOL_PARSING: shared.verbose_error_str_generic,
    ErrorType.BYTES_TYPE: shared.verbose_error_str_generic,
    ErrorType.CALLABLE_TYPE: shared.verbose_error_str_generic,
    ErrorType.NONE_REQUIRED: shared.verbose_error_str_generic,
    
    # Bytes length errors
    ErrorType.BYTES_TOO_SHORT: type_errors.bytes_too_short_error,
    ErrorType.BYTES_TOO_LONG: type_errors.bytes_too_long_error,
    
    # Union errors
    ErrorType.UNION_TAG_INVALID: union_errors.union_tag_invalid_error,
    ErrorType.UNION_TAG_NOT_FOUND: union_errors.union_tag_not_found_error,
    
    # UUID errors
    ErrorType.UUID_PARSING: uuid_errors.uuid_parsing_error,
    
    # Validation errors
    ErrorType.VALUE_ERROR: validation_errors.value_error,
    ErrorType.ASSERTION_ERROR: validation_errors.assertion_error,
    ErrorType.FROZEN_INSTANCE: validation_errors.frozen_instance_error,
}


def parse_error_details(error: pydantic.ValidationError) -> list[PydanticErrorsVerbose]:
    """Parse a ValidationError and return list of verbose error details."""
    typed_error = VerboseValidationErrorData(error)
    return [clean(error) for error in typed_error.errors]


def clean(error_details: PydanticErrorsVerbose) -> PydanticErrorsVerbose:
    """Route error to appropriate handler and set verbose_error."""
    error_type = error_details.formatted_type
    
    handler = ERROR_HANDLERS.get(error_type)
    if handler:
        error_details.verbose_error = handler(error_details)
    
    return error_details


def _process_error(error: pydantic.ValidationError) -> VerboseValidationError:
    """Process a ValidationError into a VerboseValidationError."""
    verbose_errors: list[str] = []
    structured_errors: list[NicePydanticError] = []
    
    for e in error.errors():
        cleaned = clean(PydanticErrorsVerbose(e))
        verbose_errors.append(cleaned.verbose_error or cleaned.msg)
        structured_errors.append(NicePydanticError.from_verbose(cleaned))

    return VerboseValidationError(error, verbose_errors, structured_errors)
