## Pydantic Nicer Error Classes

This package returns nicer pydantic errors that are more human readable:

 ```
        {
            "type": "union_tag_invalid",
            "loc": ("item", 2, "thing"),
            "msg": "Input tag 'c' found using 'type' does not match any of the expected tags: 'a', 'b'",
            "input": {"type": "c", "c_field": "test"},
            "ctx": {"discriminator": "'type'", "tag": "c", "expected_tags": "'a', 'b'"},
        }

        becomes:

        "'item[2].thing': Unrecognized type. The 'type' field was 'c', but must be one of: 'a', 'b'.",

```

## How to use this package

### Option 1: Use @verbose_errors wrapper

1. install the package to your project using `pip install pydantic-error-handling`

2. Add the decorator `verbose_errors` to return nicely typed errors:

```python
from pydantic_error_handling import verbose_errors


@verbose_errors
class MyPydanticClass(pydantic.BaseModel):
   ...


```

note: to produce nice loc functions, this package automatically removes typing and validators from the pattern (e.g function-before, enum etc.). To add additional omissions, you can use the omit_patterns param:

```python
from pydantic_error_handling import verbose_errors


@verbose_errors(omit_patterns=["Problem"])
class MyPydanticClass(pydantic.BaseModel):
   ...


```

### Option 2: Use helper functions to translate errors

1. install the package to your project using `pip install pydantic-error-handling`

2. generate the relevant pydantic error

3. pass the error as a NicePydanticError class or string

```python
from pydantic import BaseModel, ValidationError
from pydantic_error_handling import error_to_nice, error_to_string

class MyModel(BaseModel):
    name: str
    age: int

try:
    MyModel(name=123, age="invalid")
except ValidationError as e:
    # Get human-readable string
    print(error_to_string(e))
    # Output: 'name': Input should be a valid string. Received type: int, value: 123
    #         'age': Input should be a valid integer. Received type: str, value: 'invalid'
    
    # Or get structured errors for API/UI
    nice_errors = error_to_nice(e)
    for err in nice_errors:
        print(f"Field: {err.field_path}, Message: {err.message}")
```
