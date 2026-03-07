"""Scene planner: resolves Scene DSL into concrete timeline with timings."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from engine.audio.sync import AudioSync

from engine.camera import Rect, compute_motion_path
from engine.image_loader import ImageLoader
from engine.scene import Scene


@dataclass
class ResolvedClip:
    """A clip with computed timing and camera path."""
    
    source: Path
    start_time: float
    end_time: float
    camera_path: Callable[[float], Rect]  # maps absolute time -> viewport
    effects: list = field(default_factory=list)  # List of effect functions


@dataclass
class TransitionRegion:
    """Defines a transition between two clips."""
    
    start_time: float
    end_time: float
    clip_a_index: int
    clip_b_index: int
    transition_function: Callable
    easing_function: Callable


@dataclass
class ResolvedTimeline:
    """Fully resolved timeline ready for rendering."""

    clips: list[ResolvedClip]
    resolution: tuple[int, int]
    fps: int
    duration: float
    transitions: list[TransitionRegion] = field(default_factory=list)
    audio_sync: 'Optional[AudioSync]' = None  # Phase 3: audio analysis results




class ScenePlanner:
    """Converts Scene DSL into a concrete timeline."""
    
    def plan(self, scene: Scene, image_loader: ImageLoader) -> ResolvedTimeline:
        """
        Resolve clip timings, compute camera paths, and plan transitions.
        
        Args:
            scene: Scene description
            image_loader: For loading images to get dimensions
            
        Returns:
            ResolvedTimeline ready for rendering
            
        Raises:
            ValueError: If transition durations are invalid
        """
        from engine.transitions import get_transition_function
        
        # Analyze audio if provided (Phase 3)
        audio_sync = self._analyze_audio(scene)
        
        # Validate transitions
        self._validate_transitions(scene)
        
        resolved_clips = []
        transition_regions = []
        current_time = 0.0
        
        for i, clip in enumerate(scene.clips):
            # Load image to get dimensions
            image = image_loader.load(clip.source)
            image_size = (image.shape[1], image.shape[0])  # (width, height)
            
            # Compute camera path
            camera_path_fn = compute_motion_path(
                clip.motion,
                image_size,
                scene.resolution,
                clip.duration
            )
            
            # Determine clip timing
            if i > 0 and i - 1 < len(scene.transitions):
                # This clip overlaps with previous due to transition
                # current_time has already been adjusted for the overlap
                start_time = current_time
            else:
                start_time = current_time
            
            end_time = start_time + clip.duration
            
            # Create resolved clip with absolute timing
            start = start_time
            resolved = ResolvedClip(
                source=Path(clip.source),
                start_time=start,
                end_time=end_time,
                camera_path=lambda t, fn=camera_path_fn, s=start: fn(t - s),
                effects=clip.effects.copy() if hasattr(clip, 'effects') else []
            )
            resolved_clips.append(resolved)
            
            # Create transition region if applicable
            if i > 0 and i - 1 < len(scene.transitions):
                transition = scene.transitions[i - 1]
                transition_fn = get_transition_function(transition.type)
                
                transition_region = TransitionRegion(
                    start_time=start_time,
                    end_time=start_time + transition.duration,
                    clip_a_index=i - 1,
                    clip_b_index=i,
                    transition_function=transition_fn,
                    easing_function=transition.easing
                )
                transition_regions.append(transition_region)
            
            # Advance time (accounting for overlap)
            if i < len(scene.clips) - 1 and i < len(scene.transitions):
                transition = scene.transitions[i]
                current_time = end_time - transition.duration
            else:
                current_time = end_time
        
        # Apply beat synchronization if audio is available (Phase 3)
        resolved_clips, transition_regions = self._apply_beat_sync(
            scene, resolved_clips, transition_regions, audio_sync
        )
        
        total_duration = resolved_clips[-1].end_time if resolved_clips else 0.0
        
        return ResolvedTimeline(
            clips=resolved_clips,
            transitions=transition_regions,
            resolution=scene.resolution,
            fps=scene.fps,
            duration=total_duration,
            audio_sync=audio_sync
        )
    
    def _validate_transitions(self, scene: Scene) -> None:
        """
        Validate transition configuration.
        
        Raises:
            ValueError: If transitions are invalid
        """
        # Check if scene has transitions attribute (backward compatibility)
        if not hasattr(scene, 'transitions'):
            return
        
        # Only validate if there are clips
        if len(scene.clips) > 0 and len(scene.transitions) > len(scene.clips) - 1:
            raise ValueError(
                f"Scene has {len(scene.clips)} clips but {len(scene.transitions)} transitions. "
                f"Maximum transitions is {len(scene.clips) - 1}."
            )
        
        for i, transition in enumerate(scene.transitions):
            if transition.duration <= 0:
                raise ValueError(
                    f"Transition {i} has invalid duration: {transition.duration}. "
                    f"Duration must be positive."
                )
            
            # Check that transition doesn't exceed clip durations
            if i < len(scene.clips) - 1:
                clip_a_duration = scene.clips[i].duration
                clip_b_duration = scene.clips[i + 1].duration
                min_duration = min(clip_a_duration, clip_b_duration)
                
                if transition.duration > min_duration:
                    raise ValueError(
                        f"Transition {i} duration ({transition.duration}s) exceeds "
                        f"the shorter clip duration ({min_duration}s). "
                        f"Transition between clips {i} and {i+1}."
                    )

    def _analyze_audio(self, scene: Scene):
        """
        Analyze audio file if provided in scene.

        Args:
            scene: Scene with optional audio attribute

        Returns:
            AudioSync object if analysis succeeds, None otherwise
        """
        # Check if audio is provided
        if scene.audio is None:
            return None

        # Try to import audio analysis modules
        try:
            from engine.audio.analyzer import AudioAnalyzer
            from engine.audio.sync import AudioSync
        except ImportError as e:
            import logging
            logging.warning(
                f"Audio analysis unavailable: {e}. "
                "Install librosa for audio-reactive features: pip install librosa"
            )
            return None

        # Try to analyze audio
        try:
            analyzer = AudioAnalyzer(scene.audio)
            results = analyzer.analyze_all()

            # Extract results
            beats = results['beats']
            onsets = results['onsets']
            energy_times, energy_values = results['energy']
            spectral_times, spectral_values = results['spectral_centroid']

            # Create AudioSync object
            audio_sync = AudioSync(
                beats=beats,
                onsets=onsets,
                energy_times=energy_times,
                energy_values=energy_values,
                spectral_times=spectral_times,
                spectral_values=spectral_values
            )

            return audio_sync

        except FileNotFoundError as e:
            import logging
            logging.error(f"Audio file not found: {e}")
            return None
        except Exception as e:
            import logging
            logging.error(f"Audio analysis failed: {e}")
            return None

    def _apply_beat_sync(
        self,
        scene: Scene,
        resolved_clips: list[ResolvedClip],
        transition_regions: list[TransitionRegion],
        audio_sync
    ) -> tuple[list[ResolvedClip], list[TransitionRegion]]:
        """
        Apply beat synchronization to transition timings.

        Adjusts transition start/end times to align with audio beats based on
        the sync mode specified in each transition. Validates that adjustments
        don't create negative clip durations or invalid overlaps.

        Args:
            scene: Original scene with transitions
            resolved_clips: List of resolved clips with timings
            transition_regions: List of transition regions
            audio_sync: AudioSync object with beat data (or None)

        Returns:
            Tuple of (adjusted_clips, adjusted_transitions)
        """
        import logging
        from engine.scene import BeatSync

        # If no audio_sync or no beats, return unchanged
        if audio_sync is None or len(audio_sync.beats) == 0:
            return resolved_clips, transition_regions

        # If no transitions, return unchanged
        if len(scene.transitions) == 0:
            return resolved_clips, transition_regions

        # Create mutable copies
        adjusted_clips = [
            ResolvedClip(
                source=clip.source,
                start_time=clip.start_time,
                end_time=clip.end_time,
                camera_path=clip.camera_path,
                effects=clip.effects
            )
            for clip in resolved_clips
        ]

        adjusted_transitions = [
            TransitionRegion(
                start_time=tr.start_time,
                end_time=tr.end_time,
                clip_a_index=tr.clip_a_index,
                clip_b_index=tr.clip_b_index,
                transition_function=tr.transition_function,
                easing_function=tr.easing_function
            )
            for tr in transition_regions
        ]

        # Process each transition
        for i, transition in enumerate(scene.transitions):
            if i >= len(adjusted_transitions):
                break

            tr = adjusted_transitions[i]
            original_start = tr.start_time
            original_end = tr.end_time
            original_duration = original_end - original_start

            # Handle different sync modes
            if transition.sync == BeatSync.NONE:
                # No adjustment needed
                continue

            elif transition.sync == BeatSync.NEAREST_BEAT:
                # Snap transition start to nearest beat
                nearest_beat = audio_sync.get_nearest_beat(original_start)
                if nearest_beat is None:
                    logging.warning(
                        f"Transition {i}: No beats found, using declared timing"
                    )
                    continue

                # Compute adjusted start time
                adjusted_start = nearest_beat
                adjusted_end = adjusted_start + original_duration

                # Validate: check that clip_b still has positive duration
                clip_b_idx = tr.clip_b_index
                if clip_b_idx < len(adjusted_clips):
                    clip_b = adjusted_clips[clip_b_idx]
                    clip_b_original_end = clip_b.end_time

                    # Clip B starts at transition start
                    # Clip B ends at its original end
                    # Duration = original_end - adjusted_start
                    new_clip_b_duration = clip_b_original_end - adjusted_start

                    if new_clip_b_duration <= 0:
                        logging.warning(
                            f"Transition {i}: Beat snap would create negative clip duration, "
                            f"using declared timing"
                        )
                        continue

                # Apply adjustment
                tr.start_time = adjusted_start
                tr.end_time = adjusted_end

                # Update clip timings
                # Clip B starts at transition start
                if clip_b_idx < len(adjusted_clips):
                    adjusted_clips[clip_b_idx].start_time = adjusted_start

                # Adjust subsequent clips
                for j in range(clip_b_idx + 1, len(adjusted_clips)):
                    # Shift by the delta
                    delta = adjusted_start - original_start
                    adjusted_clips[j].start_time += delta
                    adjusted_clips[j].end_time += delta

                # Adjust subsequent transitions
                for j in range(i + 1, len(adjusted_transitions)):
                    delta = adjusted_start - original_start
                    adjusted_transitions[j].start_time += delta
                    adjusted_transitions[j].end_time += delta

            elif transition.sync == BeatSync.BEAT_GRID:
                # Snap both start and end to nearest beats
                nearest_start_beat = audio_sync.get_nearest_beat(original_start)
                nearest_end_beat = audio_sync.get_nearest_beat(original_end)

                if nearest_start_beat is None or nearest_end_beat is None:
                    logging.warning(
                        f"Transition {i}: No beats found, using declared timing"
                    )
                    continue

                # Compute adjusted times
                adjusted_start = nearest_start_beat
                adjusted_end = nearest_end_beat
                adjusted_duration = adjusted_end - adjusted_start

                # Validate: duration must be positive
                if adjusted_duration <= 0:
                    logging.warning(
                        f"Transition {i}: Beat grid would create non-positive duration, "
                        f"using declared timing"
                    )
                    continue

                # Validate: check clip durations
                clip_a_idx = tr.clip_a_index
                clip_b_idx = tr.clip_b_index

                if clip_b_idx < len(adjusted_clips):
                    clip_b = adjusted_clips[clip_b_idx]
                    clip_b_original_end = clip_b.end_time
                    new_clip_b_duration = clip_b_original_end - adjusted_start

                    if new_clip_b_duration <= 0:
                        logging.warning(
                            f"Transition {i}: Beat grid would create negative clip duration, "
                            f"using declared timing"
                        )
                        continue

                # Apply adjustment
                tr.start_time = adjusted_start
                tr.end_time = adjusted_end

                # Update clip timings
                if clip_b_idx < len(adjusted_clips):
                    adjusted_clips[clip_b_idx].start_time = adjusted_start

                # Adjust subsequent clips
                for j in range(clip_b_idx + 1, len(adjusted_clips)):
                    delta = adjusted_start - original_start
                    adjusted_clips[j].start_time += delta
                    adjusted_clips[j].end_time += delta

                # Adjust subsequent transitions
                for j in range(i + 1, len(adjusted_transitions)):
                    delta = adjusted_start - original_start
                    adjusted_transitions[j].start_time += delta
                    adjusted_transitions[j].end_time += delta

        return adjusted_clips, adjusted_transitions


