"""Scene DSL: declarative video composition with clips and motion presets."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Union, Protocol, Optional
import numpy as np


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


class TransitionType(Enum):
    """Transition types for blending between clips."""
    
    # Blend transitions
    CROSSFADE = "crossfade"
    FADE_THROUGH_BLACK = "fade_through_black"
    FADE_THROUGH_WHITE = "fade_through_white"
    
    # Geometric transitions - slides
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    
    # Geometric transitions - pushes
    PUSH_LEFT = "push_left"
    PUSH_RIGHT = "push_right"
    PUSH_UP = "push_up"
    PUSH_DOWN = "push_down"
    
    # Geometric transitions - wipes
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"
    WIPE_UP = "wipe_up"
    WIPE_DOWN = "wipe_down"
    
    # Geometric transitions - shapes
    IRIS_OPEN = "iris_open"
    IRIS_CLOSE = "iris_close"
    CLOCK_WIPE = "clock_wipe"
    DIAMOND_WIPE = "diamond_wipe"
    BLINDS_HORIZONTAL = "blinds_horizontal"
    BLINDS_VERTICAL = "blinds_vertical"
    
    # Animated transitions
    ZOOM_THROUGH = "zoom_through"
    WHIP_PAN = "whip_pan"
    PIXELATE = "pixelate"
    GLITCH = "glitch"


class BeatSync(Enum):
    """Controls how transitions align with audio beats (Phase 3)."""
    
    NONE = "none"                    # Use declared timing (default)
    NEAREST_BEAT = "nearest_beat"    # Snap transition start to nearest beat
    BEAT_GRID = "beat_grid"          # Snap both start and end to beats


class TransitionFunction(Protocol):
    """Protocol for transition functions."""
    
    def __call__(
        self, 
        frame_a: np.ndarray, 
        frame_b: np.ndarray, 
        progress: float
    ) -> np.ndarray:
        """
        Blend two frames based on transition progress.
        
        Args:
            frame_a: Outgoing frame (HxWx3 uint8)
            frame_b: Incoming frame (HxWx3 uint8)
            progress: Transition progress in [0.0, 1.0]
            
        Returns:
            Blended frame (HxWx3 uint8)
        """
        ...


class EffectFunction(Protocol):
    """Protocol for effect functions."""
    
    def __call__(
        self, 
        frame: np.ndarray, 
        t: float, 
        progress: float
    ) -> np.ndarray:
        """
        Apply visual effect to a frame.
        
        Args:
            frame: Input frame (HxWx3 uint8)
            t: Absolute time in seconds
            progress: Clip progress in [0.0, 1.0]
            
        Returns:
            Processed frame (HxWx3 uint8)
        """
        ...


@dataclass
class Transition:
    """Defines a transition between two clips."""
    
    type: TransitionType
    duration: float  # seconds
    easing: 'EasingFunction' = None  # defaults to ease_in_out_cubic
    sync: BeatSync = BeatSync.NONE  # Phase 3: beat synchronization mode
    
    def __post_init__(self):
        if self.duration <= 0:
            raise ValueError(f"Transition duration must be positive, got {self.duration}")
        if self.easing is None:
            from .easing import ease_in_out_cubic
            self.easing = ease_in_out_cubic


@dataclass
class ImageClip:
    """A single image displayed for a duration with optional motion."""
    
    source: Union[str, Path]
    duration: float  # seconds
    motion: MotionPreset = MotionPreset.STATIC
    effects: list[EffectFunction] = field(default_factory=list)


@dataclass
class Scene:
    """Declarative video composition."""
    
    clips: list[ImageClip] = field(default_factory=list)
    resolution: tuple[int, int] = (1920, 1080)
    fps: int = 30
    transitions: list[Transition] = field(default_factory=list)
    audio: Optional[Union[str, Path]] = None  # Phase 3: audio file for analysis
    
    def __post_init__(self):
        # Validate transitions count (only if there are clips)
        if len(self.clips) > 0 and len(self.transitions) > len(self.clips) - 1:
            raise ValueError(
                f"Scene has {len(self.clips)} clips but {len(self.transitions)} transitions. "
                f"Maximum transitions is {len(self.clips) - 1}."
            )
