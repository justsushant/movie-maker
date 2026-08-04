# Implementation Plan: Video Engine Phase 3

## Overview

This implementation plan breaks down Phase 3 (Audio Analysis and Sync) into discrete coding tasks. The approach follows a bottom-up strategy: build core audio analysis infrastructure first, then integrate with the planner, then implement audio-reactive effects, and finally wire everything together with comprehensive testing.

Phase 3 adds librosa-based audio analysis to drive visual effects. The implementation maintains backward compatibility—all audio features are optional and degrade gracefully when unavailable.

## Tasks

- [x] 1. Set up audio module structure and dependencies
  - Create `engine/audio/` directory with `__init__.py`
  - Add librosa to requirements.txt
  - Update engine/__init__.py to export audio classes
  - _Requirements: 1.1, 9.1_

- [x] 2. Implement AudioAnalyzer class
  - [x] 2.1 Create AudioAnalyzer with initialization and audio loading
    - Implement `__init__` with librosa import check
    - Load audio file using librosa.load
    - Store sample rate, samples, and duration
    - Handle ImportError for missing librosa
    - Handle FileNotFoundError for missing audio files
    - _Requirements: 1.2, 1.3, 1.9, 1.10_
  
  - [x] 2.2 Write property test for audio loading
    - **Property 1: Audio Loading Produces Valid Data**
    - **Validates: Requirements 1.2, 1.3**
  
  - [x] 2.3 Implement beat detection method
    - Implement `analyze_beats()` using librosa.beat.beat_track
    - Convert beat frames to timestamps in seconds
    - Cache results to avoid re-analysis
    - _Requirements: 1.4, 1.8_
  
  - [x] 2.4 Implement onset detection method
    - Implement `analyze_onsets()` using librosa.onset.onset_detect
    - Convert onset frames to timestamps in seconds
    - Cache results to avoid re-analysis
    - _Requirements: 1.5, 1.8_
  
  - [x] 2.5 Implement energy analysis method
    - Implement `analyze_energy()` using librosa.feature.rms
    - Return tuple of (timestamps, energy_values)
    - Convert frames to timestamps in seconds
    - Cache results to avoid re-analysis
    - _Requirements: 1.6, 1.8_
  
  - [x] 2.6 Implement spectral centroid analysis method
    - Implement `analyze_spectral_centroid()` using librosa.feature.spectral_centroid
    - Return tuple of (timestamps, centroid_values)
    - Convert frames to timestamps in seconds
    - Cache results to avoid re-analysis
    - _Requirements: 1.7, 1.8_
  
  - [x] 2.7 Implement analyze_all convenience method
    - Call all analysis methods and return dictionary
    - _Requirements: 1.4, 1.5, 1.6, 1.7_
  
  - [x] 2.8 Write property test for analysis methods
    - **Property 2: Analysis Methods Return Timestamp Arrays**
    - **Validates: Requirements 1.4, 1.5, 1.6, 1.7, 1.8**
  
  - [x]* 2.9 Write unit tests for AudioAnalyzer
    - Test loading various audio formats (WAV, MP3, OGG)
    - Test beat detection with synthetic audio
    - Test onset detection with synthetic audio
    - Test energy analysis shape and range
    - Test spectral centroid analysis shape and range
    - Test error handling for missing librosa
    - Test error handling for invalid audio files
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.9, 1.10_

- [x] 3. Implement AudioSync class
  - [x] 3.1 Create AudioSync with initialization
    - Implement `__init__` to store beats, onsets, energy, spectral data
    - Store all arrays as numpy arrays
    - _Requirements: 9.2_
  
  - [x]* 3.2 Write property test for AudioSync storage
    - **Property 20: AudioSync Stores All Analysis Results**
    - **Validates: Requirements 9.2**
  
  - [x] 3.3 Implement energy interpolation method
    - Implement `get_energy_at_time(t)` with linear interpolation
    - Handle edge cases (before first frame, after last frame)
    - Return 0.0 for empty data
    - _Requirements: 9.3, 9.7, 9.8_
  
  - [x] 3.4 Implement spectral centroid interpolation method
    - Implement `get_spectral_centroid_at_time(t)` with linear interpolation
    - Handle edge cases (before first frame, after last frame)
    - Return 0.0 for empty data
    - _Requirements: 9.4, 9.7, 9.8_
  
  - [x]* 3.5 Write property test for interpolation
    - **Property 21: AudioSync Interpolates Time-Series Data**
    - **Validates: Requirements 9.3, 9.4**
  
  - [x] 3.6 Implement nearest beat query method
    - Implement `get_nearest_beat(t)` using numpy argmin
    - Return None for empty beat array
    - _Requirements: 9.5, 9.8_
  
  - [x]* 3.7 Write property test for nearest beat
    - **Property 22: AudioSync Finds Nearest Beat**
    - **Validates: Requirements 9.5**
  
  - [x] 3.8 Implement onset window detection method
    - Implement `is_onset_active(t, duration)` using numpy boolean indexing
    - Return False for empty onset array
    - _Requirements: 9.6, 9.8_
  
  - [x] 3.9 Implement closest onset query method
    - Implement `get_closest_onset(t, max_distance)` helper method
    - Return None if no onset within max_distance
    - _Requirements: 9.6_
  
  - [x]* 3.10 Write property test for onset detection
    - **Property 23: AudioSync Detects Onset Windows**
    - **Validates: Requirements 9.6**
  
  - [x]* 3.11 Write unit tests for AudioSync
    - Test initialization stores all data correctly
    - Test get_energy_at_time interpolation with known values
    - Test get_spectral_centroid_at_time interpolation with known values
    - Test get_nearest_beat with known beat array
    - Test is_onset_active with known onset array
    - Test edge cases (before first frame, after last frame)
    - Test empty data returns default values
    - _Requirements: 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_

- [x] 4. Update Scene DSL for audio support
  - [x] 4.1 Add BeatSync enum to engine/scene.py
    - Define BeatSync enum with NONE, NEAREST_BEAT, BEAT_GRID values
    - _Requirements: 2.1_
  
  - [x] 4.2 Update Transition dataclass
    - Add sync attribute of type BeatSync with default NONE
    - _Requirements: 2.2_
  
  - [x] 4.3 Update Scene dataclass
    - Add audio attribute of type Optional[Union[str, Path]] with default None
    - _Requirements: 10.1_

- [x] 5. Integrate audio analysis into ScenePlanner
  - [x] 5.1 Implement _analyze_audio method in ScenePlanner
    - Check if scene.audio is None, return None if so
    - Try to import AudioAnalyzer and AudioSync
    - Catch ImportError and log warning if librosa unavailable
    - Create AudioAnalyzer with scene.audio path
    - Call analyze_all() to get all features
    - Create AudioSync object from results
    - Catch exceptions and log errors, return None on failure
    - _Requirements: 10.2, 10.3, 10.4, 10.5, 12.1, 12.2, 12.3, 14.1, 14.2, 14.3_
  
  - [x]* 5.2 Write property test for scene with audio
    - **Property 24: Scene with Audio Triggers Analysis**
    - **Validates: Requirements 10.2, 10.3**
  
  - [x]* 5.3 Write property test for scene without audio
    - **Property 25: Scene without Audio Skips Analysis**
    - **Validates: Requirements 10.5**
  
  - [x] 5.4 Update ResolvedTimeline dataclass
    - Add audio_sync attribute of type Optional[AudioSync] with default None
    - _Requirements: 10.6_
  
  - [x] 5.5 Update ScenePlanner.plan() to call _analyze_audio
    - Call _analyze_audio early in planning process
    - Store result in ResolvedTimeline
    - _Requirements: 10.2, 10.3_

- [x] 6. Implement beat synchronization in ScenePlanner
  - [x] 6.1 Implement _apply_beat_sync method
    - Check if audio_sync is None or beats array is empty, return unchanged if so
    - Iterate through transitions and clip timings
    - For each transition with sync=NEAREST_BEAT:
      - Find nearest beat to transition start time using audio_sync.get_nearest_beat
      - Compute adjusted start time
      - Validate adjusted start doesn't create negative clip duration
      - If valid, update transition start time; else log warning and keep original
    - For each transition with sync=BEAT_GRID:
      - Find nearest beat to transition start time
      - Find nearest beat to transition end time (start + duration)
      - Validate both adjustments preserve positive duration
      - If valid, update both boundaries; else log warning and keep original
    - For transitions with sync=NONE, leave timing unchanged
    - Recompute clip start times based on adjusted transition timings
    - Validate no clip durations become negative
    - Validate no invalid overlaps created
    - Log warnings and fall back to declared timing if validation fails
    - _Requirements: 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 14.4, 14.5_
  
  - [x]* 6.2 Write property test for beat sync NONE
    - **Property 3: Beat Sync NONE Preserves Timing**
    - **Validates: Requirements 2.6**
  
  - [x]* 6.3 Write property test for beat sync NEAREST_BEAT
    - **Property 4: Beat Sync NEAREST_BEAT Snaps to Beats**
    - **Validates: Requirements 2.4**
  
  - [x]* 6.4 Write property test for beat sync BEAT_GRID
    - **Property 5: Beat Sync BEAT_GRID Snaps Both Boundaries**
    - **Validates: Requirements 2.5**
  
  - [x]* 6.5 Write property test for beat sync without audio
    - **Property 6: Beat Sync Without Audio Falls Back**
    - **Validates: Requirements 2.7**
  
  - [x]* 6.6 Write property test for beat snapping preserves durations
    - **Property 7: Beat Snapping Preserves Valid Durations**
    - **Validates: Requirements 2.9**
  
  - [x]* 6.7 Write unit tests for beat synchronization
    - Test NONE mode preserves declared timings
    - Test NEAREST_BEAT snaps to closest beat
    - Test BEAT_GRID snaps both boundaries
    - Test beat sync without audio uses declared timings
    - Test beat sync preserves positive durations
    - Test beat sync avoids negative clip durations
    - Test error handling for invalid beat snapping
    - _Requirements: 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9_
  
  - [x] 6.8 Integrate _apply_beat_sync into ScenePlanner.plan()
    - Call _apply_beat_sync after computing initial clip timings
    - Use adjusted timings for final timeline
    - _Requirements: 2.3, 2.4, 2.5_

- [x] 7. Create test audio fixtures
  - [x] 7.1 Create tests/fixtures/audio/ directory
    - Create synthetic_beat_120bpm.wav (10s, clear 120 BPM beat pattern)
    - Create synthetic_onsets.wav (5s, sharp transients at 0.5s intervals)
    - Create synthetic_speech.wav (5s, simulated speech with varying energy)
    - Create silent.wav (1s, silence for edge case testing)
    - _Requirements: 15.1_
  
  - [x] 7.2 Document test audio generation
    - Add script or instructions for regenerating test audio
    - Document expected beat/onset timestamps for validation
    - _Requirements: 15.1_

- [x] 8. Checkpoint - Ensure audio analysis and beat sync work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement OnsetFlash effect
  - [x] 9.1 Create OnsetFlash effect class in engine/effects.py
    - Implement __init__ to accept audio_sync, flash_duration, intensity, easing
    - Store parameters as instance attributes
    - Implement apply(frame, t, progress) method
    - Check if audio_sync is None, return frame unchanged if so
    - Check if any onset is within flash_duration of t using audio_sync.is_onset_active
    - If no onset active, return frame unchanged
    - If onset active, find closest onset using audio_sync.get_closest_onset
    - Compute time since onset: delta = t - onset_time
    - Compute flash progress: flash_progress = delta / flash_duration
    - Apply easing to flash_progress
    - Compute brightness multiplier: 1.0 + intensity * (1.0 - eased_progress)
    - Multiply frame by brightness multiplier and clamp to [0, 255]
    - For multiple overlapping onsets, compute brightness for each and use maximum
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 11.2, 11.5_
  
  - [x]* 9.2 Write property test for OnsetFlash window detection
    - **Property 8: OnsetFlash Only Modifies During Onset Windows**
    - **Validates: Requirements 3.3, 3.5**
  
  - [x]* 9.3 Write property test for OnsetFlash brightness increase
    - **Property 9: OnsetFlash Brightness Increases During Onset**
    - **Validates: Requirements 3.4**
  
  - [x]* 9.4 Write property test for OnsetFlash easing
    - **Property 10: OnsetFlash Uses Easing for Decay**
    - **Validates: Requirements 3.6**
  
  - [x]* 9.5 Write property test for OnsetFlash overlapping onsets
    - **Property 11: OnsetFlash Maximum for Overlapping Onsets**
    - **Validates: Requirements 3.7**
  
  - [x]* 9.6 Write unit tests for OnsetFlash
    - Test brightens during onset window
    - Test unchanged outside onset window
    - Test uses easing curve
    - Test maximum for overlapping onsets
    - Test degrades gracefully without audio
    - _Requirements: 3.3, 3.4, 3.5, 3.6, 3.7, 11.5, 12.4_

- [x] 10. Implement OnsetZoomPulse effect
  - [x] 10.1 Create OnsetZoomPulse effect class in engine/effects.py
    - Implement __init__ to accept audio_sync, pulse_duration, zoom_magnitude, easing
    - Implement apply(frame, t, progress) method
    - Check if any onset is within pulse_duration of t
    - If no onset active, return frame unchanged
    - If onset active, compute time since onset and apply easing
    - Scale frame proportional to eased progress
    - Crop to original dimensions after scaling
    - For multiple overlapping onsets, use maximum zoom
    - Handle None audio_sync gracefully (return frame unchanged)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 11.2, 11.5_
  
  - [x]* 10.2 Write property test for OnsetZoomPulse window detection
    - **Property 12: OnsetZoomPulse Only Modifies During Onset Windows**
    - **Validates: Requirements 4.3, 4.5**
  
  - [x]* 10.3 Write property test for OnsetZoomPulse scaling
    - **Property 13: OnsetZoomPulse Scales Frame During Onset**
    - **Validates: Requirements 4.4**
  
  - [x]* 10.4 Write property test for OnsetZoomPulse easing
    - **Property 14: OnsetZoomPulse Uses Easing for Timing**
    - **Validates: Requirements 4.6**
  
  - [x]* 10.5 Write unit tests for OnsetZoomPulse
    - Test scales during onset window
    - Test unchanged outside onset window
    - Test uses easing curve
    - Test degrades gracefully without audio
    - _Requirements: 4.3, 4.4, 4.5, 4.6, 11.5, 12.4_

- [x] 11. Implement EnergyZoom effect
  - [x] 11.1 Create EnergyZoom effect class in engine/effects.py
    - Implement __init__ to accept audio_sync, zoom_range, energy_range
    - Implement apply(frame, t, progress) method
    - Query audio_sync.get_energy_at_time(t)
    - Map energy to zoom scale using zoom_range and energy_range
    - Clamp zoom scale to zoom_range bounds
    - Scale frame and crop to original dimensions
    - Handle None audio_sync or empty energy gracefully (return frame unchanged)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 11.2, 11.4, 11.5_
  
  - [x]* 11.2 Write property test for EnergyZoom mapping
    - **Property 15: EnergyZoom Maps Energy to Zoom Range**
    - **Validates: Requirements 5.3, 5.4, 5.5**
  
  - [x]* 11.3 Write unit tests for EnergyZoom
    - Test maps energy to zoom range
    - Test interpolates energy values
    - Test degrades gracefully without audio
    - _Requirements: 5.3, 5.4, 5.5, 5.7, 11.4, 11.5, 12.4_

- [x] 12. Implement EnergyBrightness effect
  - [x] 12.1 Create EnergyBrightness effect class in engine/effects.py
    - Implement __init__ to accept audio_sync, brightness_range, energy_range
    - Implement apply(frame, t, progress) method
    - Query audio_sync.get_energy_at_time(t)
    - Map energy to brightness multiplier using brightness_range and energy_range
    - Clamp brightness multiplier to brightness_range bounds
    - Multiply pixel values and clamp to [0, 255]
    - Handle None audio_sync or empty energy gracefully (return frame unchanged)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 11.2, 11.4, 11.5_
  
  - [x]* 12.2 Write property test for EnergyBrightness mapping
    - **Property 16: EnergyBrightness Maps Energy to Brightness Range**
    - **Validates: Requirements 6.3, 6.4, 6.5**
  
  - [x]* 12.3 Write unit tests for EnergyBrightness
    - Test maps energy to brightness range
    - Test interpolates energy values
    - Test clamps pixel values to [0, 255]
    - Test degrades gracefully without audio
    - _Requirements: 6.3, 6.4, 6.5, 6.6, 6.7, 11.4, 11.5, 12.4_

- [x] 13. Implement EnergyShake effect
  - [x] 13.1 Create EnergyShake effect class in engine/effects.py
    - Implement __init__ to accept audio_sync, shake_range, energy_range
    - Implement apply(frame, t, progress) method
    - Query audio_sync.get_energy_at_time(t)
    - Map energy to shake displacement using shake_range and energy_range
    - Generate random shake offsets smoothed with scipy.signal.savgol_filter
    - Apply shake by translating frame using cv2.warpAffine
    - Handle None audio_sync or empty energy gracefully (return frame unchanged)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 11.2, 11.4, 11.5_
  
  - [x]* 13.2 Write property test for EnergyShake mapping
    - **Property 17: EnergyShake Maps Energy to Shake Range**
    - **Validates: Requirements 7.3, 7.4**
  
  - [x]* 13.3 Write unit tests for EnergyShake
    - Test maps energy to shake range
    - Test generates smoothed shake offsets
    - Test degrades gracefully without audio
    - _Requirements: 7.3, 7.4, 7.5, 7.7, 11.4, 11.5, 12.4_

- [x] 14. Implement SpectralColorShift effect
  - [x] 14.1 Create SpectralColorShift effect class in engine/effects.py
    - Implement __init__ to accept audio_sync, temperature_range, centroid_range
    - Implement apply(frame, t, progress) method
    - Query audio_sync.get_spectral_centroid_at_time(t)
    - Map spectral centroid to color temperature shift using ranges
    - Apply temperature shift by adjusting red and blue channels
    - Handle None audio_sync or empty spectral data gracefully (return frame unchanged)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 11.2, 11.4, 11.5_
  
  - [x]* 14.2 Write property test for SpectralColorShift mapping
    - **Property 18: SpectralColorShift Maps Centroid to Temperature**
    - **Validates: Requirements 8.3, 8.4, 8.5**
  
  - [x]* 14.3 Write unit tests for SpectralColorShift
    - Test maps spectral centroid to temperature range
    - Test interpolates spectral centroid values
    - Test adjusts red and blue channels
    - Test degrades gracefully without audio
    - _Requirements: 8.3, 8.4, 8.5, 8.6, 8.7, 11.4, 11.5, 12.4_

- [x] 15. Write comprehensive graceful degradation property test
  - [x]* 15.1 Write property test for audio-reactive effects graceful degradation
    - **Property 19: Audio-Reactive Effects Degrade Gracefully**
    - **Validates: Requirements 5.7, 6.7, 7.7, 8.7**

- [x] 16. Write property test for effects querying AudioSync
  - [x]* 16.1 Write property test for effects querying AudioSync at render time
    - **Property 26: Effects Query AudioSync at Render Time**
    - **Validates: Requirements 11.4**

- [x] 17. Checkpoint - Ensure all audio-reactive effects work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 18. Integration and end-to-end testing
  - [x]* 18.1 Write integration test for end-to-end with audio
    - Create scene with audio file, clips, transitions with BeatSync
    - Add audio-reactive effects to clips
    - Plan and render complete video
    - Verify video renders without errors
    - Verify transitions align with beats
    - Verify effects respond to audio
    - _Requirements: 10.2, 10.3, 2.3, 2.4, 2.5, 11.4_
  
  - [x]* 18.2 Write integration test for graceful degradation
    - Create scene with audio but mock librosa as unavailable
    - Verify system logs warning and continues
    - Verify video renders with declared timings and no audio effects
    - _Requirements: 12.1, 12.2, 12.4, 12.5_
  
  - [x]* 18.3 Write integration test for error recovery
    - Create scene with invalid audio path
    - Verify system logs error and continues
    - Verify video renders without audio features
    - _Requirements: 12.3, 14.2, 14.3_

- [x] 19. Performance testing and optimization
  - [x] 19.1 Establish baseline performance
    - Measure time to render 100 frames without audio effects
    - Record baseline for comparison
    - _Requirements: 13.2, 13.5_
  
  - [x]* 19.2 Write performance test for audio analysis time
    - Measure time to analyze 10-second audio file
    - Verify analysis completes in < 1 second
    - _Requirements: 13.1, 13.5_
  
  - [x]* 19.3 Write performance test for render time with audio effects
    - Measure time to render 100 frames with audio-reactive effects
    - Compare to baseline (from task 19.1)
    - Verify overhead is < 20%
    - _Requirements: 13.2, 13.5_
  
  - [x]* 19.4 Write performance test for memory usage
    - Monitor memory during audio analysis
    - Verify peak memory < 100MB for typical audio files
    - Verify AudioSync object size is reasonable
    - _Requirements: 13.4_

- [x] 20. Documentation and examples
  - [x] 20.1 Update docs/video_engine.md with Phase 3 features
    - Document audio analysis capabilities
    - Document BeatSync enum and usage
    - Document audio-reactive effects with examples
    - Document graceful degradation behavior
    - _Requirements: 12.7_
  
  - [x] 20.2 Create example script demonstrating audio-reactive features
    - Create example with audio file, beat-synced transitions, and audio-reactive effects
    - Add to examples/ directory
    - _Requirements: 10.1, 2.1, 2.2, 3.1, 4.1, 5.1, 6.1, 7.1, 8.1_
  
  - [x] 20.3 Update README.md with Phase 3 completion status
    - Mark Phase 3 as complete in project status
    - Update feature list with audio-reactive capabilities

- [x] 21. Final checkpoint - Ensure all tests pass and documentation is complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end flows
- Performance tests ensure audio analysis and effects remain efficient
- The implementation follows a bottom-up approach: core infrastructure → integration → effects → testing
- All audio features are optional and degrade gracefully when unavailable
- Backward compatibility is maintained throughout—existing Phase 1 and Phase 2 code works unchanged

### Audio-Reactive Effect Pattern

Audio-reactive effects follow a class-based pattern (different from Phase 2's factory functions):

```python
class EnergyZoom:
    def __init__(self, audio_sync: Optional[AudioSync], zoom_range: tuple[float, float], energy_range: tuple[float, float]):
        self.audio_sync = audio_sync
        self.zoom_range = zoom_range
        self.energy_range = energy_range
    
    def apply(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        if self.audio_sync is None:
            return frame  # Graceful degradation
        
        energy = self.audio_sync.get_energy_at_time(t)
        # Map energy to zoom scale and apply transform
        ...
```

This pattern allows effects to:
- Store AudioSync reference at initialization
- Query audio features at render time
- Degrade gracefully when AudioSync is None
- Remain testable with mock AudioSync objects

### Property Test Generation Guidance

For property tests involving audio data:

**Audio Analysis Results** (beats, onsets, energy, spectral):
- Use `hypothesis.strategies.lists()` with `floats(min_value=0.0, max_value=10.0)` for timestamps
- Ensure timestamps are sorted: use `.map(sorted)` or `assume(all(a < b for a, b in zip(arr[:-1], arr[1:])))`
- For energy/spectral values: use `floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)`

**Synthetic Audio Files**:
- Generate numpy arrays with `np.sin()` for tone generation
- Use `scipy.io.wavfile.write()` to create temporary WAV files
- Clean up temporary files in test teardown

**AudioSync Objects**:
- Create with known data for deterministic testing
- Use empty arrays for testing graceful degradation

**Frames**:
- Use `hypothesis.strategies.integers()` for dimensions (e.g., 100-1920 for width)
- Generate frames with `np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)`
- Or use `hypothesis.extra.numpy.arrays()` for more control
