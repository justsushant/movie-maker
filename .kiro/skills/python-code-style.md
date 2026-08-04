# Python Code Style Skill

When writing or reviewing Python code in this workspace:

## Code Style Guidelines

- Use type hints for function parameters and return values
- Follow PEP 8 naming conventions (snake_case for functions/variables)
- Maximum line length: 100 characters
- Use docstrings for all public functions and classes
- Prefer f-strings over .format() or % formatting
- Use pathlib.Path for file operations instead of os.path

## Testing Requirements

- Write pytest tests for all new functions
- Aim for 80%+ code coverage
- Use fixtures for common test setup
- Mock external dependencies

## Example Format

```python
from pathlib import Path
from typing import List, Optional

def process_files(input_dir: Path, pattern: str = "*.txt") -> List[Path]:
    """
    Process files matching pattern in the input directory.
    
    Args:
        input_dir: Directory to search for files
        pattern: Glob pattern for file matching
        
    Returns:
        List of processed file paths
    """
    return list(input_dir.glob(pattern))
```

## Error Handling

- Use specific exception types, not bare `except:`
- Log errors with context information
- Provide helpful error messages to users
