from typing import Any

from pydantic_errors.models.models import PydanticErrorsVerbose


def format_received_value(value: Any) -> str:
    if isinstance(value, str):
        value_str = f"{repr(value)}"
    else:
        value_str = f"{value}"
    return f"Received type: {type(value).__name__}, value: {value_str}"


def verbose_error_str_generic(error: PydanticErrorsVerbose) -> str:
    return f"'{error.formatted_loc}': {error.msg}. {format_received_value(error.input)}"