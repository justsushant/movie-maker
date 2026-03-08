# Delta Spec: Beat Synchronization

## Overview

This delta specification modifies the existing video-engine-phase-3 capability to make beat synchronization functional. Currently, the BeatSync enum and Transition.sync attribute exist but are never executed during scene planning.

## Original Spec

The original Phase 3 specification is at `.kiro/specs/video-engine-phase-3/requirements.md`.

## MODIFIED Requirements

### Requirement: Scene Planning with Beat Synchronization

**Original Requirement 10**: Scene DSL Integration

The System SHALL define an audio attribute of type str, Path, or None with default None. When a Scene has an audio path, THE ScenePlanner SHALL analyze the audio file using AudioAnalyzer and create an AudioSync object.

**MODIFIED**:

The System SHALL integrate audio analysis into the scene planning pipeline:

1. When Scene has an audio attribute:
   - ScenePlanner.plan() SHALL call _analyze_audio() to process the audio file
   - _analyze_audio() SHALL:
     - Import AudioAnalyzer and AudioSync (catch ImportError for graceful degradation)
     - Load and analyze the audio file
     - Extract beats, onsets, energy envelope, and spectral centroid
     - Create AudioSync object with analysis results
     - Return AudioSync to planner
     - Log warnings and return None on any errors

2. ScenePlanner.plan() SHALL store the AudioSync object in the ResolvedTimeline audio_sync attribute

3. ScenePlanner.plan() SHALL call _apply_beat_sync() after computing initial clip timings

4. _apply_beat_sync() SHALL adjust transition timings based on BeatSync mode:
   - For transitions with sync=BeatSync.NONE: Preserve declared timings (no-op)
   - For transitions with sync=BeatSync.NEAREST_BEAT: Adjust transition start time to nearest beat
   - For transitions with sync=BeatSync.BEAT_GRID: Adjust both transition start and end times to beat boundaries
   - Validate that adjusted timings don't create negative clip durations or invalid overlaps
   - Log warnings and fall back to declared timing if validation fails

5. ResolvedTimeline SHALL include audio_sync: Optional[AudioSync] attribute

#### Scenario: Successful beat sync with music

- **WHEN** a Scene has audio file with clear beats and transitions use BeatSync.BEAT_GRID
- **THEN** ScenePlanner aligns all transition boundaries to detected beat timestamps, creating rhythm-locked visual changes

#### Scenario: Beat sync with no audio

- **WHEN** a Scene has no audio attribute (audio=None)
- **THEN** ScenePlanner skips audio analysis, audio_sync in ResolvedTimeline is None, transitions use declared timing

#### Scenario: Beat sync with librosa unavailable

- **WHEN** librosa is not installed
- **THEN** _analyze_audio() catches ImportError, logs warning, returns None, audio_sync in ResolvedTimeline is None, transitions use declared timing

#### Scenario: Beat sync creates invalid timing

- **WHEN** beat-snapped transition would create negative clip duration or invalid overlap
- **THEN** _apply_beat_sync() logs a warning, preserves original declared timing for that transition

#### Scenario: Multiple beat-synced transitions

- **WHEN** a Scene has multiple transitions with BeatSync modes
- **THEN** _apply_beat_sync() processes all transitions sequentially, adjusting each to nearest beats while respecting clip duration constraints

### Requirement: FrameRenderer Integration

**Original Requirement 11**: Effect Integration with Audio

The FrameRenderer SHALL pass the AudioSync object to effects that require it.

**MODIFIED**:

The FrameRenderer SHALL pass AudioSync to audio-reactive effects (from Phase 3: OnsetFlash, OnsetZoomPulse, EnergyZoom, EnergyBrightness, EnergyShake, SpectralColorShift):

1. The FrameRenderer._apply_effects() method SHALL:
   - Check if audio_sync is available in timeline
   - Pass audio_sync to audio-reactive effects during effect creation (if applicable)
   - Ensure audio-reactive effects gracefully handle None audio_sync

2. All audio-reactive effects SHALL:
   - Accept Optional[AudioSync] in __init__
   - Return frame unchanged if audio_sync is None
   - Query AudioSync for audio features at render time (t)
   - Apply effect modulation based on audio features

#### Scenario: Audio-reactive effect with valid AudioSync

- **WHEN** an audio-reactive effect is applied with a valid AudioSync object
- **THEN** the effect queries AudioSync at render time t and applies appropriate modulation (flash, zoom, brightness, shake, color shift)

#### Scenario: Audio-reactive effect without AudioSync

- **WHEN** an audio-reactive effect is applied with AudioSync=None
- **THEN** the effect returns the input frame unchanged (graceful degradation)

## ADDED Requirements

### Requirement: Audio Analysis Integration Methods

The System SHALL implement ScenePlanner methods for audio analysis integration:

1. **ScenePlanner._analyze_audio()** SHALL:
   - Accept Scene as parameter
   - Return Optional[AudioSync]
   - Check if scene.audio is None and return None immediately
   - Try to import AudioAnalyzer and AudioSync
   - Catch ImportError and log warning if librosa unavailable
   - Create AudioAnalyzer instance with scene.audio
   - Call analyzer.analyze_all() to extract all features
   - Create AudioSync object with analysis results
   - Catch file errors (FileNotFoundError, ValueError) and log appropriately
   - Return None on any error

2. **ScenePlanner._apply_beat_sync()** SHALL:
   - Accept list of Transition objects and ResolvedTimeline with audio_sync
   - Accept list of clip timing tuples (start_time, end_time)
   - Return adjusted clip timings
   - Handle BeatSync.NONE mode (no changes)
   - For NEAREST_BEAT mode:
     - Use audio_sync.get_nearest_beat() to find closest beat
     - Adjust transition start time to beat timestamp
     - Validate clip duration remains positive after adjustment
     - Fall back to original timing if adjustment invalid
   - For BEAT_GRID mode:
     - Use audio_sync.get_nearest_beat() to find beats for start and end
     - Adjust both transition boundaries to beat timestamps
     - Validate clip duration remains positive and no invalid overlaps
     - Fall back to original timing if adjustments invalid
   - Log warnings for any validation failures

3. **ResolvedTimeline Update** SHALL:
   - Add audio_sync: Optional[AudioSync] attribute
   - Default to None for backward compatibility

#### Scenario: Beat sync with NEAREST_BEAT

- **WHEN** transition has sync=BeatSync.NEAREST_BEAT and audio has detected beats
- **THEN** transition start time moves to nearest beat, end time stays at start+duration, all clips maintain positive duration

#### Scenario: Beat sync with BEAT_GRID

- **WHEN** transition has sync=BeatSync.BEAT_GRID and audio has sufficient beat density
- **THEN** both transition start and end times align with beat boundaries, creating rhythm-locked transitions

## REMOVED Requirements

None - No requirements are removed, only enhanced with new functionality.

## RENAMED Requirements

None - No requirement names are changed.
