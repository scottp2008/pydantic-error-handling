# Handlers for JSON parsing errors
import re
from pydantic_error_handling.models.models import PydanticErrorsVerbose


def json_invalid_error(error: PydanticErrorsVerbose) -> str:
    ctx_error = error.ctx.get("error", "") if error.ctx else ""
    input_str = error.input if isinstance(error.input, str) else str(error.input)
    
    # Try to extract line/column from error message
    match = re.search(r"at line (\d+) column (\d+)", ctx_error)
    
    if match:
        line_num = int(match.group(1))
        col_num = int(match.group(2))
        
        # Split into lines and get the problem line
        lines = input_str.split('\n')
        if 0 < line_num <= len(lines):
            problem_line = lines[line_num - 1]
            
            # Truncate long lines - show 40 chars either side of error
            if len(problem_line) > 80:
                start = max(0, col_num - 40)
                end = min(len(problem_line), col_num + 40)
                problem_line = ("..." if start > 0 else "") + problem_line[start:end] + ("..." if end < len(problem_line) else "")
                # Adjust column pointer for truncation
                col_num = col_num - start + (3 if start > 0 else 0)
            
            # Create pointer
            pointer = " " * (col_num - 1) + "^"
            
            # Extract the error description (before "at line...")
            error_desc = ctx_error.split(" at line")[0]
            
            return (
                f"Invalid JSON at line {line_num}, column {match.group(2)}:\n"
                f"  {problem_line}\n"
                f"  {pointer} {error_desc}"
            )
        else:
            # Line number out of range - fallback
            return f"Invalid JSON: {ctx_error}"
    else:
        # Couldn't parse line/column - fallback
        return f"Invalid JSON: {ctx_error}. Input: {input_str[:100]}{'...' if len(input_str) > 100 else ''}"
