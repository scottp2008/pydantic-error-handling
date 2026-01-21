# Handlers for email and URL validation errors
from pydantic_error_handling.models.models import PydanticErrorsVerbose
from pydantic_error_handling.error_handling import shared


def url_parsing_error(error: PydanticErrorsVerbose) -> str:
    assert error.ctx is not None
    return f"'{error.formatted_loc}': Invalid URL - {error.ctx['error']}. {shared.format_received_value(error.input)}"
