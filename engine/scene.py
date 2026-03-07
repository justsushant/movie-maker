"""Scene DSL: declarative video composition with clips and motion presets."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Union


class MotionPreset(Enum):
    """Predefined camera movement patterns."""
    
    STATIC = "static"
    KEN_BURNS_ZOOM_IN = "ken_burns_zoom_in"
    KEN_BURNS_ZOOM_OUT = "ken_burns_zoom_out"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    PAN_UP = "pan_up"
    PAN_DOWN = "pan_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"



@dataclass
class ImageClip:
    """A single image displayed for a duration with optional motion."""
    
    source: Union[str, Path]
    duration: float  # seconds
    motion: MotionPreset = MotionPreset.STATIC



@dataclass
class Scene:
    """Declarative video composition."""
    
    clips: list[ImageClip] = field(default_factory=list)
    resolution: tuple[int, int] = (1920, 1080)
    fps: int = 30
