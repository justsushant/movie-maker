# Integration Test Refactor - Tasks

## 1. Setup Directory Structure
Create new directory structure for integration tests and fixtures.

- [x] 1.1 Create `tests/integration/` directory
- [x] 1.2 Create `tests/integration/__init__.py`
- [x] 1.3 Create `tests/fixtures/real_world/` directory
- [x] 1.4 Create `tests/fixtures/technical/` directory

## 2. Write Real-World Test Fixtures
Create realistic content creator scripts for real-world scenario testing.

- [x] 2.1 Write `educational_explainer.txt` - Technical terms, moderate pacing (30-60 sec)
- [x] 2.2 Write `product_demo.txt` - Marketing language, calls to action (30-60 sec)
- [x] 2.3 Write `story_narration.txt` - Dialogue, emotional variation (30-60 sec)
- [x] 2.4 Write `tutorial_walkthrough.txt` - Step-by-step instructions (30-60 sec)
- [x] 2.5 Write `news_announcement.txt` - Formal, concise language (30-60 sec)

## 3. Write Technical Test Fixtures
Create minimal edge case inputs for technical boundary testing.

- [x] 3.1 Write `extreme_long_word.txt` - Single very long word
- [x] 3.2 Write `unicode_stress.txt` - Emoji, accented chars, CJK characters
- [x] 3.3 Write `punctuation_heavy.txt` - Multiple punctuation marks, quotes, dashes
- [x] 3.4 Write `multiline_wrap_test.txt` - Long sentence for wrapping tests
- [x] 3.5 Write `single_word.txt` - Minimal single word input

## 4. Update Pytest Fixtures
Update conftest.py with new fixture functions for integration tests.

- [x] 4.1 Add `real_world_fixture_dir` fixture
- [x] 4.2 Add `technical_fixture_dir` fixture
- [x] 4.3 Add `real_world_output_dir` fixture
- [x] 4.4 Add `technical_output_dir` fixture
- [x] 4.5 Remove `fixture_text_dir` fixture (no longer needed)

## 5. Create Helper Functions Module
Extract and organize validation helper functions.

- [x] 5.1 Create `tests/integration/helpers.py`
- [x] 5.2 Copy `validate_subtitle_json_structure` from test_library_api.py
- [x] 5.3 Copy `assert_frame_has_subtitle_pixels` from test_subtitle_stress.py
- [x] 5.4 Copy `assert_no_horizontal_edge_clipping` from test_subtitle_stress.py
- [x] 5.5 Copy `assert_sentence_layout_wraps` from test_subtitle_stress.py
- [x] 5.6 Copy `assert_single_line_layout` from test_subtitle_stress.py
- [x] 5.7 Add `get_integration_test_config` helper function

## 6. Implement Real-World Scenario Tests
Create test_real_world_scenarios.py with realistic use case tests.

- [x] 6.1 Create `tests/integration/test_real_world_scenarios.py`
- [x] 6.2 Implement `test_educational_explainer` - 1080p landscape, sentence_with_word_highlight
- [x] 6.3 Implement `test_product_demo` - 1080p landscape, sentence_with_word_highlight
- [x] 6.4 Implement `test_story_narration` - 1080p landscape, sentence mode
- [x] 6.5 Implement `test_tutorial_walkthrough` - 720p landscape, sentence_with_word_highlight
- [x] 6.6 Implement `test_news_announcement` - 1080p landscape, sentence mode
- [x] 6.7 Add module docstring explaining test purpose and validation approach
- [x] 6.8 Run tests and verify all pass

## 7. Implement Technical Boundary Tests - Text Wrapping
Create tests for text wrapping and layout behavior.

- [x] 7.1 Create `tests/integration/test_technical_boundaries.py`
- [x] 7.2 Implement `test_multiline_wrapping_narrow_width` - Portrait with multiline enabled
- [x] 7.3 Implement `test_single_line_truncation` - Portrait with multiline disabled
- [x] 7.4 Implement `test_stacking_overflow` - More lines than max_visible_lines
- [x] 7.5 Add module docstring explaining test purpose

## 8. Implement Technical Boundary Tests - Edge Clipping
Create tests for edge clipping detection.

- [x] 8.1 Implement `test_no_clipping_portrait_narrow` - 720x1280 portrait
- [x] 8.2 Implement `test_no_clipping_landscape_wide` - 1920x1080 landscape

## 9. Implement Technical Boundary Tests - Unicode & Special Characters
Create tests for unicode and punctuation handling.

- [x] 9.1 Implement `test_unicode_rendering` - Emoji, accented chars, CJK
- [x] 9.2 Implement `test_punctuation_heavy` - Multiple punctuation marks

## 10. Implement Technical Boundary Tests - Extreme Aspect Ratios
Create tests for extreme aspect ratios.

- [x] 10.1 Implement `test_ultra_wide_4k` - 3840x2160 landscape
- [x] 10.2 Implement `test_portrait_phone` - 720x1280 portrait
- [x] 10.3 Implement `test_square_format` - 1080x1080 square

## 11. Implement Technical Boundary Tests - Subtitle Modes
Create tests for different subtitle modes.

- [x] 11.1 Implement `test_word_only_mode` - Single word display
- [x] 11.2 Implement `test_stacking_mode_direction_up` - Stacking with upward direction
- [x] 11.3 Implement `test_sentence_highlight_mode` - Sentence with word highlighting

## 12. Implement Technical Boundary Tests - Edge Cases
Create tests for minimal and extreme inputs.

- [x] 12.1 Implement `test_single_word_input` - Minimal input
- [x] 12.2 Implement `test_very_long_word` - Word longer than typical line width
- [x] 12.3 Run all technical boundary tests and verify they pass

## 13. Verify Test Suite
Run complete test suite and verify functionality.

- [x] 13.1 Run `pytest tests/integration/test_real_world_scenarios.py` - verify all pass
- [x] 13.2 Run `pytest tests/integration/test_technical_boundaries.py` - verify all pass
- [x] 13.3 Run `pytest tests/integration/` - verify all pass together
- [x] 13.4 Manually review output videos in `output/test_real_world_scenarios/`
- [x] 13.5 Verify test execution time is under 5 minutes

## 14. Cleanup Old Tests
Remove old test files and fixtures.

- [x] 14.1 Delete `tests/test_subtitle_stress.py`
- [x] 14.2 Delete `tests/fixtures/text/` directory and all contents
- [x] 14.3 Verify no other tests reference deleted fixtures
- [x] 14.4 Run full test suite to ensure nothing broke

## 15. Update Documentation
Update documentation to reflect new test structure.

- [x] 15.1 Update Makefile if test commands need changes
- [x] 15.2 Add comment in conftest.py explaining new fixture structure
- [x] 15.3 Update any README or test documentation mentioning old test structure
- [x] 15.4 Document manual review process for real-world scenario tests

## 16. Final Verification
Final checks before completion.

- [x] 16.1 Run complete test suite: `pytest tests/`
- [x] 16.2 Verify test count is 15-25 integration tests
- [x] 16.3 Verify output directories are properly organized
- [x] 16.4 Verify all old fixtures and tests are removed
- [x] 16.5 Commit changes with clear commit message
