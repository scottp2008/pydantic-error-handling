# Handlers for UUID parsing and validation errors
from pydantic_error_handling.models.models import PydanticErrorsVerbose
from pydantic_error_handling.error_handling import shared


def uuid_parsing_error(error: PydanticErrorsVerbose) -> str:
    return f"'{error.formatted_loc}': Not a valid UUID. {shared.format_received_value(error.input)}"
