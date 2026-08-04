# Design Document: File Organization Refactor

## Overview

This design specifies the technical approach for reorganizing two misplaced root-level files (`subtitle_config.py` and `renderer.py`) into appropriate module directories. The refactoring improves code organization by co-locating related functionality while maintaining backward compatibility and ensuring all tests continue to pass.

The refactoring involves:
1. Moving `subtitle_config.py` → `subtitle/config.py`
2. Moving `renderer.py` → `rendering/video.py`
3. Updating all import paths across the codebase
4. Creating new module `__init__.py` files with proper exports

## Architecture

### Current Structure

```
kokoromoviepy/
├── subtitle_config.py          # ❌ Root level (should be in subtitle/)
├── renderer.py                 # ❌ Root level (should be in rendering/)
├── subtitle/
│   ├── __init__.py
│   ├── interfaces.py
│   ├── source.py
│   ├── composer.py
│   ├── layouts.py
│   └── renderer.py            # PIL-based text rendering
├── api/
│   ├── __init__.py
│   └── library.py             # Imports both files
└── [other modules...]
```

### Target Structure

```
kokoromoviepy/
├── subtitle/
│   ├── __init__.py            # ✅ Exports SubtitleConfig, SubtitleMode, etc.
│   ├── config.py              # ✅ Moved from root
│   ├── interfaces.py
│   ├── source.py
│   ├── composer.py
│   ├── layouts.py
│   └── renderer.py
├── rendering/                 # ✅ New module
│   ├── __init__.py            # ✅ Exports create_video
│   └── video.py               # ✅ Moved from root renderer.py
├── api/
│   ├── __init__.py
│   └── library.py             # ✅ Updated imports
└── [other modules...]
```

### Module Responsibilities

**`subtitle/config.py`** (formerly `subtitle_config.py`):
- Contains configuration dataclasses: `SubtitleConfig`, `StackingConfig`
- Contains enums: `SubtitleMode`
- Contains type aliases: `Color`
- Pure data structures with no external dependencies beyond standard library

**`rendering/video.py`** (formerly `renderer.py`):
- Contains `create_video()` function for video composition
- Orchestrates MoviePy VideoClip creation
- Wires together subtitle components (source, layout, renderer)
- Handles audio/video muxing and MP4 export
- Depends on: subtitle module, MoviePy, config

## Components and Interfaces

### File Movement Operations

#### Operation 1: Move subtitle_config.py

```python
# Source: subtitle_config.py (root)
# Destination: subtitle/config.py

# File contents remain identical - no code changes
# Only the file location changes
```

#### Operation 2: Move renderer.py

```python
# Source: renderer.py (root)
# Destination: rendering/video.py

# File contents remain identical - no code changes
# Only the file location changes
```

### Import Path Updates

#### Files Importing subtitle_config

The following files need import updates:

**Within subtitle/ module:**
- `subtitle/interfaces.py`: `from subtitle_config import` → `from subtitle.config import`
- `subtitle/layouts.py`: `from subtitle_config import` → `from subtitle.config import`
- `subtitle/renderer.py`: `from subtitle_config import` → `from subtitle.config import`
- `subtitle/composer.py`: `from subtitle_config import` → `from subtitle.config import`

**API module:**
- `api/library.py`: `from subtitle_config import` → `from subtitle.config import`
- `api/__init__.py`: `from subtitle_config import` → `from subtitle.config import`

**Root files:**
- `main.py`: `from subtitle_config import` → `from subtitle.config import`

**Test files:**
- `tests/test_subtitle_layouts.py`
- `tests/test_library_api.py`
- `tests/integration/helpers.py`
- `tests/benchmark_performance.py`
- `tests/profile_performance.py`
- `tests/profile_pipeline.py`

**Documentation files:**
- `README.md` (code examples)
- `docs/subtitles.md` (code examples)
- `docs/how_it_works.md` (code examples)

#### Files Importing renderer

Only one file imports renderer:
- `api/library.py`: `from renderer import create_video` → `from rendering.video import create_video`

### Module __init__.py Files

#### subtitle/__init__.py

Update to export relocated config classes:

```python
"""Subtitle system for video generation with word-level timing."""

from subtitle.config import (
    Color,
    SubtitleConfig,
    SubtitleMode,
    StackingConfig,
)
from subtitle.interfaces import (
    ISubtitleSource,
    ISubtitleLayout,
    ISubtitleRenderer,
    SubtitleSegment,
    PositionedSubtitle,
    SubtitleLayoutContext,
)
from subtitle.source import JsonSubtitleSource
from subtitle.composer import SubtitleFrameComposer
from subtitle.layouts import (
    SentenceLayout,
    WordOnlyLayout,
    WordHighlightLayout,
    StackingLayout,
)
from subtitle.renderer import PillowSubtitleRenderer

__all__ = [
    # Config
    "Color",
    "SubtitleConfig",
    "SubtitleMode",
    "StackingConfig",
    # Interfaces
    "ISubtitleSource",
    "ISubtitleLayout",
    "ISubtitleRenderer",
    "SubtitleSegment",
    "PositionedSubtitle",
    "SubtitleLayoutContext",
    # Implementations
    "JsonSubtitleSource",
    "SubtitleFrameComposer",
    "SentenceLayout",
    "WordOnlyLayout",
    "WordHighlightLayout",
    "StackingLayout",
    "PillowSubtitleRenderer",
]
```

#### rendering/__init__.py (new file)

Create new module with exports:

```python
"""Video rendering and composition."""

from rendering.video import create_video

__all__ = [
    "create_video",
]
```

## Data Models

No data model changes - this is a pure refactoring. All classes, functions, and data structures remain identical.

## Correctness Properties


A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Content Preservation

*For any* file that is moved during the refactoring, the file content (excluding import statements) should be byte-for-byte identical before and after the move.

**Validates: Requirements 1.2, 2.3, 7.2**

### Property 2: Import Path Modernization

*For all* Python files in the codebase (including documentation), no occurrences of the old import patterns (`from subtitle_config import` or `import subtitle_config` or `from renderer import`) should remain after refactoring.

**Validates: Requirements 1.3, 6.3**

### Property 3: Symbol Availability

*For all* symbols that were importable before refactoring (SubtitleConfig, SubtitleMode, StackingConfig, Color, create_video), they should remain importable from their new locations after refactoring.

**Validates: Requirements 1.4, 3.4**

### Property 4: Behavior Preservation

*For all* tests in the test suite that passed before refactoring, they should continue to pass after refactoring with identical results.

**Validates: Requirements 4.2, 7.3**

## Error Handling

This refactoring should not introduce new error conditions. All existing error handling remains unchanged.

### Potential Issues During Refactoring

1. **Circular import errors**: If imports are updated incorrectly, circular dependencies could be introduced
   - Mitigation: Update imports in dependency order (leaf modules first)
   - Verification: Run Python import checks after each file update

2. **Missing imports**: If any file is missed during import updates, it will fail at runtime
   - Mitigation: Use automated search (grep/ripgrep) to find all import statements
   - Verification: Run full test suite to catch any missed imports

3. **Git history loss**: If files are copied instead of moved, git history is lost
   - Mitigation: Use `git mv` command for all file moves
   - Verification: Check `git log --follow` on moved files

4. **Module initialization errors**: If `__init__.py` files are incorrect, imports will fail
   - Mitigation: Test imports immediately after creating `__init__.py` files
   - Verification: Run `python -c "from subtitle.config import SubtitleConfig"` style checks

## Testing Strategy

### Dual Testing Approach

This refactoring requires both unit tests and property-based tests to ensure correctness:

**Unit Tests** (specific examples and edge cases):
- Verify specific files exist at new locations
- Verify specific files don't exist at old locations
- Verify specific `__init__.py` files have correct exports
- Verify specific import statements in key files (api/library.py, main.py)
- Verify `__all__` lists are defined in new `__init__.py` files

**Property Tests** (universal properties across all inputs):
- Content preservation across all moved files
- No old import patterns in any Python or documentation files
- All previously importable symbols remain importable
- All previously passing tests continue to pass

### Test Configuration

- Property tests should run with minimum 100 iterations
- Each property test must reference its design document property
- Tag format: **Feature: file-organization-refactor, Property {number}: {property_text}**

### Testing Libraries

- **pytest**: For unit tests and test discovery
- **Hypothesis**: For property-based testing (Python PBT library)
- **ast module**: For parsing Python files to verify imports programmatically

### Test Execution Order

1. **Pre-refactoring snapshot**: Capture current state (file locations, imports, test results)
2. **File movement tests**: Verify files moved to correct locations
3. **Import update tests**: Verify all imports updated correctly
4. **Module export tests**: Verify `__init__.py` files export correct symbols
5. **Property tests**: Verify all correctness properties hold
6. **Integration tests**: Run full test suite to verify behavior preservation
7. **Documentation tests**: Verify documentation examples use new import paths

### Refactoring Verification Checklist

After completing the refactoring, verify:

- [ ] `subtitle_config.py` does not exist at root
- [ ] `renderer.py` does not exist at root
- [ ] `subtitle/config.py` exists and contains all original classes
- [ ] `rendering/video.py` exists and contains all original functions
- [ ] `rendering/__init__.py` exists and exports `create_video`
- [ ] `subtitle/__init__.py` exports config classes
- [ ] No files contain `from subtitle_config import`
- [ ] No files contain `from renderer import`
- [ ] All tests pass with same results as before refactoring
- [ ] Documentation examples use new import paths
- [ ] Git history preserved for moved files (`git log --follow` works)

## Implementation Notes

### Import Update Strategy

Update imports in this order to avoid circular dependencies:

1. **Leaf modules first**: Start with files that don't import from each other
   - `subtitle/interfaces.py` (only imports from subtitle_config)
   - `subtitle/renderer.py` (only imports from subtitle_config)
   
2. **Mid-level modules**: Files that import from leaf modules
   - `subtitle/layouts.py` (imports from interfaces and subtitle_config)
   - `subtitle/composer.py` (imports from interfaces and subtitle_config)
   
3. **Top-level modules**: Files that import from mid-level modules
   - `rendering/video.py` (imports from subtitle modules)
   - `api/library.py` (imports from rendering and subtitle)
   - `main.py` (imports from api)

4. **Test files**: Update after all source files are updated

5. **Documentation**: Update last since these are not executed

### Module __init__.py Update Strategy

1. Create `rendering/__init__.py` first (no dependencies)
2. Update `subtitle/__init__.py` to include config exports
3. Verify imports work: `python -c "from subtitle.config import SubtitleConfig"`
4. Verify imports work: `python -c "from rendering.video import create_video"`

### Git Commands

```bash
# Move files preserving history
git mv subtitle_config.py subtitle/config.py
git mv renderer.py rendering/video.py

# Create new module directory
mkdir rendering
touch rendering/__init__.py

# Verify history preserved
git log --follow subtitle/config.py
git log --follow rendering/video.py
```

### Automated Import Updates

Use ripgrep to find all files needing updates:

```bash
# Find all files importing subtitle_config
rg "from subtitle_config import|import subtitle_config" --type py

# Find all files importing renderer
rg "from renderer import|import renderer" --type py

# Find old patterns in documentation
rg "from subtitle_config import|from renderer import" --type md
```

## Migration Guide for External Users

If this library is used externally, users should update their imports:

### Old Import Patterns (Deprecated)

```python
# Old way - no longer works
from subtitle_config import SubtitleConfig, SubtitleMode
from renderer import create_video
```

### New Import Patterns (Current)

```python
# New way - use these imports
from subtitle.config import SubtitleConfig, SubtitleMode
from rendering.video import create_video

# Or import from module root
from subtitle import SubtitleConfig, SubtitleMode
from rendering import create_video
```

### Backward Compatibility

For this refactoring, we are NOT providing backward compatibility shims. The old import paths will immediately stop working. This is acceptable because:

1. This appears to be an internal project (not published to PyPI)
2. The refactoring is straightforward with clear new paths
3. All internal code is updated simultaneously
4. The test suite will catch any missed imports

If backward compatibility is needed in the future, we could add deprecation shims:

```python
# In root __init__.py or a compatibility module
import warnings
from subtitle.config import SubtitleConfig as _SubtitleConfig

def __getattr__(name):
    if name == "SubtitleConfig":
        warnings.warn(
            "Importing SubtitleConfig from root is deprecated. "
            "Use 'from subtitle.config import SubtitleConfig' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return _SubtitleConfig
    raise AttributeError(f"module has no attribute '{name}'")
```

However, this is not recommended for this refactoring as it adds complexity without clear benefit.
