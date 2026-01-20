# Handlers for date, time, datetime, and timedelta errors
from pydantic_errors.models.models import PydanticErrorsVerbose
from pydantic_errors.error_handling import shared


def _datetime_parsing_error(error: PydanticErrorsVerbose) -> str:
    assert error.ctx is not None
    error_type_readable = " ".join(error.type.split('_'))
    return f"'{error.formatted_loc}': Invalid {error_type_readable} - {error.ctx['error']}. {shared.format_received_value(error.input)}"


def date_from_datetime_parsing_error(error: PydanticErrorsVerbose) -> str:
    return _datetime_parsing_error(error)


def datetime_from_date_parsing_error(error: PydanticErrorsVerbose) -> str:
    return _datetime_parsing_error(error)


def time_parsing_error(error: PydanticErrorsVerbose) -> str:
    return _datetime_parsing_error(error)


def time_delta_parsing_error(error: PydanticErrorsVerbose) -> str:
    return _datetime_parsing_error(error)
