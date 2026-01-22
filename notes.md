The important bit of actually handling and reformatting stuff looks good!

The rest is mostly "to taste" it's just what I would do, I have three relatively big suggestions, then a load of small comments.

# Simplification 1

Get rid of the intermediary `Verbose` classes/converters, then a lot of `base` and `_core` be rolled up into:

```python
class NiceErrorDetails:
    input: Any
    type: ErrorType
    field_path: tuple[int | str, ...]
    field_str: str
    verbose_error: str

    original_type: str
    original_loc: tuple[int | str, ...]
    original_message: str
    original_ctx: dict[str, Any] | None
    original_url: str | None

    def __init__(
        error_details: pydantic.ErrorDetails, 
        omit_patterns: list[str],
    ):
        self.original_type = error_details["type"]
        self.original_loc = error_details["loc"]
        self.original_message = error_details["msg"]
        self.original_ctx = error_details.get("ctx", None)
        self.original_url = error_details.get("url", None)
        self.input = error_details["input"]

        self.type=ErrorType(self.original_type) if self.original_type in ErrorType else ErrorType.UNKNOWN
        self.field_path=tuple(i for i in self.original_loc if not any(pattern in str(i) for pattern in omit_patterns + PYDANTIC_FUNCTION_LOC_PATTERNS))
        self.field_str=".".join(f"[{i}]" if isinstance(i, int) else i for i in self.field_path) or "root"
        self.verbose_error = self.original_message
        if (handler := ERROR_HANDLERS.get(error_type)):
            self.verbose_error = handler(self)


class NiceValidationError(ValueError):
    original: pydantic.ValidationError
    errors: list[NiceErrorDetails]

    def __init__(
        self, 
        validation_error: pydantic.ValidationError, 
        omit_patterns: list[str] | None = None
    ):
        self.original = validation_error
        self.errors = [NiceErrorDetails(e, omit_patterns or []) for e in validation_error.errors()]
        super().__init__(f'Received {len(self.errors)} errors: \n {"\n".join(e.verbose_error for e in self.errors)}')
```

# Simplification 2

You can probs half the line count of the project (way fewer `def`s, no more `..._errors` files, no need for `ERROR_HANDLERS`) if for verbose errors you have one file with a big switch statement, approximately like:

```python
def to_verbose_error(error: NiceErrorDetails):
    if error.type is ErrorType.LIST_TYPE: 
        return _type_error(error, list)
    if error.type is ErrorType.SET_TYPE: 
        return _type_error(error, set)
    if error.type is ErrorType.FROZEN_BLAH: 
        # One liners inlined
        return f"'{error.formatted_loc}': Cannot modify frozen instance. {shared.format_received_value(error.input)}"
    if error.type is ErrorType.JSON_BLAH:
        # This really is too long to inline
        return json_invalid_error(error: PydanticErrorsVerbose)
    ...
    assert_never(error.typ)
```

It's easier to see what the conversion actually does with everything in one file/switch statement, I'm currently struggling to compare eg. the differences/similarities between eg. `tuple_type_error` and `time_parsing_error`.

# Testing approach

In the tests, I have no idea what types these actually correspond to:

```python
{
    "type": "frozen_instance",
    "loc": ("value",),
    "msg": "Instance is frozen",
    "input": "new_value",
}
```

Are they copy pasted out of running some actual validation or are they synthesised by an LLM? If the former, why not just run the full validation, if the latter, I don't have massive confidence that they're correct.

I would refactor to be like: 

```python
# Set up a big base class with default values, validate on `setattr(...)`.
class MyModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(validate_assignment=True)

    str_: str = "str_"
    str_with_min_length: Annotated[str, pydantic.Field(min_length=3)] = "str_with_min_length"
    ...

MODEL = MyModel()

@pytest.mark.parametrize(
    [
        ("str_with_min_length", "a", "'value': Should have at least 5 characters, not 3. Received type: str, value: 'abc'"),
        ...
    ]
    "k, v, verbose_error",
)
def test_messages(k: str, v: Any, verbose_error: str) -> None:
    try:
        setattr(MODEL, k, v)
        raise AssertionError("Didn't hit exception")
    except pydantic.ValidationError as e:
        assert NiceValidationError(e).verbose_error == verbose_error
```

# Actual functionality

- There's a load of stuff in `pydantic.Field` and `pydantic.ConfigDict` where I'm not sure how the errors would come out - see the definitions, there's loads of stuff that I assume affects errors - eg. `alias=`, `extra=`, `str_min_length=`. Worth either testing or noting a burndown of things to test.
- In the error message, is `Received type: T` acutally useful given you have the `input` straight after?
- What happens with really big `input`s, do we just try and render lists len() == 100000000000, classes with masive reprs etc?
- Should `tuple(... if not any(pattern in str(i) for pattern in omit_patterns))` be `tuple(... if not any(str(i).startswith(pattern) for pattern in omit_patterns))`?

# README

- Publish to pypi so you can just say `pip install pydantic-error-handling`
- The opening example should include a class definition and `MyModel(**...) -> error`, maybe show a before and after of the error message as opposed to the `.errors()` structure - not many people know the latter even exists.
- Re-read and neaten up capitalisation/indentation etc.
- "`To add additional omissions`" - I'm not sure what this does, add an example and probably put it further down in the doc.
- Show the full object returned by `error_to_nice(...)`, not the print-y version.

# .models

- `ErrorType` - it would be nice to link to where in pydantic (/annotated types) these come from, in case you need to update them ever.
- eg. `url: str | None = None` - the default value doesn't do what you want it to do outside of a `dataclass`/`pydantic.BaseModel` context (I'm pretty sure).
- (As per big suggestion) do everything you do in the methods and `@property`s at `__init__` time? I'm not convinced the existing `.errors()` in pydantic is a good interface, why not just store `.errors` on the object?
- Can the `Exception` also be a `BaseModel` so you can ditch `to_dict(...)`? (I'm not certain either way). 
- Store `.omit_patterns` on the top level error only, not the inner error details. In fact, do you need to store it at all?

# Other

- Some stuff screams "LLM" - eg. "# ==================== Type Errors (Custom Bytes) ====================", the `class TestFoo` wrappers - if you plan on upstreaming to Pydantic, open source maintainers are swamped by low quality LLM stuff right now - I don't think this is low quality, but if I were the pydantic maintainer, I might skip stuff that looks so at a surface level. See the concept of [extractive contributions](https://llvm.org/docs//AIToolPolicy.html#extractive-contributions).
- `json_invalid_error` seems pretty complex (does eg. the truncation work), I feel it needs more testing than the one test. Again, how do these errors even arise? Is this when you call `model_validate_json(...)` or somewhere else?
