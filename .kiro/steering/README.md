---
inclusion: always
---

# AI Agent Context Index

This directory contains comprehensive context documentation for AI agents working on the PRISM codebase.

## Context Files

### 1. **product.md** - Product Overview
- What PRISM is and its purpose
- Target users and key features
- Pipeline flow and design goals
- **Read this first** to understand the project

### 2. **structure.md** - Project Structure
- Directory layout and file organization
- Architecture diagrams
- Module relationships and data flow
- Import patterns and conventions
- **Read this** to understand how the code is organized

### 3. **tech.md** - Tech Stack
- Language and framework choices
- Core dependencies and versions
- Development and testing tools
- Technical constraints and requirements
- **Read this** to understand the technology choices

### 4. **agents.md** - Agent Guidelines
- How to approach this codebase
- Architectural principles (SOLID, design patterns)
- Code style and conventions
- Testing expectations and workflows
- Common development tasks
- **Read this** to understand how to work on the codebase

### 5. **development-workflow.md** - Development Workflows
- Step-by-step workflows for common tasks
- Setting up development environment
- Running tests and debugging
- Adding new features and fixing bugs
- Performance optimization
- Code review and release processes
- **Read this** when you need to perform a specific task

### 6. **quick-reference.md** - Quick Reference
- Common commands and file locations
- Key classes and functions
- Frame format specifications
- Testing patterns and examples
- Troubleshooting tips
- Performance benchmarks
- **Read this** when you need to look something up quickly

### 7. **common-patterns.md** - Common Patterns
- Implementation patterns used in PRISM
- Design patterns with examples
- Testing patterns
- Error handling patterns
- Performance patterns
- SOLID principles in practice
- **Read this** to understand the coding patterns used

## Recommended Reading Order

### First Time Setup
1. `product.md` - Understand what PRISM does
2. `structure.md` - Understand the codebase organization
3. `tech.md` - Understand the technology stack
4. `quick-reference.md` - Get familiar with common commands

### Before Starting a Task
1. `agents.md` - Review agent guidelines
2. `development-workflow.md` - Find the relevant workflow
3. `common-patterns.md` - Review relevant patterns

### During Development
1. `quick-reference.md` - Look up specific APIs or patterns
2. `agents.md` - Refer to conventions and testing requirements

### When Adding Features
1. `development-workflow.md` - Follow the feature addition workflow
2. `common-patterns.md` - Use appropriate patterns
3. `agents.md` - Ensure you follow conventions

### When Fixing Bugs
1. `development-workflow.md` - Follow the bug fixing workflow
2. `agents.md` - Check error handling patterns
3. `quick-reference.md` - Look up relevant APIs

### When Optimizing Performance
1. `common-patterns.md` - Review performance patterns
2. `quick-reference.md` - Check performance benchmarks
3. `tech.md` - Understand technical constraints

## Key Concepts

### Project Overview
- **PRISM**: Python-based video generation system
- **Purpose**: Generate narrated videos with subtitles, motion, and effects
- **Key Features**: TTS, video engine, subtitle system, transitions, audio-reactive effects

### Architecture
- **SOLID Principles**: Applied throughout
- **Design Patterns**: Strategy, Adapter, Factory, Protocol, Template Method
- **Modular Design**: Independent modules for TTS, engine, subtitles

### Development
- **Testing**: 300+ tests, property-based testing, visual regression tests
- **Commands**: `make setup`, `make run`, `make test`
- **Frame Format**: `(height, width, 3)` uint8 RGB numpy arrays

### Modules
- **engine/**: Video engine (motion, transitions, effects)
- **subtitle/**: Subtitle system (source → layout → renderer)
- **tts/**: Text-to-speech with word-level timestamps
- **pipeline/**: Pipeline orchestration with dependency injection

## Important Notes

### For AI Agents
- Always check `.kiro/specs/` for existing specifications
- Always write tests for new code
- Always follow SOLID principles
- Always update documentation when adding features
- Use dependency injection for all components
- Frame format is RGB, not BGR

### Critical Path
- TTS → Punctuation → Grouping → Audio Analysis → Scene Planning → Frame Rendering → Subtitle Overlay → Encoding

### Performance
- 1080p: ~2-3ms per frame (no effects)
- Effects: ~5-10ms per effect
- Transitions: <150ms
- Audio analysis: ~0.5-1.0s for 10s audio

### Testing
- Unit tests: Test components in isolation
- Integration tests: Test multi-component workflows
- Property-based tests: Validate universal properties
- Visual regression tests: Compare frame outputs

## Getting Help

1. **Check existing documentation**: Look in `docs/`
2. **Check context files**: This directory and `.kiro/steering/`
3. **Check similar code**: Look at existing implementations
4. **Check tests**: Test files show usage examples

## Updating This Index

When adding new context files:
1. Update this file to include the new file
2. Update the recommended reading order if applicable
3. Add any relevant information to key concepts section
4. Keep the file organized and easy to navigate

## Related Files

- `.opencoderules`: Project context and rules for checking specs and docs
- `.kiro/specs/`: Specifications for features and changes
- `docs/`: Comprehensive project documentation
- `tests/conftest.py`: Test fixtures and configuration

## Version

Last updated: March 8, 2026

For questions or issues with this context documentation, refer to the project's README.md or create an issue in the repository.
