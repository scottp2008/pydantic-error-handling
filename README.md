## Pydantic Nicer Error Classes

This package returns nicer pydantic errors on over 40+ ValidationError types that are more human readable.

For example, with a json error you might get the following with pydantic:

```
ValidationError: 1 validation error for User
  Invalid JSON: expected value at line 1 column 25 [type=json_invalid, input_value='{"name": "John", "age": ....com", "addresses": []}', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/json_invalid
```

This can be hard to read, and unclear to non-technical users. Producing the same error with the package the pydantic-error-handling package becomes much clearer, with clear highlighting of the specific issue.

```
Invalid JSON at line 1, column 25:
  {"name": "John", "age": invalid, "email": "test@example.com", "addresses": []}
                          ^ expected value
```

## Quick Start

```python
from pydantic import BaseModel
from pydantic_error_handling import verbose_errors

@verbose_errors
class User(BaseModel):
    name: str
    age: int
    email: str

# JSON parsing errors now show visual arrows
bad_json = '{"name": "John", "age": invalid, "email": "test@example.com"}'
try:
    User.model_validate_json(bad_json)
except Exception as e:
    print(e)
    # Invalid JSON at line 1, column 25:
    #   {"name": "John", "age": invalid, "email": "test@example.com"}
    #                           ^ expected value
```


## How to use this package

### Option 1: Use @verbose_errors wrapper

1. install the package to your project using git+https://github.com/scottp2008/pydantic-error-handling.git

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

1. install the package to your project using git+https://github.com/scottp2008/pydantic-error-handling.git

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
