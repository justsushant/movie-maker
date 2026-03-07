"""Easing functions for smooth animation curves."""

from __future__ import annotations

from typing import Callable


# Type alias for easing functions
EasingFunction = Callable[[float], float]


def linear(t: float) -> float:
    """
    Linear interpolation: f(t) = t
    
    No acceleration or deceleration - constant rate of change.
    
    Args:
        t: Progress value in [0.0, 1.0]
        
    Returns:
        Eased progress value in [0.0, 1.0]
    """
    return t


def ease_in_cubic(t: float) -> float:
    """
    Cubic ease-in: f(t) = t³
    
    Starts slow and accelerates. The rate of change increases over time.
    
    Args:
        t: Progress value in [0.0, 1.0]
        
    Returns:
        Eased progress value in [0.0, 1.0]
    """
    return t * t * t


def ease_out_cubic(t: float) -> float:
    """
    Cubic ease-out: f(t) = 1 - (1-t)³
    
    Starts fast and decelerates. The rate of change decreases over time.
    
    Args:
        t: Progress value in [0.0, 1.0]
        
    Returns:
        Eased progress value in [0.0, 1.0]
    """
    return 1 - pow(1 - t, 3)


def ease_in_out_cubic(t: float) -> float:
    """
    Cubic ease-in-out: smooth acceleration and deceleration
    
    Starts slow, accelerates in the middle, then decelerates at the end.
    Creates a smooth, natural-feeling motion.
    
    Formula:
    - For t < 0.5: f(t) = 4t³
    - For t >= 0.5: f(t) = 1 - (-2t + 2)³ / 2
    
    Args:
        t: Progress value in [0.0, 1.0]
        
    Returns:
        Eased progress value in [0.0, 1.0]
    """
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2
