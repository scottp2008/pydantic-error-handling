# Handlers for collection constraint errors (List, Set, Tuple, Dict)
from pydantic_error_handling.models.models import PydanticErrorsVerbose
from pydantic_error_handling.error_handling import shared


def _type_error(error: PydanticErrorsVerbose, expected_type: type) -> str:
    return f"'{error.formatted_loc}': Should be a {expected_type.__name__}. {shared.format_received_value(error.input)}"


def _wrong_length_error(error: PydanticErrorsVerbose, direction: str, ctx_value: str) -> str:
    assert error.ctx is not None
    return f"'{error.formatted_loc}': {error.ctx['field_type']} should have {direction} {error.ctx[ctx_value]} items, not {error.ctx['actual_length']}. {shared.format_received_value(error.input)}"


def list_type_error(error: PydanticErrorsVerbose) -> str:
    return _type_error(error, list)


def set_type_error(error: PydanticErrorsVerbose) -> str:
    return _type_error(error, set)


def tuple_type_error(error: PydanticErrorsVerbose) -> str:
    return _type_error(error, tuple)


def dict_type_error(error: PydanticErrorsVerbose) -> str:
    return _type_error(error, dict)


def frozen_set_type_error(error: PydanticErrorsVerbose) -> str:
    return _type_error(error, frozenset)


def too_short_error(error: PydanticErrorsVerbose) -> str:
    return _wrong_length_error(error, "at least", "min_length")


def too_long_error(error: PydanticErrorsVerbose) -> str:
    return _wrong_length_error(error, "at most", "max_length")
