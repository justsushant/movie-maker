# Subtitle Timestamp Reset Bugfix - Tasks

## Overview

**Goal:** Fix timestamp reset bug with minimal, surgical code change  
**Scope:** Single file (`tts/kokoro_engine.py`), ~10 lines moved  
**Validation:** Existing integration tests + debug scripts  
**Total Time:** 20-30 minutes

## Task Breakdown

### 1. Implement Core Fix (10 min)
**Validates:** US-1, US-3

- [ ] 1.1 Open `tts/kokoro_engine.py`
- [ ] 1.2 Locate `generate()` method (lines 66-91)
- [ ] 1.3 Move token processing inside batch loop:
  - [ ] Calculate `time_offset` inside `for result in generator:` loop
  - [ ] Update offset formula: `sum(audio_segments)/24000 + sum(paragraph_audio)/24000`
  - [ ] Process tokens immediately after offset calculation
  - [ ] Remove `paragraph_tokens` intermediate list
- [ ] 1.4 Add inline comment explaining per-batch offset calculation
- [ ] 1.5 Verify type hints and code style match existing code

**Expected Result:** Token timestamps calculated per batch, not per paragraph

### 2. Run Integration Tests (5 min)
**Validates:** US-1 AC 1.1-1.4, US-2 AC 2.1-2.2

- [ ] 2.1 Run integration test suite: `pytest tests/integration/test_real_world_scenarios.py -v`
- [ ] 2.2 Verify all 5 tests pass:
  - [ ] `test_educational_explainer`
  - [ ] `test_product_demo`
  - [ ] `test_story_narration`
  - [ ] `test_tutorial_walkthrough`
  - [ ] `test_news_announcement`

**Expected Result:** All tests pass (previously they passed but with incorrect timestamps)

### 3. Validate Fix with Debug Scripts (5 min)
**Validates:** US-1 AC 1.2, 1.4

- [ ] 3.1 Run timestamp reset detector: `python debug_timestamp_issue.py`
  - [ ] Verify: "No timestamp issues found!" for all 5 test cases
  - [ ] Before fix: Shows 1 reset per test case
  
- [ ] 3.2 Run audio/subtitle sync checker: `python debug_audio_duration.py`
  - [ ] Verify: Audio duration matches max subtitle time (±0.5s) for all tests
  - [ ] Before fix: Shows 13-20s gaps

**Expected Result:** Zero timestamp resets, full audio coverage

### 4. Regression Check (5 min)
**Validates:** No breaking changes

- [ ] 4.1 Run full test suite: `pytest tests/ -v`
- [ ] 4.2 Verify no new test failures
- [ ] 4.3 Check technical boundary tests still pass

**Expected Result:** All existing tests continue to pass

### 5. User Visual Verification (Required)
**Validates:** US-2 AC 2.1, 2.2

- [ ] 5.1 **User reviews test videos** - Play one or more videos from `output/test/test_real_world_scenarios/`
  - Recommended: `educational_explainer/output_video.mp4` (43s)
  - Check: Subtitles appear throughout entire duration
  - Check: Smooth transitions with no flashing
  - Check: Word highlighting syncs with audio

**Expected Result:** User confirms subtitles are correct throughout video

## Task Dependencies

```
1. Implement Core Fix (CRITICAL)
  ↓
2. Run Integration Tests (CRITICAL)
  ↓
3. Validate with Debug Scripts (HIGH)
  ↓
4. Regression Check (HIGH)
  ↓
5. User Visual Verification (REQUIRED)
```

## Time Estimates

| Task | Time | Priority | Can Skip? |
|------|------|----------|-----------|
| 1. Core Fix | 10 min | CRITICAL | No |
| 2. Integration Tests | 5 min | CRITICAL | No |
| 3. Debug Scripts | 5 min | HIGH | No |
| 4. Regression Check | 5 min | HIGH | No |
| 5. User Visual Verification | 2-5 min | REQUIRED | No |

**Total Time:** 27-30 minutes (all tasks required)

## Success Criteria

✅ **Must Have (Critical)**
- [ ] All 5 integration tests pass
- [ ] Zero timestamp resets detected by `debug_timestamp_issue.py`
- [ ] Audio duration matches subtitle coverage (±0.5s) per `debug_audio_duration.py`
- [ ] No regression in existing tests

✅ **Should Have (High Priority)**
- [ ] Code follows existing style and type hints
- [ ] Inline comment explains the fix

✅ **Nice to Have (Optional)**
- [ ] Manual video verification shows smooth playback

## User Verification Checkpoint

After automated tests pass, **pause for user visual verification**:
1. User plays test video(s) to verify subtitle quality
2. User confirms no flashing, complete coverage, smooth transitions
3. If issues found, investigate before proceeding
4. If all looks good, fix is complete!

## Rollback Criteria

🚨 **Rollback immediately if:**
- Any integration test fails after the fix
- New test failures appear in regression check
- Timestamp resets still detected by debug script

**Rollback procedure:** `git checkout tts/kokoro_engine.py`
