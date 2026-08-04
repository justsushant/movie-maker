# Integration Test Refactor - Requirements

## Overview

Refactor the integration test suite to provide better real-world validation and clearer separation between user-facing scenarios and technical boundary testing. The current `test_subtitle_stress.py` generates 48 test combinations that are difficult to validate manually and don't reflect actual content creator use cases.

## Problem Statement

The current integration testing approach has several issues:

1. **Poor real-world representation**: Test fixtures use generic dummy text ("Good morning everyone") that doesn't reflect actual content creator scripts
2. **Combinatorial explosion**: 48 test combinations (6 text files × 8 video variants) make manual validation tedious and time-consuming
3. **Unclear test purpose**: Tests mix real-world scenario validation with technical edge case testing
4. **Difficult visual confirmation**: Output from 48 tests is overwhelming to review manually
5. **Maintenance burden**: Adding new scenarios or configs multiplies test count exponentially

## User Stories

### US-1: Content Creator Validation
**As a** developer maintaining KokoroMoviePy  
**I want** integration tests that use realistic content creator scripts  
**So that** I can validate the tool works for actual use cases and manually review output quality

**Acceptance Criteria:**
- 1.1: Tests use realistic scripts representing common content types (educational, product demo, tutorial, story, news)
- 1.2: Each script is 30-60 seconds of speech when rendered
- 1.3: Each test uses one sensible configuration appropriate for that content type
- 1.4: Test output is organized by scenario name for easy manual review
- 1.5: Tests validate basic correctness (files exist, structure valid) but rely on manual review for quality

### US-2: Algorithm Correctness Validation
**As a** developer maintaining KokoroMoviePy  
**I want** focused tests that validate technical boundaries and algorithm correctness  
**So that** I can catch edge cases and regressions in subtitle layout, wrapping, and rendering logic

**Acceptance Criteria:**
- 2.1: Tests focus on specific technical edge cases (text wrapping, unicode, extreme aspect ratios, overflow)
- 2.2: Tests use minimal input text stored in fixture files to isolate the behavior being tested
- 2.3: Tests include automated assertions for pixel-level checks, layout correctness, and clipping detection
- 2.4: Tests can run quickly without manual review
- 2.5: Each test validates one specific algorithm behavior or boundary condition
- 2.6: Test inputs are preserved in `tests/fixtures/technical/` for reproducibility

### US-3: Clear Test Organization
**As a** developer running tests  
**I want** clear separation between real-world scenarios and technical boundary tests  
**So that** I can run them independently and understand test failures quickly

**Acceptance Criteria:**
- 3.1: Real-world scenario tests are in `tests/integration/test_real_world_scenarios.py`
- 3.2: Technical boundary tests are in `tests/integration/test_technical_boundaries.py`
- 3.3: Test fixtures are organized in `tests/fixtures/real_world/` and `tests/fixtures/technical/`
- 3.4: Test outputs are organized in `output/test_real_world_scenarios/` and `output/test_technical_boundaries/`
- 3.5: Each test file can be run independently with pytest

### US-4: Manageable Test Count
**As a** developer maintaining tests  
**I want** a reasonable number of integration tests (15-25 total)  
**So that** I can run them regularly and review output without being overwhelmed

**Acceptance Criteria:**
- 4.1: Real-world scenario tests: 5-8 tests (one per content type)
- 4.2: Technical boundary tests: 10-15 tests (focused on specific edge cases)
- 4.3: Total integration test count is under 25
- 4.4: Tests complete in reasonable time (under 5 minutes on typical hardware)
- 4.5: `test_subtitle_stress.py` is removed after migration

### US-5: Realistic Test Content
**As a** developer validating output quality  
**I want** test scripts that represent actual content creator use cases  
**So that** I can confidently assess whether the tool produces acceptable results

**Acceptance Criteria:**
- 5.1: Educational explainer script includes technical terms and moderate pacing
- 5.2: Product demo script includes marketing language and calls to action
- 5.3: Story narration script includes dialogue and varied emotional tone
- 5.4: Tutorial walkthrough script includes step-by-step instructions
- 5.5: News announcement script uses formal, concise language
- 5.6: Each script is written as if by an actual content creator, not generic test text

## Non-Functional Requirements

### NFR-1: Test Execution Performance
- Real-world scenario tests should complete in under 3 minutes total
- Technical boundary tests should complete in under 2 minutes total
- Tests should be parallelizable where possible

### NFR-2: Output Organization
- Test outputs should be clearly named and organized for easy manual review
- Output directories should be gitignored but structure should be documented
- Failed test outputs should be preserved for debugging

### NFR-3: Clean Migration
- Old test fixtures in `tests/fixtures/text/` will be removed (not needed)
- Test configuration should use existing `config.py` infrastructure
- No changes to production code should be required
- Pytest fixtures in `conftest.py` should be updated for new structure

### NFR-4: Documentation
- Test purpose and validation approach should be documented in docstrings
- README or test documentation should explain how to run and review tests
- Fixture content should be self-documenting (realistic, readable scripts)

## Out of Scope

- Property-based testing (separate concern)
- Performance benchmarking tests (already exist in `tests/benchmark_performance.py`)
- Unit tests for individual components (already exist)
- CI/CD pipeline configuration changes
- Changes to production code or APIs
- Backward compatibility with existing test fixtures (will be replaced)

## Success Metrics

1. **Test count reduction**: From 48 to under 25 integration tests
2. **Manual review time**: Reduced from reviewing 48 outputs to reviewing 5-8 key scenarios
3. **Test clarity**: Each test has clear purpose documented in name and docstring
4. **Real-world coverage**: 5+ realistic content creator scenarios represented
5. **Edge case coverage**: 10+ specific technical boundaries validated with automated assertions

## Dependencies

- Existing test infrastructure (`conftest.py`, pytest fixtures)
- Existing fixture text files (may be reused or replaced)
- `config.py` test configuration system
- Pytest framework and existing test utilities

## Migration Strategy

1. Create new directory structure (`tests/integration/`, `tests/fixtures/real_world/`, `tests/fixtures/technical/`)
2. Write realistic scripts for real-world scenarios
3. Implement `test_real_world_scenarios.py` with 5-8 tests
4. Implement `test_technical_boundaries.py` with 10-15 tests, cherry-picking valuable assertions from `test_subtitle_stress.py`
5. Update `conftest.py` with new fixtures for new directory structure
6. Verify all new tests pass
7. Delete `test_subtitle_stress.py` and old fixtures in `tests/fixtures/text/`
8. Update documentation and Makefile if needed
