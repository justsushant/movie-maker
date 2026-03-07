"""Video configuration for rendering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass
class VideoConfig:
    """Configuration for video rendering.
    
    Attributes:
        width: Video width in pixels
        height: Video height in pixels
        fps: Frames per second
        bg_color: Background color as RGB tuple (0-255)
    """
    width: int = 1920
    height: int = 1080
    fps: int = 30
    bg_color: Tuple[int, int, int] = (0, 0, 0)
    
    @classmethod
    def from_dict(cls, config: dict) -> VideoConfig:
        """Create VideoConfig from legacy config dictionary.
        
        Args:
            config: Configuration dictionary containing video settings
            
        Returns:
            VideoConfig instance with values from the dictionary
        """
        return cls(
            width=config.get("width", 1920),
            height=config.get("height", 1080),
            fps=config.get("fps", 30),
            bg_color=config.get("bg_color", (0, 0, 0))
        )
