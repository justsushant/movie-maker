"""Transition function implementations for Phase 2.

This module provides transition functions that blend two frames during clip overlaps.
All transitions follow the TransitionFunction protocol: (frame_a, frame_b, progress) -> frame.

Transition Categories:
- Blend: Alpha blending and color space transitions (crossfade, fade through black/white)
- Geometric: Spatial transformations (slides, pushes, wipes, iris, shapes)
- Animated: Complex motion effects (zoom through, whip pan, pixelate, glitch)
"""

from __future__ import annotations
import numpy as np
import cv2


# ============================================================================
# Blend Transitions
# ============================================================================

def crossfade(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Linear crossfade between two frames.
    
    Formula: result = frame_a * (1 - progress) + frame_b * progress
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    alpha = progress
    blended = (frame_a * (1 - alpha) + frame_b * alpha).astype(np.uint8)
    return blended


def fade_through_black(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Fade to black in first half, then fade from black in second half.
    
    Progress [0.0, 0.5]: frame_a fades to black
    Progress [0.5, 1.0]: black fades to frame_b
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    if progress < 0.5:
        # Fade out frame_a
        fade_progress = 1.0 - (progress * 2.0)
        return (frame_a * fade_progress).astype(np.uint8)
    else:
        # Fade in frame_b
        fade_progress = (progress - 0.5) * 2.0
        return (frame_b * fade_progress).astype(np.uint8)


def fade_through_white(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Fade to white in first half, then fade from white in second half.
    
    Progress [0.0, 0.5]: frame_a fades to white
    Progress [0.5, 1.0]: white fades to frame_b
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    white = np.full_like(frame_a, 255, dtype=np.uint8)
    
    if progress < 0.5:
        # Fade to white
        fade_progress = progress * 2.0
        return (frame_a * (1 - fade_progress) + white * fade_progress).astype(np.uint8)
    else:
        # Fade from white
        fade_progress = (progress - 0.5) * 2.0
        return (white * (1 - fade_progress) + frame_b * fade_progress).astype(np.uint8)


def fade_through_color(color: tuple[int, int, int]):
    """
    Create a fade through specified RGB color transition.
    
    Factory function that returns a transition function.
    
    Args:
        color: RGB color tuple (r, g, b) with values in [0, 255]
        
    Returns:
        Transition function that fades through the specified color
    """
    def transition(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
        """
        Fade through specified color.
        
        Progress [0.0, 0.5]: frame_a fades to color
        Progress [0.5, 1.0]: color fades to frame_b
        """
        color_frame = np.full_like(frame_a, color, dtype=np.uint8)
        
        if progress < 0.5:
            # Fade to color
            fade_progress = progress * 2.0
            return (frame_a * (1 - fade_progress) + color_frame * fade_progress).astype(np.uint8)
        else:
            # Fade from color
            fade_progress = (progress - 0.5) * 2.0
            return (color_frame * (1 - fade_progress) + frame_b * fade_progress).astype(np.uint8)
    
    return transition



# ============================================================================
# Geometric Transitions - Slides
# ============================================================================

def slide_left(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Slide frame_b from right to left over frame_a.
    
    Frame_b enters from the right edge and moves left.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    offset = int(w * (1 - progress))
    
    result = frame_a.copy()
    if offset < w:
        # Copy the visible portion of frame_b
        visible_width = w - offset
        result[:, offset:] = frame_b[:, :visible_width]
    
    return result


def slide_right(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Slide frame_b from left to right over frame_a.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    offset = int(w * progress)
    
    result = frame_a.copy()
    if offset > 0:
        visible_width = min(offset, w)
        result[:, :visible_width] = frame_b[:, w - visible_width:]
    
    return result


def slide_up(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Slide frame_b from bottom to top over frame_a.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    offset = int(h * (1 - progress))
    
    result = frame_a.copy()
    if offset < h:
        visible_height = h - offset
        result[offset:, :] = frame_b[:visible_height, :]
    
    return result


def slide_down(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Slide frame_b from top to bottom over frame_a.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    offset = int(h * progress)
    
    result = frame_a.copy()
    if offset > 0:
        visible_height = min(offset, h)
        result[:visible_height, :] = frame_b[h - visible_height:, :]
    
    return result



# ============================================================================
# Geometric Transitions - Pushes
# ============================================================================

def push_left(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Push frame_a left while frame_b enters from right.
    
    Both frames move together, no black regions.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    offset = int(w * progress)
    
    result = np.zeros_like(frame_a)
    
    # Frame_a portion (moving left)
    if offset < w:
        visible_a = w - offset
        result[:, :visible_a] = frame_a[:, offset:]
    
    # Frame_b portion (entering from right)
    if offset > 0:
        result[:, w - offset:] = frame_b[:, :offset]
    
    return result


def push_right(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Push frame_a right while frame_b enters from left.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    offset = int(w * progress)
    
    result = np.zeros_like(frame_a)
    
    # Frame_b portion (entering from left)
    if offset > 0:
        result[:, :offset] = frame_b[:, w - offset:]
    
    # Frame_a portion (moving right)
    if offset < w:
        visible_a = w - offset
        result[:, offset:] = frame_a[:, :visible_a]
    
    return result


def push_up(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Push frame_a up while frame_b enters from bottom.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    offset = int(h * progress)
    
    result = np.zeros_like(frame_a)
    
    # Frame_a portion (moving up)
    if offset < h:
        visible_a = h - offset
        result[:visible_a, :] = frame_a[offset:, :]
    
    # Frame_b portion (entering from bottom)
    if offset > 0:
        result[h - offset:, :] = frame_b[:offset, :]
    
    return result


def push_down(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Push frame_a down while frame_b enters from top.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    offset = int(h * progress)
    
    result = np.zeros_like(frame_a)
    
    # Frame_b portion (entering from top)
    if offset > 0:
        result[:offset, :] = frame_b[h - offset:, :]
    
    # Frame_a portion (moving down)
    if offset < h:
        visible_a = h - offset
        result[offset:, :] = frame_a[:visible_a, :]
    
    return result



# ============================================================================
# Geometric Transitions - Wipes
# ============================================================================

def wipe_left(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Wipe from left to right with hard edge.
    
    Frame_b is revealed from left to right.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    split = int(w * progress)
    
    result = frame_a.copy()
    if split > 0:
        result[:, :split] = frame_b[:, :split]
    
    return result


def wipe_right(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Wipe from right to left with hard edge.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    split = int(w * (1 - progress))
    
    result = frame_a.copy()
    if split < w:
        result[:, split:] = frame_b[:, split:]
    
    return result


def wipe_up(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Wipe from top to bottom with hard edge.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    split = int(h * progress)
    
    result = frame_a.copy()
    if split > 0:
        result[:split, :] = frame_b[:split, :]
    
    return result


def wipe_down(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Wipe from bottom to top with hard edge.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    split = int(h * (1 - progress))
    
    result = frame_a.copy()
    if split < h:
        result[split:, :] = frame_b[split:, :]
    
    return result



def wipe_left_soft(feather_width: int = 50):
    """
    Create a wipe_left transition with soft edge.
    
    Args:
        feather_width: Width of gradient feather in pixels
        
    Returns:
        Transition function with soft edge
    """
    def transition(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
        h, w = frame_a.shape[:2]
        split = int(w * progress)
        
        result = frame_a.copy()
        
        # Create gradient mask
        if split > 0:
            start = max(0, split - feather_width)
            end = min(w, split + feather_width)
            
            # Hard edge region
            if start > 0:
                result[:, :start] = frame_b[:, :start]
            
            # Soft edge region
            if end > start:
                gradient = np.linspace(0, 1, end - start)
                gradient = gradient[np.newaxis, :, np.newaxis]
                result[:, start:end] = (
                    frame_b[:, start:end] * gradient + 
                    frame_a[:, start:end] * (1 - gradient)
                ).astype(np.uint8)
        
        return result
    
    return transition


def wipe_right_soft(feather_width: int = 50):
    """Create a wipe_right transition with soft edge."""
    def transition(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
        h, w = frame_a.shape[:2]
        split = int(w * (1 - progress))
        
        result = frame_a.copy()
        
        if split < w:
            start = max(0, split - feather_width)
            end = min(w, split + feather_width)
            
            # Hard edge region
            if end < w:
                result[:, end:] = frame_b[:, end:]
            
            # Soft edge region
            if end > start:
                gradient = np.linspace(1, 0, end - start)
                gradient = gradient[np.newaxis, :, np.newaxis]
                result[:, start:end] = (
                    frame_a[:, start:end] * gradient + 
                    frame_b[:, start:end] * (1 - gradient)
                ).astype(np.uint8)
        
        return result
    
    return transition


def wipe_up_soft(feather_width: int = 50):
    """Create a wipe_up transition with soft edge."""
    def transition(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
        h, w = frame_a.shape[:2]
        split = int(h * progress)
        
        result = frame_a.copy()
        
        if split > 0:
            start = max(0, split - feather_width)
            end = min(h, split + feather_width)
            
            # Hard edge region
            if start > 0:
                result[:start, :] = frame_b[:start, :]
            
            # Soft edge region
            if end > start:
                gradient = np.linspace(0, 1, end - start)
                gradient = gradient[:, np.newaxis, np.newaxis]
                result[start:end, :] = (
                    frame_b[start:end, :] * gradient + 
                    frame_a[start:end, :] * (1 - gradient)
                ).astype(np.uint8)
        
        return result
    
    return transition


def wipe_down_soft(feather_width: int = 50):
    """Create a wipe_down transition with soft edge."""
    def transition(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
        h, w = frame_a.shape[:2]
        split = int(h * (1 - progress))
        
        result = frame_a.copy()
        
        if split < h:
            start = max(0, split - feather_width)
            end = min(h, split + feather_width)
            
            # Hard edge region
            if end < h:
                result[end:, :] = frame_b[end:, :]
            
            # Soft edge region
            if end > start:
                gradient = np.linspace(1, 0, end - start)
                gradient = gradient[:, np.newaxis, np.newaxis]
                result[start:end, :] = (
                    frame_a[start:end, :] * gradient + 
                    frame_b[start:end, :] * (1 - gradient)
                ).astype(np.uint8)
        
        return result
    
    return transition



# ============================================================================
# Geometric Transitions - Shapes
# ============================================================================

def iris_open(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Reveal frame_b through expanding circle from center.
    
    Creates a circular mask that grows from center.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    # At progress=0, return frame_a unchanged
    if progress == 0.0:
        return frame_a.copy()
    
    # At progress=1, return frame_b unchanged
    if progress == 1.0:
        return frame_b.copy()
    
    h, w = frame_a.shape[:2]
    center_y, center_x = h // 2, w // 2
    max_radius = np.sqrt(center_x**2 + center_y**2)
    radius = max_radius * progress
    
    # Create circular mask
    y, x = np.ogrid[:h, :w]
    mask = ((x - center_x)**2 + (y - center_y)**2) <= radius**2
    mask = mask[:, :, np.newaxis]  # Add channel dimension
    
    result = np.where(mask, frame_b, frame_a)
    return result.astype(np.uint8)


def iris_close(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Reveal frame_b outside shrinking circle from center.
    
    Frame_a is visible inside circle, frame_b outside.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    # At progress=0, return frame_a unchanged (circle at max size)
    if progress == 0.0:
        return frame_a.copy()
    
    # At progress=1, return frame_b unchanged (circle at zero size)
    if progress == 1.0:
        return frame_b.copy()
    
    h, w = frame_a.shape[:2]
    center_y, center_x = h // 2, w // 2
    max_radius = np.sqrt(center_x**2 + center_y**2)
    radius = max_radius * (1 - progress)
    
    # Create circular mask
    y, x = np.ogrid[:h, :w]
    mask = ((x - center_x)**2 + (y - center_y)**2) <= radius**2
    mask = mask[:, :, np.newaxis]
    
    result = np.where(mask, frame_a, frame_b)
    return result.astype(np.uint8)



def clock_wipe(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Clockwise sweep from 12 o'clock.
    
    Reveals frame_b in a clockwise sweep starting from top.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    # At progress=0, return frame_a unchanged
    if progress == 0.0:
        return frame_a.copy()
    
    # At progress=1, return frame_b unchanged
    if progress == 1.0:
        return frame_b.copy()
    
    h, w = frame_a.shape[:2]
    center_y, center_x = h // 2, w // 2
    
    # Create angle map
    y, x = np.ogrid[:h, :w]
    angles = np.arctan2(y - center_y, x - center_x)
    # Rotate so 0 is at top (12 o'clock)
    angles = (angles + np.pi / 2) % (2 * np.pi)
    
    # Progress maps to angle threshold
    threshold = progress * 2 * np.pi
    mask = angles <= threshold
    mask = mask[:, :, np.newaxis]
    
    result = np.where(mask, frame_b, frame_a)
    return result.astype(np.uint8)



def diamond_wipe(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Reveal frame_b through expanding diamond from center.
    
    Uses Manhattan distance for diamond shape.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    # At progress=0, return frame_a unchanged
    if progress == 0.0:
        return frame_a.copy()
    
    # At progress=1, return frame_b unchanged
    if progress == 1.0:
        return frame_b.copy()
    
    h, w = frame_a.shape[:2]
    center_y, center_x = h // 2, w // 2
    max_distance = center_x + center_y
    threshold = max_distance * progress
    
    # Create diamond mask using Manhattan distance
    y, x = np.ogrid[:h, :w]
    distance = np.abs(x - center_x) + np.abs(y - center_y)
    mask = distance <= threshold
    mask = mask[:, :, np.newaxis]
    
    result = np.where(mask, frame_b, frame_a)
    return result.astype(np.uint8)



def blinds_horizontal(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Reveal frame_b through horizontal strips.
    
    Creates venetian blind effect with horizontal slats.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    # At progress=1, return frame_b unchanged
    if progress == 1.0:
        return frame_b.copy()
    
    h, w = frame_a.shape[:2]
    num_blinds = 10
    blind_height = h // num_blinds
    
    result = frame_a.copy()
    reveal_height = int(blind_height * progress)
    
    for i in range(num_blinds):
        start_y = i * blind_height
        # Handle last blind to cover remaining pixels
        if i == num_blinds - 1:
            end_y = min(start_y + reveal_height, h)
        else:
            end_y = min(start_y + reveal_height, (i + 1) * blind_height)
        if end_y > start_y:
            result[start_y:end_y, :] = frame_b[start_y:end_y, :]
    
    return result


def blinds_vertical(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Reveal frame_b through vertical strips.
    
    Creates venetian blind effect with vertical slats.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    # At progress=1, return frame_b unchanged
    if progress == 1.0:
        return frame_b.copy()
    
    h, w = frame_a.shape[:2]
    num_blinds = 10
    blind_width = w // num_blinds
    
    result = frame_a.copy()
    reveal_width = int(blind_width * progress)
    
    for i in range(num_blinds):
        start_x = i * blind_width
        # Handle last blind to cover remaining pixels
        if i == num_blinds - 1:
            end_x = min(start_x + reveal_width, w)
        else:
            end_x = min(start_x + reveal_width, (i + 1) * blind_width)
        if end_x > start_x:
            result[:, start_x:end_x] = frame_b[:, start_x:end_x]
    
    return result



# ============================================================================
# Animated Transitions
# ============================================================================

def zoom_through(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Zoom in on frame_a while fading out, zoom out from frame_b while fading in.
    
    Creates a "zoom through" effect.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    
    # Scale factor: frame_a zooms in, frame_b zooms out
    scale_a = 1.0 + progress * 0.5  # 1.0 -> 1.5
    scale_b = 1.5 - progress * 0.5  # 1.5 -> 1.0
    
    # Resize frames
    new_size_a = (int(w * scale_a), int(h * scale_a))
    new_size_b = (int(w * scale_b), int(h * scale_b))
    
    scaled_a = cv2.resize(frame_a, new_size_a, interpolation=cv2.INTER_LINEAR)
    scaled_b = cv2.resize(frame_b, new_size_b, interpolation=cv2.INTER_LINEAR)
    
    # Center crop to original size
    crop_a = _center_crop(scaled_a, w, h)
    crop_b = _center_crop(scaled_b, w, h)
    
    # Crossfade with progress
    alpha = progress
    result = (crop_a * (1 - alpha) + crop_b * alpha).astype(np.uint8)
    return result



def whip_pan(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Fast horizontal motion blur effect.
    
    Creates a whip pan by applying horizontal motion blur.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    # Use aggressive easing for whip effect
    if progress < 0.3:
        # Mostly frame_a with increasing blur
        blur_amount = int(progress * 100)
        if blur_amount > 1:
            blurred = cv2.blur(frame_a, (blur_amount, 1))
            return blurred
        return frame_a
    elif progress > 0.7:
        # Mostly frame_b with decreasing blur
        blur_amount = int((1 - progress) * 100)
        if blur_amount > 1:
            blurred = cv2.blur(frame_b, (blur_amount, 1))
            return blurred
        return frame_b
    else:
        # Peak blur - blend both frames
        blur_amount = 30
        blurred_a = cv2.blur(frame_a, (blur_amount, 1))
        blurred_b = cv2.blur(frame_b, (blur_amount, 1))
        return ((blurred_a + blurred_b) // 2).astype(np.uint8)



def pixelate(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Pixelate frame_a while un-pixelating frame_b.
    
    Creates a digital transition effect.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    
    # Pixelation level: high at progress=0.5, low at edges
    if progress < 0.5:
        # Pixelate frame_a
        pixel_progress = progress * 2.0
        pixel_size = max(1, int(50 * pixel_progress))
        
        small = cv2.resize(frame_a, (w // pixel_size, h // pixel_size), 
                          interpolation=cv2.INTER_NEAREST)
        pixelated_a = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        
        # Blend with frame_b
        alpha = pixel_progress
        result = (pixelated_a * (1 - alpha) + frame_b * alpha).astype(np.uint8)
    else:
        # Un-pixelate frame_b
        pixel_progress = (1.0 - progress) * 2.0
        pixel_size = max(1, int(50 * pixel_progress))
        
        small = cv2.resize(frame_b, (w // pixel_size, h // pixel_size),
                          interpolation=cv2.INTER_NEAREST)
        pixelated_b = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        
        alpha = 1.0 - pixel_progress
        result = (pixelated_b * (1 - alpha) + frame_b * alpha).astype(np.uint8)
    
    return result



def glitch(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray:
    """
    Digital glitch effect with RGB channel shifts and scanlines.
    
    Creates a digital distortion transition.
    
    Args:
        frame_a: Outgoing frame (HxWx3 uint8)
        frame_b: Incoming frame (HxWx3 uint8)
        progress: Transition progress in [0.0, 1.0]
        
    Returns:
        Blended frame (HxWx3 uint8)
    """
    h, w = frame_a.shape[:2]
    
    # Glitch intensity peaks at progress=0.5
    intensity = 1.0 - abs(progress - 0.5) * 2.0
    
    # Start with crossfade
    alpha = progress
    base = (frame_a * (1 - alpha) + frame_b * alpha).astype(np.uint8)
    
    if intensity < 0.1:
        return base
    
    # RGB channel shift
    shift = int(20 * intensity)
    result = base.copy()
    if shift > 0:
        result[:, shift:, 0] = base[:, :-shift, 0]  # Red channel shift
        result[:, :-shift, 2] = base[:, shift:, 2]  # Blue channel shift
    
    # Add scanlines
    if np.random.random() < intensity:
        scanline_spacing = max(2, int(10 * (1 - intensity)))
        for y in range(0, h, scanline_spacing):
            if np.random.random() < 0.5:
                result[y, :] = (result[y, :] * 0.7).astype(np.uint8)
    
    return result



# ============================================================================
# Helper Functions
# ============================================================================

def _center_crop(image: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    """Crop image to target size from center."""
    h, w = image.shape[:2]
    start_y = (h - target_h) // 2
    start_x = (w - target_w) // 2
    return image[start_y:start_y + target_h, start_x:start_x + target_w]


# ============================================================================
# Transition Registry
# ============================================================================

def get_transition_function(transition_type):
    """
    Get the transition function for a given transition type.
    
    Args:
        transition_type: The type of transition (TransitionType enum)
        
    Returns:
        Transition function
        
    Raises:
        ValueError: If transition type is unknown
    """
    from .scene import TransitionType
    
    registry = {
        TransitionType.CROSSFADE: crossfade,
        TransitionType.FADE_THROUGH_BLACK: fade_through_black,
        TransitionType.FADE_THROUGH_WHITE: fade_through_white,
        TransitionType.SLIDE_LEFT: slide_left,
        TransitionType.SLIDE_RIGHT: slide_right,
        TransitionType.SLIDE_UP: slide_up,
        TransitionType.SLIDE_DOWN: slide_down,
        TransitionType.PUSH_LEFT: push_left,
        TransitionType.PUSH_RIGHT: push_right,
        TransitionType.PUSH_UP: push_up,
        TransitionType.PUSH_DOWN: push_down,
        TransitionType.WIPE_LEFT: wipe_left,
        TransitionType.WIPE_RIGHT: wipe_right,
        TransitionType.WIPE_UP: wipe_up,
        TransitionType.WIPE_DOWN: wipe_down,
        TransitionType.IRIS_OPEN: iris_open,
        TransitionType.IRIS_CLOSE: iris_close,
        TransitionType.CLOCK_WIPE: clock_wipe,
        TransitionType.DIAMOND_WIPE: diamond_wipe,
        TransitionType.BLINDS_HORIZONTAL: blinds_horizontal,
        TransitionType.BLINDS_VERTICAL: blinds_vertical,
        TransitionType.ZOOM_THROUGH: zoom_through,
        TransitionType.WHIP_PAN: whip_pan,
        TransitionType.PIXELATE: pixelate,
        TransitionType.GLITCH: glitch,
    }
    
    if transition_type not in registry:
        raise ValueError(f"Unknown transition type: {transition_type}")
    
    return registry[transition_type]
