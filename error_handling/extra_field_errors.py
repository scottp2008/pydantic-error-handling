# Handlers for extra/unexpected field errors
from pydantic_errors.models.models import PydanticErrorsVerbose
from pydantic_errors.error_handling import shared


def extra_forbidden_error(error: PydanticErrorsVerbose) -> str:
    return f"Unexpected field: '{error.formatted_loc}'. Extra fields are not permitted. {shared.format_received_value(error.input)}"
