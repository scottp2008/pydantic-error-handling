# decorator.py
"""Decorator for Pydantic models to provide verbose validation errors."""

from functools import wraps as _wraps
from typing import TypeVar, Type, Any
from pydantic import BaseModel, ValidationError

from pydantic_errors._core import _process_error

T = TypeVar('T', bound=BaseModel)


def verbose_errors(cls: Type[T]) -> Type[T]:
    """
    Decorator for Pydantic models that converts ValidationError 
    to VerboseValidationError with human-readable messages.
    
    Usage:
        @verbose_errors
        class MyModel(BaseModel):
            name: str
            age: int
    """
    original_init = cls.__init__

    @_wraps(original_init)
    def wrapped_init(self: Any, *args: Any, **kwargs: Any) -> None:
        try:
            original_init(self, *args, **kwargs)
        except ValidationError as e:
            raise _process_error(e) from e

    @classmethod
    def wrapped_validate(cls_inner: Type[T], *args: Any, **kwargs: Any) -> T:
        try:
            return BaseModel.model_validate.__func__(cls_inner, *args, **kwargs)  # type: ignore[attr-defined]
        except ValidationError as e:
            raise _process_error(e) from e

    @classmethod
    def wrapped_validate_json(cls_inner: Type[T], *args: Any, **kwargs: Any) -> T:
        try:
            return BaseModel.model_validate_json.__func__(cls_inner, *args, **kwargs)  # type: ignore[attr-defined]
        except ValidationError as e:
            raise _process_error(e) from e

    cls.__init__ = wrapped_init  # type: ignore[assignment]
    cls.model_validate = wrapped_validate  # type: ignore[assignment]
    cls.model_validate_json = wrapped_validate_json  # type: ignore[assignment]

    return cls
