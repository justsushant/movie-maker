"""Scene planner: resolves Scene DSL into concrete timeline with timings."""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass
class ResolvedTimeline:
    """Fully resolved timeline ready for rendering."""
    
    clips: list[ResolvedClip]
    resolution: tuple[int, int]
    fps: int
    duration: float



class ScenePlanner:
    """Converts Scene DSL into a concrete timeline."""
    
    def plan(self, scene: Scene, image_loader: ImageLoader) -> ResolvedTimeline:
        """
        Resolve clip timings and compute camera paths.
        
        Args:
            scene: Scene description
            image_loader: For loading images to get dimensions
            
        Returns:
            ResolvedTimeline ready for rendering
        """
        resolved_clips = []
        current_time = 0.0
        
        for clip in scene.clips:
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
            
            # Create resolved clip with absolute timing
            # Use closure to capture current_time for this specific clip
            start = current_time
            resolved = ResolvedClip(
                source=Path(clip.source),
                start_time=start,
                end_time=start + clip.duration,
                camera_path=lambda t, fn=camera_path_fn, s=start: fn(t - s)
            )
            resolved_clips.append(resolved)
            current_time += clip.duration
        
        return ResolvedTimeline(
            clips=resolved_clips,
            resolution=scene.resolution,
            fps=scene.fps,
            duration=current_time
        )
