# Handlers for union type matching errors
from pydantic_errors.models.models import PydanticErrorsVerbose


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
