"""Tests for text overlay effect."""

from __future__ import annotations

import numpy as np
import pytest

from engine.effects import text_overlay


def test_text_overlay_basic():
    """Test basic text overlay functionality."""
    frame = np.ones((100, 200, 3), dtype=np.uint8) * 128
    
    effect = text_overlay("Test", position=(10, 10))
    result = effect(frame, t=0.5, progress=0.5)
    
    # Verify shape and dtype preserved
    assert result.shape == frame.shape
    assert result.dtype == np.uint8
    
    # Verify frame was modified (text was added)
    assert not np.array_equal(result, frame)


def test_text_overlay_preserves_dimensions():
    """Test that text overlay preserves frame dimensions."""
    for height in [50, 100, 480, 1080]:
        for width in [50, 100, 640, 1920]:
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            effect = text_overlay("Test")
            result = effect(frame, t=0.0, progress=0.0)
            
            assert result.shape == (height, width, 3)
            assert result.dtype == np.uint8


def test_text_overlay_with_background():
    """Test text overlay with background."""
    frame = np.ones((100, 200, 3), dtype=np.uint8) * 128
    
    effect = text_overlay(
        "Test",
        position=(10, 10),
        bg_color=(0, 0, 0),
        bg_opacity=0.8
    )
    result = effect(frame, t=0.5, progress=0.5)
    
    assert result.shape == frame.shape
    assert result.dtype == np.uint8


def test_text_overlay_without_background():
    """Test text overlay without background."""
    frame = np.ones((100, 200, 3), dtype=np.uint8) * 128
    
    effect = text_overlay(
        "Test",
        position=(10, 10),
        bg_color=None
    )
    result = effect(frame, t=0.5, progress=0.5)
    
    assert result.shape == frame.shape
    assert result.dtype == np.uint8


def test_text_overlay_custom_color():
    """Test text overlay with custom color."""
    frame = np.zeros((100, 200, 3), dtype=np.uint8)
    
    effect = text_overlay(
        "Test",
        position=(10, 10),
        color=(255, 0, 0),  # Red text
        bg_color=None
    )
    result = effect(frame, t=0.5, progress=0.5)
    
    assert result.shape == frame.shape
    assert result.dtype == np.uint8
    
    # Verify some red pixels were added
    assert np.any(result[:, :, 0] > 0)


def test_text_overlay_different_positions():
    """Test text overlay at different positions."""
    frame = np.ones((200, 300, 3), dtype=np.uint8) * 128
    
    positions = [(10, 10), (50, 50), (100, 100), (150, 150)]
    
    for pos in positions:
        effect = text_overlay("Test", position=pos)
        result = effect(frame, t=0.5, progress=0.5)
        
        assert result.shape == frame.shape
        assert result.dtype == np.uint8


def test_text_overlay_different_font_scales():
    """Test text overlay with different font scales."""
    frame = np.ones((200, 300, 3), dtype=np.uint8) * 128
    
    for scale in [0.5, 1.0, 1.5, 2.0]:
        effect = text_overlay("Test", font_scale=scale)
        result = effect(frame, t=0.5, progress=0.5)
        
        assert result.shape == frame.shape
        assert result.dtype == np.uint8


def test_text_overlay_long_text():
    """Test text overlay with long text."""
    frame = np.ones((200, 400, 3), dtype=np.uint8) * 128
    
    effect = text_overlay("This is a longer text string")
    result = effect(frame, t=0.5, progress=0.5)
    
    assert result.shape == frame.shape
    assert result.dtype == np.uint8


def test_text_overlay_multiline_not_supported():
    """Test that text overlay handles newlines (as single line)."""
    frame = np.ones((200, 300, 3), dtype=np.uint8) * 128
    
    # OpenCV putText doesn't support multiline, so newlines are treated as part of text
    effect = text_overlay("Line 1\nLine 2")
    result = effect(frame, t=0.5, progress=0.5)
    
    assert result.shape == frame.shape
    assert result.dtype == np.uint8


def test_text_overlay_edge_position():
    """Test text overlay at edge positions."""
    frame = np.ones((100, 200, 3), dtype=np.uint8) * 128
    
    # Near edges
    edge_positions = [(0, 0), (190, 0), (0, 90), (190, 90)]
    
    for pos in edge_positions:
        effect = text_overlay("Test", position=pos, padding=5)
        result = effect(frame, t=0.5, progress=0.5)
        
        assert result.shape == frame.shape
        assert result.dtype == np.uint8


def test_text_overlay_with_padding():
    """Test text overlay with different padding values."""
    frame = np.ones((200, 300, 3), dtype=np.uint8) * 128
    
    for padding in [0, 5, 10, 20]:
        effect = text_overlay("Test", padding=padding, bg_color=(0, 0, 0))
        result = effect(frame, t=0.5, progress=0.5)
        
        assert result.shape == frame.shape
        assert result.dtype == np.uint8


def test_text_overlay_clamping():
    """Test that text overlay clamps values to [0, 255]."""
    frame = np.ones((100, 200, 3), dtype=np.uint8) * 255
    
    effect = text_overlay("Test", color=(255, 255, 255))
    result = effect(frame, t=0.5, progress=0.5)
    
    assert np.all(result >= 0)
    assert np.all(result <= 255)
    assert result.dtype == np.uint8
