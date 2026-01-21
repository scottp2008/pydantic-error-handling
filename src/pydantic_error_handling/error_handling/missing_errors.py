# Handlers for missing required field errors
from pydantic_error_handling.models.models import PydanticErrorsVerbose


def missing_error(error: PydanticErrorsVerbose) -> str:
    return f"Missing required field: {error.formatted_loc}."
