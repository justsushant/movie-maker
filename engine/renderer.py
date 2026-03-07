"""Frame renderer: generates video frames from resolved timeline."""

from __future__ import annotations

from typing import Optional

import numpy as np

from engine.camera import VirtualCamera
from engine.image_loader import ImageLoader
from engine.planner import ResolvedClip, ResolvedTimeline


class FrameRenderer:
    """Generates video frames from a resolved timeline."""
    
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
        Render a single frame at time t.
        
        Args:
            t: Time in seconds
            
        Returns:
            HxWx3 numpy array (RGB) at output resolution
        """
        # Find active clip
        active_clip = self._find_active_clip(t)
        
        if active_clip is None:
            # No clip active - return black frame
            return np.zeros(
                (self.output_height, self.output_width, 3), 
                dtype=np.uint8
            )
        
        # Load source image
        source_image = self.image_loader.load(active_clip.source)
        
        # Get camera viewport for this time
        viewport = active_clip.camera_path(t)
        
        # Apply camera transform
        camera = VirtualCamera(viewport)
        frame = camera.apply_transform(
            source_image, 
            (self.output_width, self.output_height)
        )
        
        return frame
    
    def _find_active_clip(self, t: float) -> Optional[ResolvedClip]:
        """
        Find the clip that is active at time t.
        
        Args:
            t: Time in seconds
            
        Returns:
            Active clip or None if no clip is active
        """
        for clip in self.timeline.clips:
            if clip.start_time <= t < clip.end_time:
                return clip
        return None
