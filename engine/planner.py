"""Scene planner: resolves Scene DSL into concrete timeline with timings."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

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
        
        total_duration = resolved_clips[-1].end_time if resolved_clips else 0.0
        
        return ResolvedTimeline(
            clips=resolved_clips,
            transitions=transition_regions,
            resolution=scene.resolution,
            fps=scene.fps,
            duration=total_duration
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
