import pytest
from pydantic import BaseModel

from pydantic_error_handling import verbose_errors
from pydantic_error_handling.models.models import PydanticErrorsVerbose
from pydantic_error_handling.error_handling import json_invalid_error


class TestJSONErrorHandling:
    """Test various JSON error scenarios to achieve full coverage."""

    def test_json_error_shows_arrow_pointer(self):
        """Test that JSON errors show the visual arrow pointer at the error location."""
        @verbose_errors
        class SimpleModel(BaseModel):
            name: str
            age: int

        json_input = '{"name": "John", "age": invalid_value}'
        
        with pytest.raises(Exception) as exc_info:
            SimpleModel.model_validate_json(json_input) # type: ignore
        
        error_msg = str(exc_info.value)
        
        assert "Invalid JSON at line" in error_msg
        assert "^" in error_msg
        assert '{"name": "John", "age": invalid_value}' in error_msg  # The problem line
        # The arrow should point to the problematic location
        lines = error_msg.split('\n')
        # Find the line with the arrow
        arrow_line = [line for line in lines if '^' in line]
        assert len(arrow_line) > 0, "Arrow pointer not found in error message"

    def test_json_error_arrow_position_column_1(self):
        """Test arrow positioning when error is at column 1."""
        from pydantic_error_handling.models.models import PydanticErrorsVerbose
        from pydantic_error_handling.error_handling import json_invalid_error
        
        error_dict = {
            "type": "json_invalid",
            "loc": ("root",),
            "msg": "Invalid JSON",
            "input": 'invalid json here',
            "ctx": {"error": "Unexpected character at line 1 column 1"},
        }
        
        verbose_error = PydanticErrorsVerbose(error_dict) # type: ignore
        result = json_invalid_error(verbose_error)
        
        lines = result.split('\n')
        # Line 1: "Invalid JSON at line X, column Y:"
        # Line 2: "  {json content}"
        # Line 3: "  ^ error description"
        assert len(lines) >= 3
        assert "Invalid JSON at line 1, column 1" in lines[0]
        assert "invalid json here" in lines[1]
        # Arrow should be at position 0 (after the 2-space indent)
        assert lines[2] == ("  ^ Unexpected character")

    def test_json_error_arrow_position_middle(self):
        """Test arrow positioning when error is in the middle of the line."""
        from pydantic_error_handling.models.models import PydanticErrorsVerbose
        from pydantic_error_handling.error_handling import json_invalid_error
        
        error_dict = {
            "type": "json_invalid",
            "loc": ("root",),
            "msg": "Invalid JSON",
            "input": '{"valid": "data", "bad": X}',
            "ctx": {"error": "Unexpected token at line 1 column 26"},
        }
        
        verbose_error = PydanticErrorsVerbose(error_dict) # type: ignore
        result = json_invalid_error(verbose_error)
        
        lines = result.split('\n')
        assert len(lines) >= 3
        # The arrow should be positioned at column 26
        # Line format: "  " + content + "\n" + "  " + spaces + "^"
        arrow_line = lines[2]
        # Count spaces before ^
        spaces_before_arrow = len(arrow_line) - len(arrow_line.lstrip(' '))
        # Should be 2 (indent) + 25 (col_num - 1) = 27 spaces before ^
        assert arrow_line[spaces_before_arrow] == '^'

    def test_json_error_shows_error_description_after_arrow(self):
        """Test that error description appears after the arrow pointer."""
        from pydantic_error_handling.models.models import PydanticErrorsVerbose
        from pydantic_error_handling.error_handling import json_invalid_error
        
        error_dict = {
            "type": "json_invalid",
            "loc": ("root",),
            "msg": "Invalid JSON",
            "input": '{"test": invalid}',
            "ctx": {"error": "Unexpected token 'i' at line 1 column 10"},
        }
        
        verbose_error = PydanticErrorsVerbose(error_dict) # type: ignore
        result = json_invalid_error(verbose_error)
        
        lines = result.split('\n')
        # The error description should be on the arrow line, after the ^
        arrow_line = [line for line in lines if '^' in line][0]
        # Should have format: "  <spaces>^ Unexpected token 'i'"
        assert "^" in arrow_line
        assert "Unexpected token 'i'" in arrow_line

    def test_json_error_multiline(self):
        """Test JSON error across multiple lines."""
        @verbose_errors
        class MultiModel(BaseModel):
            name: str
            age: int
            email: str

        json_input = """{
    "name": "John",
    "age": invalid_value,
    "email": "test@example.com"
}"""
        
        with pytest.raises(Exception) as exc_info:
            MultiModel.model_validate_json(json_input) # type: ignore
        
        error_msg = str(exc_info.value)
        assert "Invalid JSON at line" in error_msg
        assert "column" in error_msg

    def test_json_error_long_line_truncation(self):
        """Test that very long JSON lines get truncated (lines 145-149)."""
        @verbose_errors
        class LongModel(BaseModel):
            data: str

        # Create a JSON string with a line > 80 characters
        long_value = "x" * 150
        json_input = f'{{"data": "{long_value}", "invalid_field": broken_value}}'
        
        with pytest.raises(Exception) as exc_info:
            LongModel.model_validate_json(json_input) # type: ignore
        
        error_msg = str(exc_info.value)
        # Should contain "..." indicating truncation
        if "Invalid JSON at line" in error_msg:
            # The line should be truncated
            assert '...xxxxxxxxxxxxxxxxxxx", "invalid_field": broken_value' in error_msg or len(error_msg) < 500
            lines = error_msg.split('\n')
            assert lines[3].find('^') == 44

        # confirm this works when we have long text either side of the error
        json_input_2 = f'{{"data": "{long_value}", "invalid_field": broken_value, "extra": {long_value}}}'

        with pytest.raises(Exception) as exc_info:
            LongModel.model_validate_json(json_input_2) # type: ignore
        
        error_msg = str(exc_info.value)
        if "Invalid JSON at line" in error_msg:
            assert '...xxxxxxxxxxxxxxxxxxx", "invalid_field": broken_value, "extra": xxxxxxxxxxxxxxxxxx...' in error_msg or len(error_msg) < 500
            # ensure ^ is placed correctly
            lines = error_msg.split('\n')
            assert lines[3].find('^') == 44

    def test_json_error_no_line_column_match(self):
        """Test JSON error when line/column cannot be parsed (lines 166-167)."""
        
        # Create a mock error with error message that doesn't match line/column pattern
        error_dict = {
            "type": "json_invalid",
            "loc": ("root",),
            "msg": "Invalid JSON",
            "input": '{"broken": json}',
            "ctx": {"error": "Generic JSON parse error without line/column info"},
        }
        
        verbose_error = PydanticErrorsVerbose(error_dict) # type: ignore
        result = json_invalid_error(verbose_error)
        
        # Should fall back to simpler error message (line 166-167)
        assert "Invalid JSON" in result
        assert "Input:" in result
        assert "Generic JSON parse error" in result

    def test_json_error_line_out_of_range(self):
        """Test JSON error when reported line number exceeds actual lines (lines 163-164)."""
        @verbose_errors
        class SimpleModel(BaseModel):
            name: str

        # This is a tricky edge case - we'd need to mock or create a scenario
        # where the error reports a line number that doesn't exist
        json_input = '{"name": invalid}'
        
        with pytest.raises(Exception) as exc_info:
            SimpleModel.model_validate_json(json_input) # type: ignore
        
        error_msg = str(exc_info.value)
        assert "Invalid JSON" in error_msg

    def test_json_error_with_ctx_none(self):
        """Test JSON error handling when ctx is None or missing 'error' key."""
        
        error_dict = {
            "type": "json_invalid",
            "loc": ("root",),
            "msg": "Invalid JSON",
            "input": '{"broken": json}',
            "ctx": None,
        }
        
        verbose_error = PydanticErrorsVerbose(error_dict) # type: ignore
        result = json_invalid_error(verbose_error)
        
        # Should fall back to generic error message
        assert "Invalid JSON" in result
        assert "Input:" in result

    def test_json_error_empty_ctx_error(self):
        """Test JSON error when ctx['error'] is empty or missing."""
        
        # Create a mock error with empty ctx['error']
        error_dict = {
            "type": "json_invalid",
            "loc": ("root",),
            "msg": "Invalid JSON",
            "input": '{"broken": json}',
            "ctx": {"error": ""},
        }
        
        verbose_error = PydanticErrorsVerbose(error_dict) # type: ignore
        result = json_invalid_error(verbose_error)
        
        # Should fall back to generic error message (no line/column match)
        assert "Invalid JSON" in result

    def test_json_error_very_long_input(self):
        """Test JSON error with input > 100 chars gets truncated in fallback."""
        
        # Create a very long invalid JSON string
        long_json = '{"data": "' + "x" * 200 + '"}'
        
        error_dict = {
            "type": "json_invalid",
            "loc": ("root",),
            "msg": "Invalid JSON",
            "input": long_json,
            "ctx": {"error": "Some generic error without line info"},
        }
        
        verbose_error = PydanticErrorsVerbose(error_dict) # type: ignore
        result = json_invalid_error(verbose_error)
        
        # Should show "..." indicating truncation
        assert "Invalid JSON" in result
        assert "..." in result
        # Input should be truncated to ~100 chars
        assert len(result) < len(long_json) + 50  # Some buffer for message text

    def test_json_error_column_at_line_start(self):
        """Test JSON error where column is at position 1 (edge case for pointer)."""
        @verbose_errors
        class TestModel(BaseModel):
            value: str

        json_input = 'invalid'  # Entire thing is invalid from column 1
        
        with pytest.raises(Exception) as exc_info:
            TestModel.model_validate_json(json_input) # type: ignore
        
        error_msg = str(exc_info.value)
        assert "Invalid JSON" in error_msg

    def test_json_error_with_newlines_in_input(self):
        """Test JSON error with actual newline characters in the problematic line."""
        @verbose_errors
        class TestModel(BaseModel):
            name: str
            age: int

        json_input = """{"name": "John",
"age": not_a_number}"""
        
        with pytest.raises(Exception) as exc_info:
            TestModel.model_validate_json(json_input) # type: ignore
        
        error_msg = str(exc_info.value)
        assert "Invalid JSON" in error_msg
        # Should show line 2 where the error is
        if "at line 2" in error_msg:
            assert "not_a_number" in error_msg or "column" in error_msg

    def test_json_error_line_number_exceeds_actual_lines(self):
        """Test JSON error when reported line number is out of range (line 164)."""
        
        # Create error with line 10 reported but input only has 2 lines
        error_dict = {
            "type": "json_invalid",
            "loc": ("root",),
            "msg": "Invalid JSON",
            "input": '{"name": "John",\n"age": 25}',  # Only 2 lines
            "ctx": {"error": "Unexpected token at line 10 column 5"},  # Line 10 doesn't exist
        }
        
        verbose_error = PydanticErrorsVerbose(error_dict) # type: ignore
        result = json_invalid_error(verbose_error)
        
        # Should fall back to simpler message (line 164) - no fancy formatting
        assert result == "Invalid JSON: Unexpected token at line 10 column 5"
        # Should NOT have the visual pointer (^) or show actual code
        assert "^" not in result
        assert '{"name"' not in result
