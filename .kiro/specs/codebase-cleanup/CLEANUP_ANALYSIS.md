# Cleanup Analysis - Files to Remove

## Summary

The app has been successfully refactored with new modular APIs. This document identifies files that can be safely removed as they are:
1. Debug/analysis files created during development
2. Deprecated code with replacement APIs
3. Tests for deprecated functionality
4. Legacy configuration that's been replaced

---

## Files to Remove

### 1. Debug Scripts (Root Directory)
These were created for troubleshooting specific issues and are no longer needed:

- `debug_audio_duration.py` - Audio duration debugging
- `debug_renderer_width.py` - Renderer width debugging  
- `debug_subtitle_rendering.py` - Subtitle rendering debugging
- `debug_subtitle_rendering2.py` - Second iteration of subtitle debugging
- `debug_timestamp_issue.py` - Timestamp bug debugging

**Reason:** These were temporary debugging tools. The bugs have been fixed and the app is working.

---

### 2. Bug Analysis Documents (Root Directory)
Documentation created during bug investigation:

- `BUG_ANALYSIS.md` - Timestamp reset bug analysis
- `SUBTITLE_BUG_ANALYSIS.md` - Subtitle rendering bug analysis

**Reason:** Bugs have been fixed. If you want to keep historical context, move to `docs/archive/` instead of deleting.

---

### 3. Deprecated Code

#### `tts_pipeline.py` (Root Directory)
- Contains `MoviePySubtitleExtractor` class
- Already marked as DEPRECATED with warnings
- Replaced by modular pipeline in `tts/`, `processing/`, and `pipeline/` packages
- Only used by deprecation tests

**Migration Path:** Users should use `api.library.generate_video_from_text()` or `api.library.generate_video_from_file()`

#### `api/legacy.py`
- Contains legacy `generate_video()` function
- Maintains backward compatibility for pre-existing audio/JSON files
- Still exported in `api/__init__.py`

**Decision Point:** 
- **Keep if:** You want to maintain backward compatibility for users with existing audio/JSON files
- **Remove if:** You want to force migration to the new text-based API
- **Recommendation:** Keep for now, mark as deprecated, remove in next major version

#### `config.py` (Root Directory)
- Legacy configuration with `get_config()` and `get_test_config()`
- Replaced by:
  - `tts/config.py` → `TTSConfig`
  - `config/video_config.py` → `VideoConfig`
  - `subtitle_config.py` → `SubtitleConfig`
- Still used by `main.py` for CLI compatibility

**Decision Point:**
- **Keep if:** You want to maintain CLI backward compatibility
- **Remove if:** You want to force migration to new config classes
- **Recommendation:** Keep for now, but refactor `main.py` to use new config classes directly

---

### 4. Tests for Deprecated Code

#### `tests/test_tts_pipeline_deprecation.py`
- Tests that `MoviePySubtitleExtractor` emits deprecation warnings
- Only relevant if keeping `tts_pipeline.py`

**Action:** Remove when `tts_pipeline.py` is removed

#### `tests/test_tts_pipeline.py`
- Tests the deprecated `MoviePySubtitleExtractor` functionality
- Superseded by tests for new modular components

**Action:** Remove when `tts_pipeline.py` is removed

#### `tests/test_api_backward_compatibility.py`
- Tests the legacy `api.legacy.generate_video()` function
- Only relevant if keeping backward compatibility

**Action:** Remove when `api/legacy.py` is removed

---

## Recommended Cleanup Phases

### Phase 1: Immediate Cleanup (Safe to Remove Now)
Remove debug scripts and bug analysis docs:

```bash
rm debug_audio_duration.py
rm debug_renderer_width.py
rm debug_subtitle_rendering.py
rm debug_subtitle_rendering2.py
rm debug_timestamp_issue.py
rm BUG_ANALYSIS.md
rm SUBTITLE_BUG_ANALYSIS.md
```

### Phase 2: Deprecation Cleanup (After Deprecation Period)
After giving users time to migrate (e.g., 1-2 releases):

```bash
# Remove deprecated TTS pipeline
rm tts_pipeline.py
rm tests/test_tts_pipeline.py
rm tests/test_tts_pipeline_deprecation.py

# Remove legacy API
rm api/legacy.py
rm tests/test_api_backward_compatibility.py

# Update api/__init__.py to remove legacy exports
```

### Phase 3: Configuration Modernization
Refactor `main.py` to use new config classes, then:

```bash
rm config.py
```

---

## Files to Keep (Important!)

### Keep These - They're Part of the New Architecture:

- `main.py` - CLI entry point (refactor to use new configs)
- `renderer.py` - Video rendering (uses new modular subtitle system)
- `subtitle_config.py` - Subtitle configuration dataclass
- `api/library.py` - New library API
- `api/__init__.py` - Public API exports
- All files in `tts/`, `config/`, `processing/`, `pipeline/`, `subtitle/`, `io_adapters/`
- All integration tests in `tests/integration/`
- All unit tests for new components

---

## Impact Analysis

### If You Remove Everything in Phase 1:
- ✅ No breaking changes
- ✅ Cleaner repository
- ✅ No impact on functionality

### If You Remove Everything in Phase 2:
- ⚠️ Breaking change for users still using:
  - `from tts_pipeline import MoviePySubtitleExtractor`
  - `from api.legacy import generate_video`
- ✅ Forces migration to better API
- ✅ Reduces maintenance burden

### If You Remove Everything in Phase 3:
- ⚠️ Breaking change for users importing `config.py` directly
- ⚠️ Requires updating `main.py`
- ✅ Completes migration to new architecture

---

## Recommendation

**Start with Phase 1 immediately** - Remove debug scripts and analysis docs. These have zero impact on users.

**For Phase 2 and 3:** Consider your versioning strategy:
- If this is a major version bump (e.g., 1.x → 2.0), remove deprecated code now
- If this is a minor version (e.g., 1.2 → 1.3), keep deprecated code with warnings for 1-2 more releases
- Add deprecation warnings to `config.py` if you plan to remove it

**Update Documentation:**
- Update `docs/structure.md` to reflect removed files
- Update `docs/how_it_works.md` to reference new APIs only
- Add migration guide to README if removing deprecated code
