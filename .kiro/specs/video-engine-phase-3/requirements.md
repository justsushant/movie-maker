# Requirements Document: Video Engine Phase 3

## Introduction

Phase 3 of the video engine adds audio analysis and synchronization capabilities to the system. This phase integrates librosa to analyze TTS audio and drive visual effects based on audio characteristics like beats, onsets, energy levels, and spectral features. The system enables audio-reactive video generation where visual elements respond dynamically to the narration audio.

The architecture maintains backward compatibility with Phases 1 and 2. Audio analysis is optional and fails gracefully when no audio is provided or librosa is unavailable. Effects remain pure functions, with audio analysis results passed as parameters rather than computed per-frame.

## Glossary

- **Audio Analysis**: The process of extracting temporal and spectral features from audio using librosa
- **Beat**: A rhythmic pulse in music, detected using librosa's beat tracking algorithm
- **Onset**: A sharp transient in audio marking the start of a sound event (e.g., percussive hit, word start)
- **Energy Envelope**: A time-series of audio loudness (RMS) values computed per frame
- **Spectral Centroid**: The "center of mass" of the audio spectrum, indicating brightness or tone
- **BeatSync**: An enum controlling how transitions align with musical beats (NONE, NEAREST_BEAT, BEAT_GRID)
- **Audio-Reactive Effect**: An effect whose parameters are driven by audio analysis results
- **Librosa**: A Python library for audio analysis and music information retrieval
- **RMS**: Root Mean Square, a measure of audio signal energy/loudness
- **Hop Length**: The number of audio samples between successive analysis frames in librosa
- **Frame Rate**: The number of analysis frames per second (audio frame rate, not video frame rate)
- **AudioAnalyzer**: A module that wraps librosa to extract beats, onsets, energy, and spectral features
- **AudioSync**: A module that maps audio features to video timeline and effect parameters
- **Graceful Degradation**: The system's ability to function without audio analysis when audio is unavailable

## Requirements

### Requirement 1: Audio Analysis Module

**User Story:** As a system developer, I want to analyze audio files using librosa, so that I can extract beats, onsets, and energy features.

#### Acceptance Criteria

1. THE System SHALL define an AudioAnalyzer class in engine/audio/analyzer.py
2. WHEN AudioAnalyzer is initialized with an audio file path, THE System SHALL load the audio using librosa
3. WHEN audio is loaded, THE System SHALL extract the sample rate and audio samples as a numpy array
4. WHEN analyze_beats is called, THE System SHALL use librosa.beat.beat_track to detect beat timestamps
5. WHEN analyze_onsets is called, THE System SHALL use librosa.onset.onset_detect to detect onset timestamps
6. WHEN analyze_energy is called, THE System SHALL use librosa.feature.rms to compute an energy envelope
7. WHEN analyze_spectral_centroid is called, THE System SHALL use librosa.feature.spectral_centroid to compute spectral brightness
8. THE System SHALL convert all librosa frame indices to timestamps in seconds
9. WHEN librosa is not installed, THE System SHALL raise an ImportError with a helpful message
10. WHEN an audio file cannot be loaded, THE System SHALL raise a ValueError with the file path

### Requirement 2: Beat Detection and Synchronization

**User Story:** As a video creator, I want transitions to snap to musical beats, so that visual changes align with audio rhythm.

#### Acceptance Criteria

1. THE System SHALL define a BeatSync enum with values NONE, NEAREST_BEAT, and BEAT_GRID
2. THE Transition dataclass SHALL include a sync attribute of type BeatSync with default NONE
3. WHEN a Scene has an audio attribute, THE ScenePlanner SHALL analyze beats from the audio file
4. WHEN a Transition has sync=NEAREST_BEAT, THE ScenePlanner SHALL adjust the transition start time to the nearest beat
5. WHEN a Transition has sync=BEAT_GRID, THE ScenePlanner SHALL adjust both transition start and end times to beat boundaries
6. WHEN a Transition has sync=NONE, THE ScenePlanner SHALL use the declared transition timing without adjustment
7. WHEN no audio is provided, THE System SHALL ignore all BeatSync settings and use declared timings
8. WHEN beat detection fails, THE System SHALL log a warning and fall back to declared timings
9. THE System SHALL ensure beat-snapped transitions do not create negative durations or overlaps

### Requirement 3: Onset Detection and Flash Effects

**User Story:** As a video creator, I want visual flashes triggered by sharp sounds, so that percussive elements create visual impact.

#### Acceptance Criteria

1. THE System SHALL define an OnsetFlash effect that brightens the frame briefly at onset times
2. WHEN OnsetFlash is initialized, THE System SHALL accept onset timestamps and flash duration parameters
3. WHEN rendering a frame at time t, THE OnsetFlash effect SHALL check if t is within flash_duration of any onset
4. WHEN an onset is active, THE OnsetFlash effect SHALL increase frame brightness proportional to time since onset
5. WHEN no onset is active, THE OnsetFlash effect SHALL return the frame unchanged
6. THE System SHALL use an easing function to control flash intensity decay
7. WHEN multiple onsets overlap, THE System SHALL use the maximum flash intensity

### Requirement 4: Onset-Driven Zoom Pulse

**User Story:** As a video creator, I want zoom effects triggered by sharp sounds, so that audio transients create visual motion.

#### Acceptance Criteria

1. THE System SHALL define an OnsetZoomPulse effect that briefly zooms the frame at onset times
2. WHEN OnsetZoomPulse is initialized, THE System SHALL accept onset timestamps, pulse duration, and zoom magnitude parameters
3. WHEN rendering a frame at time t, THE OnsetZoomPulse effect SHALL check if t is within pulse_duration of any onset
4. WHEN an onset is active, THE OnsetZoomPulse effect SHALL scale the frame proportional to time since onset
5. WHEN no onset is active, THE OnsetZoomPulse effect SHALL return the frame unchanged
6. THE System SHALL use an easing function to control zoom pulse timing
7. THE System SHALL apply zoom by scaling the frame and cropping to original dimensions

### Requirement 5: Energy-Driven Zoom

**User Story:** As a video creator, I want zoom level to breathe with audio loudness, so that visual scale responds to narration intensity.

#### Acceptance Criteria

1. THE System SHALL define an EnergyZoom effect that modulates zoom based on audio energy
2. WHEN EnergyZoom is initialized, THE System SHALL accept an energy envelope and zoom range parameters
3. WHEN rendering a frame at time t, THE EnergyZoom effect SHALL sample the energy envelope at time t
4. WHEN energy is sampled, THE System SHALL map energy to zoom scale using the specified range
5. THE System SHALL interpolate energy values between analysis frames for smooth zoom
6. THE System SHALL apply zoom by scaling the frame and cropping to original dimensions
7. WHEN energy envelope is empty or unavailable, THE System SHALL return the frame unchanged

### Requirement 6: Energy-Driven Brightness

**User Story:** As a video creator, I want frame brightness to scale with audio loudness, so that visual intensity matches audio intensity.

#### Acceptance Criteria

1. THE System SHALL define an EnergyBrightness effect that modulates brightness based on audio energy
2. WHEN EnergyBrightness is initialized, THE System SHALL accept an energy envelope and brightness range parameters
3. WHEN rendering a frame at time t, THE EnergyBrightness effect SHALL sample the energy envelope at time t
4. WHEN energy is sampled, THE System SHALL map energy to brightness multiplier using the specified range
5. THE System SHALL interpolate energy values between analysis frames for smooth brightness changes
6. THE System SHALL apply brightness by multiplying pixel values and clamping to [0, 255]
7. WHEN energy envelope is empty or unavailable, THE System SHALL return the frame unchanged

### Requirement 7: Energy-Driven Camera Shake

**User Story:** As a video creator, I want camera shake intensity to follow audio loudness, so that visual jitter responds to narration energy.

#### Acceptance Criteria

1. THE System SHALL define an EnergyShake effect that modulates shake amplitude based on audio energy
2. WHEN EnergyShake is initialized, THE System SHALL accept an energy envelope and shake range parameters
3. WHEN rendering a frame at time t, THE EnergyShake effect SHALL sample the energy envelope at time t
4. WHEN energy is sampled, THE System SHALL map energy to shake displacement using the specified range
5. THE System SHALL generate random shake offsets smoothed with scipy's savgol_filter
6. THE System SHALL apply shake by translating the frame using cv2.warpAffine
7. WHEN energy envelope is empty or unavailable, THE System SHALL return the frame unchanged

### Requirement 8: Spectral Color Shift

**User Story:** As a video creator, I want color temperature to track audio tone, so that bright sounds create warm colors and dark sounds create cool colors.

#### Acceptance Criteria

1. THE System SHALL define a SpectralColorShift effect that modulates color temperature based on spectral centroid
2. WHEN SpectralColorShift is initialized, THE System SHALL accept a spectral centroid array and temperature range parameters
3. WHEN rendering a frame at time t, THE SpectralColorShift effect SHALL sample the spectral centroid at time t
4. WHEN spectral centroid is sampled, THE System SHALL map centroid to color temperature shift
5. THE System SHALL interpolate spectral centroid values between analysis frames
6. THE System SHALL apply temperature shift by adjusting red and blue channels
7. WHEN spectral centroid is empty or unavailable, THE System SHALL return the frame unchanged

### Requirement 9: Audio Sync Module

**User Story:** As a system developer, I want a module to map audio features to video timeline, so that effects can query audio data at any video timestamp.

#### Acceptance Criteria

1. THE System SHALL define an AudioSync class in engine/audio/sync.py
2. WHEN AudioSync is initialized with AudioAnalyzer results, THE System SHALL store beats, onsets, energy, and spectral features
3. WHEN get_energy_at_time is called with time t, THE System SHALL interpolate the energy envelope at t
4. WHEN get_spectral_centroid_at_time is called with time t, THE System SHALL interpolate the spectral centroid at t
5. WHEN get_nearest_beat is called with time t, THE System SHALL return the timestamp of the nearest beat
6. WHEN is_onset_active is called with time t and duration, THE System SHALL return True if any onset is within duration of t
7. THE System SHALL handle edge cases where t is before the first or after the last analysis frame
8. WHEN no audio data is available, THE System SHALL return default values (zero energy, no onsets, no beats)

### Requirement 10: Scene DSL Integration

**User Story:** As a video creator, I want to specify audio files in my Scene, so that the system can analyze audio and enable audio-reactive effects.

#### Acceptance Criteria

1. THE Scene dataclass SHALL include an audio attribute of type str, Path, or None with default None
2. WHEN a Scene has an audio path, THE ScenePlanner SHALL create an AudioAnalyzer and analyze the audio
3. WHEN audio analysis succeeds, THE ScenePlanner SHALL create an AudioSync object and store it in the ResolvedTimeline
4. WHEN audio analysis fails, THE ScenePlanner SHALL log a warning and continue without audio features
5. WHEN a Scene has no audio attribute or audio is None, THE ScenePlanner SHALL skip audio analysis
6. THE ResolvedTimeline SHALL include an audio_sync attribute of type AudioSync or None

### Requirement 11: Effect Integration with Audio

**User Story:** As a system developer, I want effects to receive audio sync data, so that audio-reactive effects can query audio features.

#### Acceptance Criteria

1. THE FrameRenderer SHALL pass the AudioSync object to effects that require it
2. WHEN an effect is audio-reactive, THE System SHALL provide access to AudioSync through effect initialization
3. WHEN an effect is not audio-reactive, THE System SHALL not require AudioSync
4. THE System SHALL allow effects to query AudioSync at render time using the current timestamp
5. THE System SHALL ensure audio-reactive effects degrade gracefully when AudioSync is None

### Requirement 12: Graceful Degradation

**User Story:** As a video creator, I want the system to work without audio analysis, so that I can create videos even when audio is unavailable or librosa is not installed.

#### Acceptance Criteria

1. WHEN librosa is not installed, THE System SHALL log a warning and disable audio analysis
2. WHEN audio analysis is disabled, THE System SHALL render videos using declared timings and non-audio-reactive effects
3. WHEN an audio file cannot be loaded, THE System SHALL log an error and continue without audio features
4. WHEN audio-reactive effects are used without audio, THE System SHALL apply default behavior (no modulation)
5. WHEN BeatSync is used without audio, THE System SHALL use declared transition timings
6. THE System SHALL not crash or raise exceptions when audio features are unavailable
7. THE System SHALL document which effects require audio and how they behave without it

### Requirement 13: Performance Considerations

**User Story:** As a video creator, I want audio analysis to be fast, so that video generation remains efficient.

#### Acceptance Criteria

1. WHEN analyzing audio, THE System SHALL perform analysis once during planning, not per-frame
2. WHEN rendering frames, THE System SHALL query pre-computed audio features using interpolation
3. THE System SHALL use librosa's default hop_length for analysis to balance speed and accuracy
4. THE System SHALL cache AudioAnalyzer results to avoid re-analyzing the same audio file
5. THE System SHALL complete audio analysis in less than 10% of the audio duration for typical files
6. THE System SHALL document the performance impact of audio analysis on total render time

### Requirement 14: Error Handling

**User Story:** As a video creator, I want clear error messages when audio analysis fails, so that I can fix issues quickly.

#### Acceptance Criteria

1. WHEN librosa is not installed, THE System SHALL raise ImportError with installation instructions
2. WHEN an audio file does not exist, THE System SHALL raise FileNotFoundError with the file path
3. WHEN an audio file format is unsupported, THE System SHALL raise ValueError with the file format
4. WHEN beat detection fails, THE System SHALL log a warning and continue without beat sync
5. WHEN onset detection fails, THE System SHALL log a warning and continue without onset effects
6. WHEN energy analysis fails, THE System SHALL log a warning and continue without energy effects
7. THE System SHALL include the audio file path in all error messages

### Requirement 15: Testing Strategy

**User Story:** As a system developer, I want comprehensive tests for audio analysis, so that I can ensure correctness and catch regressions.

#### Acceptance Criteria

1. THE System SHALL include unit tests for AudioAnalyzer with sample audio files
2. THE System SHALL include unit tests for AudioSync interpolation and queries
3. THE System SHALL include property tests for audio-reactive effects with generated audio features
4. THE System SHALL include integration tests for Scene with audio analysis
5. THE System SHALL include tests for graceful degradation when librosa is unavailable
6. THE System SHALL include tests for error handling with invalid audio files
7. THE System SHALL include performance tests measuring audio analysis time
