"""Virtual camera system with viewport transforms and motion presets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import cv2
import numpy as np

from engine.easing import EasingFunction, ease_in_out_cubic
from engine.scene import MotionPreset


@dataclass
class Rect:
    """Rectangle in image coordinates."""
    
    x: float
    y: float
    width: float
    height: float
    
    def clamp_to(self, image_width: int, image_height: int) -> Rect:
        """
        Clamp rectangle to image boundaries.
        
        Ensures the rectangle stays within valid image coordinates and
        has positive dimensions.
        
        Args:
            image_width: Width of the source image
            image_height: Height of the source image
            
        Returns:
            New Rect clamped to valid bounds
        """
        # Clamp width and height to image dimensions
        w = min(self.width, image_width)
        h = min(self.height, image_height)
        
        # Clamp x and y to ensure rect stays within image
        x = max(0, min(self.x, image_width - w))
        y = max(0, min(self.y, image_height - h))
        
        return Rect(x, y, w, h)



class VirtualCamera:
    """Defines a viewport into a source image."""
    
    def __init__(self, viewport: Rect):
        """
        Initialize virtual camera with a viewport rectangle.
        
        Args:
            viewport: Rectangle defining the visible region of the source image
        """
        self.viewport = viewport
    
    def apply_transform(
        self, 
        source_image: np.ndarray, 
        output_size: tuple[int, int]
    ) -> np.ndarray:
        """
        Crop source image to viewport and resize to output size.
        
        Args:
            source_image: HxWx3 numpy array (RGB)
            output_size: (width, height) for output frame
            
        Returns:
            Transformed HxWx3 numpy array at output resolution
        """
        h, w = source_image.shape[:2]
        viewport = self.viewport.clamp_to(w, h)
        
        # Crop to viewport
        x1 = int(viewport.x)
        y1 = int(viewport.y)
        x2 = int(viewport.x + viewport.width)
        y2 = int(viewport.y + viewport.height)
        cropped = source_image[y1:y2, x1:x2]
        
        # Resize to output size using high-quality bicubic interpolation
        resized = cv2.resize(cropped, output_size, interpolation=cv2.INTER_CUBIC)
        return resized
    
    @staticmethod
    def interpolate(
        rect_start: Rect,
        rect_end: Rect,
        progress: float,
        easing_fn: EasingFunction
    ) -> Rect:
        """
        Interpolate between two rectangles using an easing function.
        
        Args:
            rect_start: Starting viewport
            rect_end: Ending viewport
            progress: Time progress in [0, 1]
            easing_fn: Easing function to apply
            
        Returns:
            Interpolated rectangle
        """
        t = easing_fn(progress)
        return Rect(
            x=rect_start.x + (rect_end.x - rect_start.x) * t,
            y=rect_start.y + (rect_end.y - rect_start.y) * t,
            width=rect_start.width + (rect_end.width - rect_start.width) * t,
            height=rect_start.height + (rect_end.height - rect_start.height) * t,
        )



def compute_motion_path(
    preset: MotionPreset,
    image_size: tuple[int, int],
    output_size: tuple[int, int],
    duration: float
) -> Callable[[float], Rect]:
    """
    Compute a camera path function for a motion preset.
    
    Args:
        preset: Motion pattern to apply
        image_size: (width, height) of source image
        output_size: (width, height) of output frame
        duration: Clip duration in seconds
        
    Returns:
        Function that maps time -> viewport Rect
        
    Raises:
        ValueError: If preset is unknown
    """
    img_w, img_h = image_size
    out_w, out_h = output_size
    
    if preset == MotionPreset.STATIC:
        # Center crop to output aspect ratio
        aspect = out_w / out_h
        if img_w / img_h > aspect:
            # Image is wider - fit height
            viewport_h = img_h
            viewport_w = img_h * aspect
        else:
            # Image is taller - fit width
            viewport_w = img_w
            viewport_h = img_w / aspect
        x = (img_w - viewport_w) / 2
        y = (img_h - viewport_h) / 2
        rect = Rect(x, y, viewport_w, viewport_h)
        return lambda t: rect
    
    elif preset == MotionPreset.KEN_BURNS_ZOOM_IN:
        # Start with full image, zoom to 50% centered
        start = Rect(0, 0, img_w, img_h)
        end_w = img_w * 0.5
        end_h = img_h * 0.5
        end = Rect((img_w - end_w) / 2, (img_h - end_h) / 2, end_w, end_h)
        return lambda t: VirtualCamera.interpolate(
            start, end, t / duration, ease_in_out_cubic
        )
    
    elif preset == MotionPreset.KEN_BURNS_ZOOM_OUT:
        # Start at 50% centered, zoom out to full
        start_w = img_w * 0.5
        start_h = img_h * 0.5
        start = Rect((img_w - start_w) / 2, (img_h - start_h) / 2, start_w, start_h)
        end = Rect(0, 0, img_w, img_h)
        return lambda t: VirtualCamera.interpolate(
            start, end, t / duration, ease_in_out_cubic
        )
    
    elif preset == MotionPreset.PAN_LEFT:
        # Viewport moves right (scene moves left)
        viewport_w = out_w
        viewport_h = out_h
        start = Rect(0, 0, viewport_w, viewport_h)
        end = Rect(img_w - viewport_w, 0, viewport_w, viewport_h)
        return lambda t: VirtualCamera.interpolate(
            start, end, t / duration, ease_in_out_cubic
        )
    
    elif preset == MotionPreset.PAN_RIGHT:
        # Viewport moves left (scene moves right)
        viewport_w = out_w
        viewport_h = out_h
        start = Rect(img_w - viewport_w, 0, viewport_w, viewport_h)
        end = Rect(0, 0, viewport_w, viewport_h)
        return lambda t: VirtualCamera.interpolate(
            start, end, t / duration, ease_in_out_cubic
        )
    
    elif preset == MotionPreset.PAN_UP:
        # Viewport moves down (scene moves up)
        viewport_w = out_w
        viewport_h = out_h
        start = Rect(0, 0, viewport_w, viewport_h)
        end = Rect(0, img_h - viewport_h, viewport_w, viewport_h)
        return lambda t: VirtualCamera.interpolate(
            start, end, t / duration, ease_in_out_cubic
        )
    
    elif preset == MotionPreset.PAN_DOWN:
        # Viewport moves up (scene moves down)
        viewport_w = out_w
        viewport_h = out_h
        start = Rect(0, img_h - viewport_h, viewport_w, viewport_h)
        end = Rect(0, 0, viewport_w, viewport_h)
        return lambda t: VirtualCamera.interpolate(
            start, end, t / duration, ease_in_out_cubic
        )
    
    elif preset == MotionPreset.ZOOM_IN:
        # Shrink viewport toward center
        start = Rect(0, 0, img_w, img_h)
        end_w = img_w * 0.5
        end_h = img_h * 0.5
        end = Rect((img_w - end_w) / 2, (img_h - end_h) / 2, end_w, end_h)
        return lambda t: VirtualCamera.interpolate(
            start, end, t / duration, ease_in_out_cubic
        )
    
    elif preset == MotionPreset.ZOOM_OUT:
        # Expand viewport from center
        start_w = img_w * 0.5
        start_h = img_h * 0.5
        start = Rect((img_w - start_w) / 2, (img_h - start_h) / 2, start_w, start_h)
        end = Rect(0, 0, img_w, img_h)
        return lambda t: VirtualCamera.interpolate(
            start, end, t / duration, ease_in_out_cubic
        )
    
    else:
        raise ValueError(f"Unknown motion preset: {preset}")
