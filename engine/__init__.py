"""
Video generation engine for PRISM.

This module provides a clip-based video composition system that generates
frames from image sequences with camera motion effects (Ken Burns, pan, zoom).
"""

from engine.scene import Scene, ImageClip, MotionPreset
from engine.easing import (
    linear,
    ease_in_cubic,
    ease_out_cubic,
    ease_in_out_cubic,
    EasingFunction,
)
from engine.camera import VirtualCamera, Rect, compute_motion_path
from engine.planner import ScenePlanner, ResolvedTimeline, ResolvedClip
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader

__all__ = [
    # Scene DSL
    "Scene",
    "ImageClip",
    "MotionPreset",
    # Easing
    "EasingFunction",
    "linear",
    "ease_in_cubic",
    "ease_out_cubic",
    "ease_in_out_cubic",
    # Camera
    "VirtualCamera",
    "Rect",
    "compute_motion_path",
    # Planning
    "ScenePlanner",
    "ResolvedTimeline",
    "ResolvedClip",
    # Rendering
    "FrameRenderer",
    "ImageLoader",
]
