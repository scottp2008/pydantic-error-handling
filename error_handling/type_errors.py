# Handlers for type mismatch errors (wrong type provided)
from pydantic_errors.models.models import PydanticErrorsVerbose
from pydantic_errors.error_handling import shared


def _bytes_wrong_length_error(error: PydanticErrorsVerbose, actual_length: int, required_length: int, direction: str) -> str:
    return f"'{error.formatted_loc}': Should have {direction} {required_length} bytes, not {actual_length}. {shared.format_received_value(error.input)}"


def bytes_too_short_error(error: PydanticErrorsVerbose) -> str:
    return _bytes_wrong_length_error(error, len(error.input), error.ctx['min_length'], "no less than")


def bytes_too_long_error(error: PydanticErrorsVerbose) -> str:
    return _bytes_wrong_length_error(error, len(error.input), error.ctx['max_length'], "no more than")


def _string_wrong_length_error(error: PydanticErrorsVerbose, actual_length: int, required_length: int, direction: str) -> str:
    return f"'{error.formatted_loc}': Should have {direction} {required_length} characters, not {actual_length}. {shared.format_received_value(error.input)}"


def string_too_short_error(error: PydanticErrorsVerbose) -> str:
    return _string_wrong_length_error(error, len(error.input), error.ctx['min_length'], "at least")


def string_too_long_error(error: PydanticErrorsVerbose) -> str:
    return _string_wrong_length_error(error, len(error.input), error.ctx['max_length'], "at most")
