---
name: "python-testing-best-practices"
displayName: "Python Testing Best Practices"
description: "Comprehensive guide to testing Python applications with pytest, including patterns for unit tests, integration tests, and test organization strategies."
keywords: ["python", "pytest", "testing", "unit-test", "tdd"]
author: "Example Author"
---

# Python Testing Best Practices

## Overview

This power provides comprehensive best practices for testing Python applications. It covers test organization, pytest patterns, mocking strategies, and common pitfalls to avoid. Whether you're writing unit tests, integration tests, or end-to-end tests, these guidelines will help you write maintainable and effective test suites.

## Core Principles

1. **Test Isolation** - Each test should be independent and not rely on other tests
2. **Clear Test Names** - Test names should describe what they're testing and expected behavior
3. **Arrange-Act-Assert** - Structure tests with clear setup, execution, and verification phases
4. **Fast Feedback** - Keep tests fast to encourage frequent running
5. **Meaningful Assertions** - Use specific assertions that provide clear failure messages

## Patterns

### Pattern: Test Organization

**Structure your tests to mirror your source code:**

```
project/
├── src/
│   ├── module_a.py
│   └── module_b.py
└── tests/
    ├── test_module_a.py
    └── test_module_b.py
```

### Pattern: Fixture Usage

**Good - Reusable fixtures:**
```python
import pytest

@pytest.fixture
def sample_user():
    return {"name": "John", "email": "john@example.com"}

def test_user_creation(sample_user):
    assert sample_user["name"] == "John"
```

**Bad - Duplicated setup:**
```python
def test_user_creation():
    user = {"name": "John", "email": "john@example.com"}
    assert user["name"] == "John"

def test_user_email():
    user = {"name": "John", "email": "john@example.com"}  # Duplicated
    assert user["email"] == "john@example.com"
```

### Pattern: Mocking External Dependencies

**Good - Mock external services:**
```python
from unittest.mock import patch

def test_api_call(mocker):
    mocker.patch('requests.get', return_value=MockResponse())
    result = fetch_data()
    assert result.status_code == 200
```

## Best Practices

- Write tests before or alongside code (TDD approach)
- Keep tests simple and focused on one behavior
- Use descriptive test names that explain the scenario
- Avoid testing implementation details
- Use fixtures for common setup
- Mock external dependencies to keep tests fast
- Run tests frequently during development
- Maintain test code quality as you would production code

## Common Pitfalls

- **Flaky tests** - Tests that pass/fail randomly due to timing or state issues
- **Slow test suites** - Tests that take too long discourage frequent running
- **Brittle tests** - Tests that break with minor refactoring
- **Testing implementation** - Tests coupled to internal implementation rather than behavior

## Quick Reference

### Common pytest Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_module.py

# Run tests matching pattern
pytest -k "test_user"

# Run with coverage
pytest --cov=src tests/

# Run in parallel
pytest -n auto
```

### Useful pytest Markers

```python
@pytest.mark.skip(reason="Not implemented yet")
@pytest.mark.parametrize("input,expected", [(1, 2), (3, 4)])
@pytest.mark.slow  # Custom marker for slow tests
```

---

**Testing Framework:** pytest
**Documentation:** https://docs.pytest.org/
