from dataclasses import field
import enum
from typing import Any
from pydantic import BaseModel
from pydantic_core import ErrorDetails, ValidationError


class ErrorType(enum.Enum):
    """Verified error types captured from Pydantic validation."""
    
    UNKNOWN = "unknown"

    # Collection errors
    LIST_TYPE = "list_type"
    SET_TYPE = "set_type"
    TUPLE_TYPE = "tuple_type"
    DICT_TYPE = "dict_type"
    FROZEN_SET_TYPE = "frozen_set_type"
    TOO_SHORT = "too_short"
    TOO_LONG = "too_long"

    # Datetime errors
    DATE_FROM_DATETIME_PARSING = "date_from_datetime_parsing"
    DATETIME_FROM_DATE_PARSING = "datetime_from_date_parsing"
    TIME_PARSING = "time_parsing"
    TIME_DELTA_PARSING = "time_delta_parsing"
    DATE_PAST = "date_past"
    DATE_FUTURE = "date_future"
    DATETIME_PAST = "datetime_past"
    DATETIME_FUTURE = "datetime_future"
    TIMEZONE_AWARE = "timezone_aware"
    TIMEZONE_NAIVE = "timezone_naive"

    # Decimal errors
    DECIMAL_PARSING = "decimal_parsing"
    DECIMAL_MAX_DIGITS = "decimal_max_digits"
    DECIMAL_MAX_PLACES = "decimal_max_places"

    # URL errors
    URL_PARSING = "url_parsing"
    URL_SCHEME = "url_scheme"

    # Enum errors
    ENUM = "enum"
    LITERAL_ERROR = "literal_error"

    # Extra field errors
    EXTRA_FORBIDDEN = "extra_forbidden"

    # JSON errors
    JSON_INVALID = "json_invalid"

    # Missing errors
    MISSING = "missing"

    # Numeric errors
    GREATER_THAN = "greater_than"
    GREATER_THAN_EQUAL = "greater_than_equal"
    LESS_THAN = "less_than"
    LESS_THAN_EQUAL = "less_than_equal"
    MULTIPLE_OF = "multiple_of"

    # String errors
    STRING_TYPE = "string_type"
    STRING_TOO_SHORT = "string_too_short"
    STRING_TOO_LONG = "string_too_long"
    STRING_PATTERN_MISMATCH = "string_pattern_mismatch"

    # Type/parsing errors
    INT_PARSING = "int_parsing"
    FLOAT_PARSING = "float_parsing"
    BOOL_PARSING = "bool_parsing"
    BYTES_TYPE = "bytes_type"
    BYTES_TOO_SHORT = "bytes_too_short"
    BYTES_TOO_LONG = "bytes_too_long"
    CALLABLE_TYPE = "callable_type"
    MODEL_TYPE = "model_type"
    NONE_REQUIRED = "none_required"

    # Union errors
    UNION_TAG_INVALID = "union_tag_invalid"
    UNION_TAG_NOT_FOUND = "union_tag_not_found"

    # UUID errors
    UUID_PARSING = "uuid_parsing"

    # Validation errors
    VALUE_ERROR = "value_error"
    ASSERTION_ERROR = "assertion_error"
    FROZEN_INSTANCE = "frozen_instance"


# Patterns that appear in Pydantic error `loc` tuples that should be filtered out
# when constructing clean field paths for UI/API consumption.
#
# When Pydantic validates complex types or uses custom validators, it wraps field
# paths with internal validation metadata. For example:
#   loc = ("serial", "function-before[validate(), str]")
#
# The field_path property filters these patterns to return just ("serial",).
#
# This list includes all known Pydantic v2.x location patterns that represent
# validation/serialization internals rather than actual data field paths.
#
# When using the wrapper, you are able to add additional patterns via the omit_patterns parameter.
PYDANTIC_FUNCTION_LOC_PATTERNS = [ 
    # Validator patterns (from @field_validator, @model_validator decorators)
    "function-before[",   # mode='before' validators
    "function-after[",    # mode='after' validators
    "function-wrap[",     # mode='wrap' validators
    "function-plain[",    # mode='plain' validators
    
    # Type-specific validation wrappers
    "enum[",              # enum field validation
    "dict[",              # dict field validation
    "list[",              # list/sequence field validation
    "set[",               # set field validation
    "frozenset[",         # frozenset field validation
    "tuple[",             # tuple field validation
    
    # Union/discriminated union patterns
    "union[",             # union type validation
    "tagged-union[",      # discriminated union validation
    
    # Special validators
    "dataclass[",         # dataclass validation
    "model[",             # BaseModel validation (nested models)
    "typed-dict[",        # TypedDict validation
    "arguments[",         # @validate_call arguments validation
    
    # Serialization patterns (can appear in error paths during validation)
    "function-ser[",      # custom serializers
    "function-plain-ser[", # plain serializers
]


class PydanticErrorsVerbose:
    type: str
    loc: tuple[int | str, ...]
    msg: str
    input: Any
    ctx: dict[str, Any] | None
    url: str | None
    verbose_error: str | None
    field_path: tuple[int | str, ...]
    formatted_loc: str
    formatted_type: ErrorType

    def __init__(self, error_details: ErrorDetails, omit_patterns: list[str] | None = None):
        self.type = error_details["type"]
        self.loc = error_details["loc"]
        self.msg = error_details["msg"]
        self.input = error_details["input"]
        self.ctx = error_details.get("ctx", None)
        self.url = error_details.get("url", None)
        self.verbose_error = None  
        
        omit_patterns_combined = (omit_patterns or []) + PYDANTIC_FUNCTION_LOC_PATTERNS
        self.field_path = tuple(i for i in self.loc if not any(pattern in str(i) for pattern in omit_patterns_combined))
        
        # Define formatted loc
        self.formatted_loc = "root" if self.field_path == () else ".".join(
            f"[{i}]" if isinstance(i, int) else i for i in self.field_path
        )
        
        try:
            self.formatted_type = ErrorType(self.type)
        except ValueError:
            self.formatted_type = ErrorType.UNKNOWN


class VerboseValidationErrorData:
    count: int
    errors: list[PydanticErrorsVerbose]

    def __init__(self, validation_error: ValidationError):
        self.count = validation_error.error_count()
        self.errors = [PydanticErrorsVerbose(error) for error in validation_error.errors()]


class NicePydanticError(BaseModel):
    """Structured error for UI field-level rendering."""
    
    field: str
    message: str
    error_type: str
    input_value: Any
    field_path: tuple[int | str, ...]

    @classmethod
    def from_verbose(cls, error: PydanticErrorsVerbose) -> "NicePydanticError":
        return cls(
            field=error.formatted_loc,
            message=error.verbose_error or error.msg,
            error_type=error.type,
            input_value=error.input,
            field_path=error.field_path,
        )


class VerboseValidationError(Exception):
    """Exception raised when Pydantic validation fails, with human-readable error messages."""
    
    original: ValidationError
    verbose_errors: list[str]
    structured_errors: list[NicePydanticError]

    def __init__(
        self,
        validation_error: ValidationError,
        verbose_errors: list[str],
        structured_errors: list[NicePydanticError],
    ):
        self.original = validation_error
        self.verbose_errors = verbose_errors
        self.structured_errors = structured_errors
        super().__init__(f'Received {self.error_count()} errors: \n {"\n".join(verbose_errors)}')

    def errors(self) -> list[ErrorDetails]:
        """Return the original Pydantic error details."""
        return self.original.errors()

    def error_count(self) -> int:
        """Return the number of validation errors."""
        return self.original.error_count()

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary suitable for API responses.
        
        Returns:
            {"detail": ["error message 1", "error message 2", ...]}
        """
        return {"detail": self.verbose_errors}