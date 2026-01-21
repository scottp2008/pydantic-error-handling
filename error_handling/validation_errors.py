# Handlers for custom validation errors (ValueError, AssertionError, etc.)
from pydantic_error_handling.models.models import PydanticErrorsVerbose
from pydantic_error_handling.error_handling import shared


def value_error(error: PydanticErrorsVerbose) -> str:
    return f"'{error.formatted_loc}': Validation failed - {error.ctx['error']}. {shared.format_received_value(error.input)}"


def assertion_error(error: PydanticErrorsVerbose) -> str:
    return f"'{error.formatted_loc}': Validation failed - {error.ctx['error']}. {shared.format_received_value(error.input)}"


def frozen_instance_error(error: PydanticErrorsVerbose) -> str:
    return f"'{error.formatted_loc}': Cannot modify frozen instance. {shared.format_received_value(error.input)}"
