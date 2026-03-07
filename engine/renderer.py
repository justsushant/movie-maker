"""Frame renderer: generates video frames from resolved timeline."""

from __future__ import annotations

from typing import Optional

import numpy as np

from engine.camera import VirtualCamera
from engine.image_loader import ImageLoader
from engine.planner import ResolvedClip, ResolvedTimeline, TransitionRegion


class FrameRenderer:
    """Generates video frames from a resolved timeline with transitions and effects."""
    
    def __init__(self, timeline: ResolvedTimeline, image_loader: ImageLoader):
        """
        Initialize frame renderer.
        
        Args:
            timeline: Resolved timeline with clips and timings
            image_loader: Image loader for loading source images
        """
        self.timeline = timeline
        self.image_loader = image_loader
        self.output_width, self.output_height = timeline.resolution
    
    def render_frame(self, t: float) -> np.ndarray:
        """
        Render a single frame at time t, handling transitions and effects.
        
        Args:
            t: Time in seconds
            
        Returns:
            HxWx3 numpy array (RGB) at output resolution
        """
        # Check if we're in a transition region
        transition = self._find_transition_at_time(t)
        
        if transition is not None:
            # Render both clips and blend
            return self._render_transition_frame(t, transition)
        else:
            # Render single clip (Phase 1 behavior)
            return self._render_single_clip_frame(t)
    
    def _render_single_clip_frame(self, t: float) -> np.ndarray:
        """Render a frame from a single clip with effects."""
        active_clip = self._find_active_clip(t)
        
        if active_clip is None:
            # No clip active - return black frame
            return np.zeros(
                (self.output_height, self.output_width, 3),
                dtype=np.uint8
            )
        
        # Render base frame from clip
        base_frame = self._render_clip_base(active_clip, t)
        
        # Apply effect chain
        final_frame = self._apply_effects(base_frame, active_clip, t)
        
        return final_frame
    
    def _render_transition_frame(self, t: float, transition: TransitionRegion) -> np.ndarray:
        """Render a frame during a transition between two clips."""
        clip_a = self.timeline.clips[transition.clip_a_index]
        clip_b = self.timeline.clips[transition.clip_b_index]
        
        # Render both clips with their effect chains
        frame_a = self._render_clip_base(clip_a, t)
        frame_a = self._apply_effects(frame_a, clip_a, t)
        
        frame_b = self._render_clip_base(clip_b, t)
        frame_b = self._apply_effects(frame_b, clip_b, t)
        
        # Validate dimensions match
        if frame_a.shape != frame_b.shape:
            raise ValueError(
                f"Frame dimension mismatch during transition: "
                f"clip {transition.clip_a_index} produced {frame_a.shape}, "
                f"clip {transition.clip_b_index} produced {frame_b.shape}"
            )
        
        # Compute transition progress
        transition_duration = transition.end_time - transition.start_time
        raw_progress = (t - transition.start_time) / transition_duration
        raw_progress = np.clip(raw_progress, 0.0, 1.0)
        
        # Apply easing
        eased_progress = transition.easing_function(raw_progress)
        
        # Blend frames using transition function
        blended_frame = transition.transition_function(frame_a, frame_b, eased_progress)
        
        return blended_frame
    
    def _render_clip_base(self, clip: ResolvedClip, t: float) -> np.ndarray:
        """Render the base frame from a clip (camera transform only, no effects)."""
        # Load source image
        source_image = self.image_loader.load(clip.source)
        
        # Get camera viewport for this time
        viewport = clip.camera_path(t)
        
        # Apply camera transform
        camera = VirtualCamera(viewport)
        frame = camera.apply_transform(
            source_image,
            (self.output_width, self.output_height)
        )
        
        return frame
    
    def _apply_effects(
        self,
        frame: np.ndarray,
        clip: ResolvedClip,
        t: float
    ) -> np.ndarray:
        """Apply the effect chain to a frame."""
        # Check if clip has effects attribute (backward compatibility)
        if not hasattr(clip, 'effects') or not clip.effects:
            return frame
        
        # Compute clip progress
        clip_duration = clip.end_time - clip.start_time
        progress = (t - clip.start_time) / clip_duration if clip_duration > 0 else 0.0
        progress = np.clip(progress, 0.0, 1.0)
        
        # Apply effects in sequence
        result = frame
        for i, effect in enumerate(clip.effects):
            try:
                processed = effect(result, t, progress)
                
                # Validate effect output
                if processed.shape != result.shape:
                    raise ValueError(
                        f"Effect {i} changed frame dimensions from {result.shape} to {processed.shape}"
                    )
                if processed.dtype != result.dtype:
                    raise ValueError(
                        f"Effect {i} changed frame dtype from {result.dtype} to {processed.dtype}"
                    )
                
                result = processed
                
            except Exception as e:
                raise Exception(
                    f"Error applying effect {i} to clip at {clip.source} at time {t:.2f}s: {e}"
                ) from e
        
        return result
    
    def _find_active_clip(self, t: float) -> Optional[ResolvedClip]:
        """Find the clip that is active at time t (excluding transition regions)."""
        # Check if we're in a transition
        if self._find_transition_at_time(t) is not None:
            return None
        
        # Find clip containing t
        for clip in self.timeline.clips:
            if clip.start_time <= t < clip.end_time:
                return clip
        
        return None
    
    def _find_transition_at_time(self, t: float) -> Optional[TransitionRegion]:
        """Find the transition region active at time t."""
        for transition in self.timeline.transitions:
            if transition.start_time <= t < transition.end_time:
                return transition
        
        return None
