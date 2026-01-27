"""
Unit tests for pydantic_errors verbose error formatting.

Each test case passes an error dict through the clean() function
and verifies the verbose_error output matches expectations.
"""
import pytest
from pydantic_error_handling import PydanticErrorsVerbose, clean


# Test cases: (test_id, error_dict, expected_verbose_error)
TEST_CASES = [
    # Collection Errors
    (
        "list_type",
        {
            "type": "list_type",
            "loc": ("value",),
            "msg": "Input should be a valid list",
            "input": "not_a_list",
        },
        "'value': Should be a list. Received type: str, value: 'not_a_list'",
    ),
    (
        "set_type",
        {
            "type": "set_type",
            "loc": ("value",),
            "msg": "Input should be a valid set",
            "input": "not_a_set",
        },
        "'value': Should be a set. Received type: str, value: 'not_a_set'",
    ),
    (
        "tuple_type",
        {
            "type": "tuple_type",
            "loc": ("value",),
            "msg": "Input should be a valid tuple",
            "input": "not_a_tuple",
        },
        "'value': Should be a tuple. Received type: str, value: 'not_a_tuple'",
    ),
    (
        "dict_type",
        {
            "type": "dict_type",
            "loc": ("value",),
            "msg": "Input should be a valid dictionary",
            "input": "not_a_dict",
        },
        "'value': Should be a dict. Received type: str, value: 'not_a_dict'",
    ),
    (
        "frozen_set_type",
        {
            "type": "frozen_set_type",
            "loc": ("value",),
            "msg": "Input should be a valid frozenset",
            "input": "not_a_frozenset",
        },
        "'value': Should be a frozenset. Received type: str, value: 'not_a_frozenset'",
    ),
    (
        "too_short",
        {
            "type": "too_short",
            "loc": ("value",),
            "msg": "List should have at least 3 items after validation, not 1",
            "input": [1],
            "ctx": {"field_type": "List", "min_length": 3, "actual_length": 1},
        },
        "'value': List should have at least 3 items, not 1. Received type: list, value: [1]",
    ),
    (
        "too_long",
        {
            "type": "too_long",
            "loc": ("value",),
            "msg": "List should have at most 3 items after validation, not 5",
            "input": [1, 2, 3, 4, 5],
            "ctx": {"field_type": "List", "max_length": 3, "actual_length": 5},
        },
        "'value': List should have at most 3 items, not 5. Received type: list, value: [1, 2, 3, 4, 5]",
    ),
    # Datetime parsing errors
    (
        "date_from_datetime_parsing",
        {
            "type": "date_from_datetime_parsing",
            "loc": ("value",),
            "msg": "Input should be a valid date or datetime, invalid character in year",
            "input": "not-a-date",
            "ctx": {"error": "invalid character in year"},
        },
        "'value': Invalid date from datetime parsing - invalid character in year. Received type: str, value: 'not-a-date'",
    ),
    (
        "datetime_from_date_parsing",
        {
            "type": "datetime_from_date_parsing",
            "loc": ("value",),
            "msg": "Input should be a valid datetime or date, invalid character in year",
            "input": "not-a-datetime",
            "ctx": {"error": "invalid character in year"},
        },
        "'value': Invalid datetime from date parsing - invalid character in year. Received type: str, value: 'not-a-datetime'",
    ),
    (
        "time_parsing",
        {
            "type": "time_parsing",
            "loc": ("value",),
            "msg": "Input should be in a valid time format, invalid character in hour",
            "input": "not-a-time",
            "ctx": {"error": "invalid character in hour"},
        },
        "'value': Invalid time parsing - invalid character in hour. Received type: str, value: 'not-a-time'",
    ),
    (
        "time_delta_parsing",
        {
            "type": "time_delta_parsing",
            "loc": ("value",),
            "msg": "Input should be a valid timedelta, invalid digit in duration",
            "input": "not-a-timedelta",
            "ctx": {"error": "invalid digit in duration"},
        },
        "'value': Invalid time delta parsing - invalid digit in duration. Received type: str, value: 'not-a-timedelta'",
    ),
    # Datetime constraint errors
    (
        "date_past",
        {
            "type": "date_past",
            "loc": ("value",),
            "msg": "Date should be in the past",
            "input": "2099-01-01",
        },
        "'value': Date should be in the past. Received type: str, value: '2099-01-01'",
    ),
    (
        "date_future",
        {
            "type": "date_future",
            "loc": ("value",),
            "msg": "Date should be in the future",
            "input": "2000-01-01",
        },
        "'value': Date should be in the future. Received type: str, value: '2000-01-01'",
    ),
    (
        "datetime_past",
        {
            "type": "datetime_past",
            "loc": ("value",),
            "msg": "Input should be in the past",
            "input": "2099-01-01T00:00:00Z",
        },
        "'value': Input should be in the past. Received type: str, value: '2099-01-01T00:00:00Z'",
    ),
    (
        "datetime_future",
        {
            "type": "datetime_future",
            "loc": ("value",),
            "msg": "Input should be in the future",
            "input": "2000-01-01T00:00:00Z",
        },
        "'value': Input should be in the future. Received type: str, value: '2000-01-01T00:00:00Z'",
    ),
    (
        "timezone_aware",
        {
            "type": "timezone_aware",
            "loc": ("value",),
            "msg": "Input should have timezone info",
            "input": "2023-01-15T10:30:00",
        },
        "'value': Input should have timezone info. Received type: str, value: '2023-01-15T10:30:00'",
    ),
    (
        "timezone_naive",
        {
            "type": "timezone_naive",
            "loc": ("value",),
            "msg": "Input should not have timezone info",
            "input": "2023-01-15T10:30:00Z",
        },
        "'value': Input should not have timezone info. Received type: str, value: '2023-01-15T10:30:00Z'",
    ),
    # Decimal errors
    (
        "decimal_parsing",
        {
            "type": "decimal_parsing",
            "loc": ("value",),
            "msg": "Input should be a valid decimal",
            "input": "not-a-decimal",
        },
        "'value': Input should be a valid decimal. Received type: str, value: 'not-a-decimal'",
    ),
    (
        "decimal_max_digits",
        {
            "type": "decimal_max_digits",
            "loc": ("value",),
            "msg": "Decimal input should have no more than 5 digits in total",
            "input": "123456.789",
            "ctx": {"max_digits": 5},
        },
        "'value': Decimal input should have no more than 5 digits in total. Received type: str, value: '123456.789'",
    ),
    (
        "decimal_max_places",
        {
            "type": "decimal_max_places",
            "loc": ("value",),
            "msg": "Decimal input should have no more than 2 decimal places",
            "input": "123.456",
            "ctx": {"decimal_places": 2},
        },
        "'value': Decimal input should have no more than 2 decimal places. Received type: str, value: '123.456'",
    ),
    # URL errors
    (
        "url_parsing",
        {
            "type": "url_parsing",
            "loc": ("value",),
            "msg": "Input should be a valid URL, relative URL without a base",
            "input": "not-a-url",
            "ctx": {"error": "relative URL without a base"},
        },
        "'value': Invalid URL - relative URL without a base. Received type: str, value: 'not-a-url'",
    ),
    (
        "url_scheme",
        {
            "type": "url_scheme",
            "loc": ("value",),
            "msg": "URL scheme should be 'http' or 'https'",
            "input": "ftp://example.com",
            "ctx": {"expected_schemes": "'http' or 'https'"},
        },
        "'value': URL scheme should be 'http' or 'https'. Received type: str, value: 'ftp://example.com'",
    ),
    # Enum errors
    (
        "enum",
        {
            "type": "enum",
            "loc": ("value",),
            "msg": "Input should be 'red', 'green' or 'blue'",
            "input": "purple",
            "ctx": {"expected": "'red', 'green' or 'blue'"},
        },
        "'value': Input should be 'red', 'green' or 'blue'. Received type: str, value: 'purple'",
    ),
    (
        "literal_error",
        {
            "type": "literal_error",
            "loc": ("value",),
            "msg": "Input should be 'active' or 'inactive'",
            "input": "pending",
            "ctx": {"expected": "'active' or 'inactive'"},
        },
        "'value': Input should be 'active' or 'inactive'. Received type: str, value: 'pending'",
    ),
    # Extra field errors
    (
        "extra_forbidden",
        {
            "type": "extra_forbidden",
            "loc": ("extra_field",),
            "msg": "Extra inputs are not permitted",
            "input": "value",
        },
        "Unexpected field: 'extra_field'. Extra fields are not permitted. Received type: str, value: 'value'",
    ),
    # JSON errors
    (
        "json_invalid",
        {
            "type": "json_invalid",
            "loc": (),
            "msg": "Invalid JSON: key must be a string at line 1 column 2",
            "input": "{invalid json}",
            "ctx": {"error": "key must be a string at line 1 column 2"},
        },
        "Invalid JSON at line 1, column 2:\n  {invalid json}\n   ^ key must be a string",
    ),
    # Missing field errors
    (
        "missing",
        {
            "type": "missing",
            "loc": ("required_field",),
            "msg": "Field required",
            "input": {},
        },
        "Missing required field: required_field.",
    ),
    # Numeric constraint errors
    (
        "greater_than",
        {
            "type": "greater_than",
            "loc": ("value",),
            "msg": "Input should be greater than 10",
            "input": 5,
            "ctx": {"gt": 10},
        },
        "'value': Input should be greater than 10. Received type: int, value: 5",
    ),
    (
        "greater_than_equal",
        {
            "type": "greater_than_equal",
            "loc": ("value",),
            "msg": "Input should be greater than or equal to 10",
            "input": 5,
            "ctx": {"ge": 10},
        },
        "'value': Input should be greater than or equal to 10. Received type: int, value: 5",
    ),
    (
        "less_than",
        {
            "type": "less_than",
            "loc": ("value",),
            "msg": "Input should be less than 10",
            "input": 15,
            "ctx": {"lt": 10},
        },
        "'value': Input should be less than 10. Received type: int, value: 15",
    ),
    (
        "less_than_equal",
        {
            "type": "less_than_equal",
            "loc": ("value",),
            "msg": "Input should be less than or equal to 10",
            "input": 15,
            "ctx": {"le": 10},
        },
        "'value': Input should be less than or equal to 10. Received type: int, value: 15",
    ),
    (
        "multiple_of",
        {
            "type": "multiple_of",
            "loc": ("value",),
            "msg": "Input should be a multiple of 5",
            "input": 7,
            "ctx": {"multiple_of": 5},
        },
        "'value': Input should be a multiple of 5. Received type: int, value: 7",
    ),
    # String errors
    (
        "string_type",
        {
            "type": "string_type",
            "loc": ("value",),
            "msg": "Input should be a valid string",
            "input": 123,
        },
        "'value': Input should be a valid string. Received type: int, value: 123",
    ),
    (
        "string_too_short",
        {
            "type": "string_too_short",
            "loc": ("value",),
            "msg": "String should have at least 5 characters",
            "input": "abc",
            "ctx": {"min_length": 5},
        },
        "'value': Should have at least 5 characters, not 3. Received type: str, value: 'abc'",
    ),
    (
        "string_too_long",
        {
            "type": "string_too_long",
            "loc": ("value",),
            "msg": "String should have at most 5 characters",
            "input": "this is way too long",
            "ctx": {"max_length": 5},
        },
        "'value': Should have at most 5 characters, not 20. Received type: str, value: 'this is way too long'",
    ),
    (
        "string_pattern_mismatch",
        {
            "type": "string_pattern_mismatch",
            "loc": ("value",),
            "msg": "String should match pattern '^[a-z]+$'",
            "input": "ABC123",
            "ctx": {"pattern": "^[a-z]+$"},
        },
        "'value': String should match pattern '^[a-z]+$'. Received type: str, value: 'ABC123'",
    ),
    # Type parsing errors
    (
        "int_parsing",
        {
            "type": "int_parsing",
            "loc": ("value",),
            "msg": "Input should be a valid integer, unable to parse string as an integer",
            "input": "not_an_int",
        },
        "'value': Input should be a valid integer, unable to parse string as an integer. Received type: str, value: 'not_an_int'",
    ),
    (
        "float_parsing",
        {
            "type": "float_parsing",
            "loc": ("value",),
            "msg": "Input should be a valid number, unable to parse string as a number",
            "input": "not_a_float",
        },
        "'value': Input should be a valid number, unable to parse string as a number. Received type: str, value: 'not_a_float'",
    ),
    (
        "bool_parsing",
        {
            "type": "bool_parsing",
            "loc": ("value",),
            "msg": "Input should be a valid boolean, unable to interpret input",
            "input": "not_a_bool",
        },
        "'value': Input should be a valid boolean, unable to interpret input. Received type: str, value: 'not_a_bool'",
    ),
    (
        "bytes_type",
        {
            "type": "bytes_type",
            "loc": ("value",),
            "msg": "Input should be a valid bytes",
            "input": 123,
        },
        "'value': Input should be a valid bytes. Received type: int, value: 123",
    ),
    (
        "callable_type",
        {
            "type": "callable_type",
            "loc": ("value",),
            "msg": "Input should be callable",
            "input": "not_callable",
        },
        "'value': Input should be callable. Received type: str, value: 'not_callable'",
    ),
    (
        "none_required",
        {
            "type": "none_required",
            "loc": ("value",),
            "msg": "Input should be None",
            "input": "not_none",
        },
        "'value': Input should be None. Received type: str, value: 'not_none'",
    ),
    # Bytes length errors
    (
        "bytes_too_short",
        {
            "type": "bytes_too_short",
            "loc": ("value",),
            "msg": "Data should have at least 10 bytes",
            "input": b"short",
            "ctx": {"min_length": 10},
        },
        "'value': Should have at least 10 bytes, not 5. Received type: bytes, value: b'short'",
    ),
    (
        "bytes_too_long",
        {
            "type": "bytes_too_long",
            "loc": ("value",),
            "msg": "Data should have at most 5 bytes",
            "input": b"this is too long",
            "ctx": {"max_length": 5},
        },
        "'value': Should have at most 5 bytes, not 16. Received type: bytes, value: b'this is too long'",
    ),
    # Union errors
    (
        "union_tag_invalid",
        {
            "type": "union_tag_invalid",
            "loc": ("item",),
            "msg": "Input tag 'c' found using 'type' does not match any of the expected tags: 'a', 'b'",
            "input": {"type": "c", "c_field": "test"},
            "ctx": {"discriminator": "'type'", "tag": "c", "expected_tags": "'a', 'b'"},
        },
        "'item': Unrecognized type. The 'type' field was 'c', but must be one of: 'a', 'b'.",
    ),
    (
        "union_tag_not_found",
        {
            "type": "union_tag_not_found",
            "loc": ("item",),
            "msg": "Unable to extract tag using discriminator 'type'",
            "input": {"no_type": "test"},
            "ctx": {"discriminator": "'type'"},
        },
        "'item': Missing 'type' field to identify what type of object it is.",
    ),
    # UUID errors
    (
        "uuid_parsing",
        {
            "type": "uuid_parsing",
            "loc": ("value",),
            "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `n` at 1",
            "input": "not-a-uuid",
            "ctx": {"error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `n` at 1"},
        },
        "'value': Not a valid UUID. Received type: str, value: 'not-a-uuid'",
    ),
    # Validation errors
    (
        "value_error",
        {
            "type": "value_error",
            "loc": ("value",),
            "msg": "Value error, Value cannot be 'bad'",
            "input": "bad",
            "ctx": {"error": "Value cannot be 'bad'"},
        },
        "'value': Validation failed - Value cannot be 'bad'. Received type: str, value: 'bad'",
    ),
    (
        "assertion_error",
        {
            "type": "assertion_error",
            "loc": ("value",),
            "msg": "Assertion failed, Value cannot be 'bad'",
            "input": "bad",
            "ctx": {"error": "Value cannot be 'bad'"},
        },
        "'value': Validation failed - Value cannot be 'bad'. Received type: str, value: 'bad'",
    ),
    (
        "frozen_instance",
        {
            "type": "frozen_instance",
            "loc": ("value",),
            "msg": "Instance is frozen",
            "input": "new_value",
        },
        "'value': Cannot modify frozen instance. Received type: str, value: 'new_value'",
    ),
]


@pytest.mark.parametrize(
    "test_id,error_dict,expected",
    TEST_CASES,
    ids=[case[0] for case in TEST_CASES],
)
def test_verbose_error(test_id: str, error_dict: dict, expected: str) -> None:
    """Test that error dicts produce the expected verbose error string."""
    error = PydanticErrorsVerbose(error_dict)  # type: ignore[arg-type]
    result = clean(error)
    assert result.verbose_error == expected, f"Failed for {test_id}"


def test_unknown_error_type_returns_unchanged() -> None:
    """Test that unknown error types return the error unchanged (no verbose_error)."""
    error_dict = {
        "type": "some_unknown_type",
        "loc": ("field",),
        "msg": "Some message",
        "input": "value",
    }
    error = PydanticErrorsVerbose(error_dict)  # type: ignore[arg-type]
    result = clean(error)
    assert result.verbose_error is None

