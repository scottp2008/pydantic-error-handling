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

### How to use this package

1. install the package to your project using git+https://github.com/scottp2008/pydantic-error-handling.git

2. Add the decorator `verbose_errors` to return nicely typed errors:

```
from pydantic_errors import verbose_errors


@verbose_errors
class MyPydanticClass(pydantic.BaseModel):
   ...


```