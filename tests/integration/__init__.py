"""
Integration tests for PRISM.

This package contains two types of integration tests:

1. Real-World Scenarios (test_real_world_scenarios.py):
   - Tests with realistic content creator scripts
   - Validates end-to-end pipeline for actual use cases
   - Requires manual review of output videos
   - 5-8 tests covering different content types

2. Technical Boundaries (test_technical_boundaries.py):
   - Tests algorithm correctness at edge cases
   - Validates text wrapping, clipping, unicode, aspect ratios
   - Automated assertions, no manual review needed
   - 10-15 tests covering specific technical boundaries
"""
