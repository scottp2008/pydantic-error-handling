# decorator.py
"""Decorator for Pydantic models to provide verbose validation errors."""

from functools import wraps as _wraps
from typing import TypeVar, Type, Any, Callable
from pydantic import BaseModel, ValidationError

from pydantic_error_handling._core import _process_error

T = TypeVar('T', bound=BaseModel)


def verbose_errors(
    cls: Type[T] | None = None, 
    *, 
    omit_patterns: list[str] | None = None
) -> Type[T] | Callable[[Type[T]], Type[T]]:
    """
    Decorator for Pydantic models that converts ValidationError 
    to VerboseValidationError with human-readable messages.
    
    Usage:
        @verbose_errors
        class MyModel(BaseModel):
            name: str
            age: int
            
        # Or with custom patterns:
        @verbose_errors(omit_patterns=["Problem"])
        class MyModel(BaseModel):
            name: str
            age: int
    """
    omit_patterns = omit_patterns or []
    
    def decorator(cls_to_wrap: Type[T]) -> Type[T]:
        original_init = cls_to_wrap.__init__

        @_wraps(original_init)
        def wrapped_init(self: Any, *args: Any, **kwargs: Any) -> None:
            try:
                original_init(self, *args, **kwargs)
            except ValidationError as e:
                raise _process_error(e, omit_patterns=omit_patterns) from e

        @classmethod
        def wrapped_validate(cls_inner: Type[T], *args: Any, **kwargs: Any) -> T:
            try:
                return BaseModel.model_validate.__func__(cls_inner, *args, **kwargs)  # type: ignore[attr-defined]
            except ValidationError as e:
                raise _process_error(e, omit_patterns=omit_patterns) from e

        @classmethod
        def wrapped_validate_json(cls_inner: Type[T], *args: Any, **kwargs: Any) -> T:
            try:
                return BaseModel.model_validate_json.__func__(cls_inner, *args, **kwargs)  # type: ignore[attr-defined]
            except ValidationError as e:
                raise _process_error(e, omit_patterns=omit_patterns) from e

        cls_to_wrap.__init__ = wrapped_init  # type: ignore[assignment]
        cls_to_wrap.model_validate = wrapped_validate  # type: ignore[assignment]
        cls_to_wrap.model_validate_json = wrapped_validate_json  # type: ignore[assignment]

        return cls_to_wrap
    
    # If called without parentheses: @verbose_errors
    if cls is not None:
        return decorator(cls)
    
    # If called with parentheses: @verbose_errors(omit_patterns=[...])
    return decorator
