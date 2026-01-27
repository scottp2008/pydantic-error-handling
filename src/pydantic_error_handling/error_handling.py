"""Error handlers for transforming Pydantic validation errors into verbose messages."""

import re
from typing import Any

from pydantic_error_handling.models.models import PydanticErrorsVerbose



def format_received_value(value: Any) -> str:
    MAX_RESULT_LENGTH = 100
    if isinstance(value, str):
        value_str = f"{repr(value)}"
    else:
        value_str = f"{value}"
    if len(value_str) > MAX_RESULT_LENGTH:
        value_str = value_str[:MAX_RESULT_LENGTH] + "..."
    return f"Received type: {type(value).__name__}, value: {value_str}"


def verbose_error_str_generic(error: PydanticErrorsVerbose) -> str:
    return f"'{error.formatted_loc}': {error.msg}. {format_received_value(error.input)}"


def verbose_type_error(error: PydanticErrorsVerbose, expected_type: type) -> str:
    return f"'{error.formatted_loc}': Should be a {expected_type.__name__}. {format_received_value(error.input)}"


def _wrong_length_error(error: PydanticErrorsVerbose, direction: str, ctx_key: str, unit: str) -> str:
    assert error.ctx is not None
    required = error.ctx[ctx_key]
    actual = error.ctx['actual_length'] if 'actual_length' in error.ctx else len(error.input)
    prefix = f"{error.ctx['field_type']} should" if 'field_type' in error.ctx else "Should"
    return f"'{error.formatted_loc}': {prefix} have {direction} {required} {unit}, not {actual}. {format_received_value(error.input)}"


def too_short_error(error: PydanticErrorsVerbose, unit:str) -> str:
    return _wrong_length_error(error, "at least", "min_length", unit)


def too_long_error(error: PydanticErrorsVerbose, unit:str) -> str:
    return _wrong_length_error(error, "at most", "max_length", unit)


def datetime_parsing_error(error: PydanticErrorsVerbose) -> str:
    assert error.ctx is not None
    error_type_readable = " ".join(error.type.split('_'))
    return f"'{error.formatted_loc}': Invalid {error_type_readable} - {error.ctx['error']}. {format_received_value(error.input)}"


def url_parsing_error(error: PydanticErrorsVerbose) -> str:
    assert error.ctx is not None
    return f"'{error.formatted_loc}': Invalid URL - {error.ctx['error']}. {format_received_value(error.input)}"


def uuid_parsing_error(error: PydanticErrorsVerbose) -> str:
    return f"'{error.formatted_loc}': Not a valid UUID. {format_received_value(error.input)}"


def union_tag_invalid_error(error: PydanticErrorsVerbose) -> str:
    assert error.ctx is not None
    discriminator = error.ctx['discriminator'].strip("'")
    return (
        f"'{error.formatted_loc}': Unrecognized type. "
        f"The '{discriminator}' field was {error.ctx['tag']!r}, "
        f"but must be one of: {error.ctx['expected_tags']}."
    )


def union_tag_not_found_error(error: PydanticErrorsVerbose) -> str:
    assert error.ctx is not None
    discriminator = error.ctx['discriminator'].strip("'")
    return (
        f"'{error.formatted_loc}': Missing '{discriminator}' field "
        f"to identify what type of object it is."
    )


def missing_error(error: PydanticErrorsVerbose) -> str:
    return f"Missing required field: {error.formatted_loc}."


def extra_forbidden_error(error: PydanticErrorsVerbose) -> str:
    return f"Unexpected field: '{error.formatted_loc}'. Extra fields are not permitted. {format_received_value(error.input)}"


def validation_error(error: PydanticErrorsVerbose) -> str:
    assert error.ctx is not None
    return f"'{error.formatted_loc}': Validation failed - {error.ctx['error']}. {format_received_value(error.input)}"


def frozen_instance_error(error: PydanticErrorsVerbose) -> str:
    return f"'{error.formatted_loc}': Cannot modify frozen instance. {format_received_value(error.input)}"


def json_invalid_error(error: PydanticErrorsVerbose) -> str:
    """
    Handler for JSON parsing errors.
    Attempts to show the exact location in the JSON where the error occurred.
    """
    ctx_error = error.ctx.get("error", "") if error.ctx else ""
    input_str = error.input if isinstance(error.input, str) else str(error.input)
    
    # Try to extract line/column from error message
    match = re.search(r"at line (\d+) column (\d+)", ctx_error)
    
    if match:
        line_num = int(match.group(1))
        col_num = int(match.group(2))
        
        # Split into lines and get the problem line
        lines = input_str.split('\n')
        if 0 < line_num <= len(lines):
            problem_line = lines[line_num - 1]
            
            # Truncate long lines - show 40 chars either side of error
            if len(problem_line) > 80:
                start = max(0, col_num - 40)
                end = min(len(problem_line), col_num + 40)
                problem_line = ("..." if start > 0 else "") + problem_line[start:end] + ("..." if end < len(problem_line) else "")
                # Adjust column pointer for truncation
                col_num = col_num - start + (3 if start > 0 else 0)
            
            # Create pointer
            pointer = " " * (col_num - 1) + "^"
            
            # Extract the error description (before "at line...")
            error_desc = ctx_error.split(" at line")[0]
            
            return (
                f"Invalid JSON at line {line_num}, column {match.group(2)}:\n"
                f"  {problem_line}\n"
                f"  {pointer} {error_desc}"
            )
        else:
            # Line number out of range - fallback
            return f"Invalid JSON: {ctx_error}"
    else:
        # Couldn't parse line/column - fallback
        return f"Invalid JSON: {ctx_error}. Input: {input_str[:100]}{'...' if len(input_str) > 100 else ''}"
