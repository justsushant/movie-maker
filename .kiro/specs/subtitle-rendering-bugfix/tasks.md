# Implementation Plan: Subtitle Rendering Bugfix

## Overview

This plan implements fixes for two critical subtitle rendering bugs:
1. Character width overestimation causing overflow in narrow videos
2. Incorrect word filtering causing sudden sentence breaks in word-highlight mode

The implementation follows a phased approach: fix character width estimation first, then enhance data model, then fix word filtering. Each phase includes testing to catch regressions early.

## Tasks

- [x] 1. Fix character width estimation ratio
  - [x] 1.1 Update `_max_chars_for_context()` to use 0.50 ratio
    - Change `avg_char_px = max(1, int(context.font_size * 0.55))` to use 0.50
    - Located at line ~76 in `subtitle/layouts.py`
    - _Requirements: 1.1, 1.4_
  
  - [x] 1.2 Update `_wrap_sentence_text()` to use 0.50 ratio
    - Change `avg_char_px = max(1, int(context.font_size * 0.55))` to use 0.50
    - Located at line ~48 in `subtitle/layouts.py`
    - _Requirements: 1.1, 1.4, 4.3_
  
  - [x] 1.3 Run stress tests to verify character width fix
    - Execute `make test-stress` or `pytest tests/test_subtitle_stress.py -v`
    - Verify phone portrait tests pass (720x1280, 1080x1920)
    - Verify edge clipping assertions pass
    - _Requirements: 5.1, 5.2, 7.1_

- [x] 2. Checkpoint - Verify character width fixes
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Enhance _TimedChunk data model
  - [x] 3.1 Add word_indices field to _TimedChunk dataclass
    - Add `word_indices: List[int]` field after `end_time` field
    - Add import for `List` from typing if not already present
    - Located at line ~68 in `subtitle/layouts.py`
    - _Requirements: 7.1, 6.5_
  
  - [x] 3.2 Update _build_single_line_chunks() to track word indices
    - Add `current_word_indices: List[int] = []` variable initialization
    - Change `for w in words:` to `for i, w in enumerate(words):`
    - When appending to current_words, also append `i` to current_word_indices
    - When creating _TimedChunk objects, add `word_indices=current_word_indices.copy()`
    - Handle the empty words case by adding `word_indices=[]` to the early return
    - Located at line ~81-140 in `subtitle/layouts.py`
    - _Requirements: 7.1, 7.3, 7.4_
  
  - [x]* 3.3 Run stress tests to verify data model changes don't break anything
    - Execute `make test-stress`
    - Verify all 48 test combinations still pass
    - Verify no regressions in any subtitle mode
    - _Requirements: 5.1, 6.1, 6.2, 7.1_

- [x] 4. Checkpoint - Verify data model enhancement
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Fix word filtering in WordHighlightLayout
  - [x] 5.1 Replace time-based word filtering with index-based filtering
    - In `WordHighlightLayout.layout_frame()`, replace the word filtering loop
    - Old: `for w in seg.words: if w.start_time <= active_chunk.end_time and w.end_time >= active_chunk.start_time: active_words.append(w)`
    - New: `active_words = [seg.words[i] for i in active_chunk.word_indices]`
    - Remove the entire filtering loop and replace with single line
    - Located at line ~268-275 in `subtitle/layouts.py`
    - _Requirements: 3.1, 3.2, 3.3, 3.5, 7.2, 7.3_
  
  - [x]* 5.2 Run stress tests to verify word-highlight fix
    - Execute `make test-stress`
    - Specifically verify word-highlight mode tests pass
    - Check punctuation_heavy tests for smooth transitions
    - Verify no sudden sentence breaks mid-display
    - _Requirements: 5.1, 5.3, 3.1, 3.2_

- [x] 6. Checkpoint - Verify word filtering fix
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Final validation and testing
  - [x] 7.1 Run complete stress test suite
    - Execute `make test-stress` with verbose output
    - Verify all 48 test combinations pass (6 text cases × 8 video variants)
    - Document any test failures and analyze root cause
    - _Requirements: 5.1, 5.5, 7.1, 7.2_
  
  - [x] 7.2 Manually inspect problematic test cases
    - Check `output/test/punctuation_heavy_phone_1080x1920_sentence_highlight/`
    - Check `output/test/long_paragraph_720_sentence_multiline/`
    - Verify no edge clipping in phone portrait videos
    - Verify smooth word transitions in word-highlight mode
    - _Requirements: 2.1, 2.2, 3.1, 3.2_
  
  - [x] 7.3 Evaluate need for additional tests
    - Review if any new edge cases were discovered during implementation
    - Determine if additional unit tests are needed for duplicate words
    - Determine if additional tests are needed for very narrow screens
    - Add new test cases if necessary
    - _Requirements: 7.4, 7.5_

- [x] 8. Final checkpoint - Implementation complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional test validation tasks that can be skipped for faster iteration
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and catch issues early
- The phased approach (character width → data model → word filtering) allows isolating issues
- All changes are in `subtitle/layouts.py` - no other files need modification
- Existing stress tests provide comprehensive coverage - no new tests need to be written
- If any tests fail, analyze whether it's due to bugs being fixed or new regressions
