"""
Helper functions for integration tests.

This module contains validation and assertion helpers used by both
real-world scenario tests and technical boundary tests.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from subtitle.layouts import ISubtitleLayout

# Import from config.py file (not config/ package) to avoid naming conflict
_config_spec = importlib.util.spec_from_file_location("config_module", "config.py")
config_py = importlib.util.module_from_spec(_config_spec)
_config_spec.loader.exec_module(config_py)

from subtitle.composer import SubtitleFrameComposer
from subtitle.interfaces import SubtitleLayoutContext
from subtitle.layouts import StackingLayout, SentenceLayout, WordHighlightLayout, WordOnlyLayout
from subtitle.renderer import PillowSubtitleRenderer
from subtitle.source import JsonSubtitleSource
from subtitle.config import SubtitleConfig, SubtitleMode


def _layout_for_mode(mode: SubtitleMode) -> ISubtitleLayout:
    """Get layout instance for a given subtitle mode."""
    if mode == SubtitleMode.SENTENCE:
        return SentenceLayout()
    if mode == SubtitleMode.WORD:
        return WordOnlyLayout()
    if mode == SubtitleMode.STACKING:
        return StackingLayout()
    return WordHighlightLayout()


def validate_subtitle_json_structure(json_path: Path) -> None:
    """
    Validate that subtitle JSON has correct structure.
    
    Checks:
    - Root is a list
    - Each segment has required fields
    - Each word has required fields
    - Timing values are valid
    """
    with open(json_path) as f:
        data = json.load(f)
    
    assert isinstance(data, list), "Root should be a list"
    assert len(data) > 0, "Should have at least one subtitle segment"
    
    for segment in data:
        # Verify segment structure
        assert "sentence_text" in segment, "Segment should have sentence_text"
        assert "start_time" in segment, "Segment should have start_time"
        assert "end_time" in segment, "Segment should have end_time"
        assert "words" in segment, "Segment should have words array"
        
        # Verify types
        assert isinstance(segment["sentence_text"], str)
        assert isinstance(segment["start_time"], (int, float))
        assert isinstance(segment["end_time"], (int, float))
        assert isinstance(segment["words"], list)
        
        # Verify timing is valid
        assert segment["start_time"] >= 0
        assert segment["end_time"] > segment["start_time"]
        
        # Verify word structure
        for word in segment["words"]:
            assert "text" in word, "Word should have text"
            assert "clean_word" in word, "Word should have clean_word"
            assert "start_time" in word, "Word should have start_time"
            assert "end_time" in word, "Word should have end_time"
            
            # Verify types
            assert isinstance(word["text"], str)
            assert isinstance(word["clean_word"], str)
            assert isinstance(word["start_time"], (int, float))
            assert isinstance(word["end_time"], (int, float))
            
            # Verify timing
            assert word["start_time"] >= segment["start_time"]
            assert word["end_time"] <= segment["end_time"]
            assert word["end_time"] > word["start_time"]


def assert_frame_has_subtitle_pixels(cfg: dict, json_path: Path, subtitle_time: float) -> None:
    """
    Assert that a frame contains rendered subtitle pixels (not blank).
    
    Args:
        cfg: Test configuration dictionary
        json_path: Path to subtitle JSON file
        subtitle_time: Timestamp to render
    """
    source = JsonSubtitleSource(json_path)
    subtitle_cfg = SubtitleConfig.from_dict(cfg)
    composer = SubtitleFrameComposer(
        subtitle_source=source,
        layout=_layout_for_mode(subtitle_cfg.mode),
        renderer=PillowSubtitleRenderer(),
        subtitle_config=subtitle_cfg,
        video_settings={
            "width": cfg["width"],
            "height": cfg["height"],
            "bg_color": cfg["bg_color"],
        },
    )

    frame = composer(subtitle_time)
    bg = np.array(cfg["bg_color"], dtype=np.uint8)
    bg_frame = np.broadcast_to(bg, frame.shape)

    # At least some pixels should differ from pure background when subtitle is visible.
    assert np.any(frame != bg_frame), "Frame appears to contain no rendered subtitle pixels"


def assert_no_horizontal_edge_clipping(cfg: dict, json_path: Path, subtitle_time: float) -> None:
    """
    Ensure visible subtitle pixels are not clipped into frame edges.
    
    We treat non-background pixels in first/last column as clipping risk.
    
    Args:
        cfg: Test configuration dictionary
        json_path: Path to subtitle JSON file
        subtitle_time: Timestamp to render
    """
    source = JsonSubtitleSource(json_path)
    subtitle_cfg = SubtitleConfig.from_dict(cfg)
    composer = SubtitleFrameComposer(
        subtitle_source=source,
        layout=_layout_for_mode(subtitle_cfg.mode),
        renderer=PillowSubtitleRenderer(),
        subtitle_config=subtitle_cfg,
        video_settings={
            "width": cfg["width"],
            "height": cfg["height"],
            "bg_color": cfg["bg_color"],
        },
    )
    frame = composer(subtitle_time)
    bg = np.array(cfg["bg_color"], dtype=np.uint8)

    left_edge_diff = np.any(frame[:, 0, :] != bg)
    right_edge_diff = np.any(frame[:, -1, :] != bg)
    assert not left_edge_diff and not right_edge_diff, "Detected subtitle pixels at frame edges"


def assert_sentence_layout_wraps(cfg: dict, json_path: Path, subtitle_time: float) -> None:
    """
    Assert sentence mode creates multiple lines for long-paragraph overflow cases.
    
    Args:
        cfg: Test configuration dictionary
        json_path: Path to subtitle JSON file
        subtitle_time: Timestamp to render
    """
    subtitle_cfg = SubtitleConfig.from_dict(cfg)
    context = SubtitleLayoutContext.from_config(cfg["width"], cfg["height"], subtitle_cfg)
    source = JsonSubtitleSource(json_path)
    segments = source.get_segments_for_time(subtitle_time)
    laid_out = SentenceLayout().layout_frame(subtitle_time, segments, context, subtitle_cfg)
    assert len(laid_out) >= 2, "Expected wrapped multi-line sentence layout for long paragraph"


def assert_single_line_layout(cfg: dict, json_path: Path, subtitle_time: float) -> None:
    """
    Assert sentence mode produces at most one PositionedSubtitle (single-line chunking).
    
    Args:
        cfg: Test configuration dictionary
        json_path: Path to subtitle JSON file
        subtitle_time: Timestamp to render
    """
    subtitle_cfg = SubtitleConfig.from_dict(cfg)
    context = SubtitleLayoutContext.from_config(cfg["width"], cfg["height"], subtitle_cfg)
    source = JsonSubtitleSource(json_path)
    segments = source.get_segments_for_time(subtitle_time)
    laid_out = SentenceLayout().layout_frame(subtitle_time, segments, context, subtitle_cfg)
    assert len(laid_out) <= 1, (
        f"Expected single-line layout (multiline disabled), got {len(laid_out)} lines"
    )


def get_integration_test_config(
    case_id: str,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    subtitle_config: dict | None = None,
    test_suite: str = "test_real_world_scenarios"
) -> dict:
    """
    Create test configuration for integration tests.
    
    Uses existing config.py infrastructure but with test-specific defaults.
    Organizes output into test suite subdirectories.
    
    Args:
        case_id: Unique identifier for this test case
        width: Video width in pixels
        height: Video height in pixels
        fps: Frames per second
        subtitle_config: Subtitle configuration dictionary
        test_suite: Test suite name (test_real_world_scenarios or test_technical_boundaries)
    
    Returns:
        Complete configuration dictionary for test
    """
    # Prepend test suite name to case_id for organized output
    full_case_id = f"{test_suite}/{case_id}"
    
    overrides = {
        "width": width,
        "height": height,
        "fps": fps,
        "bg_color": (0, 0, 0),
        "text_color": (255, 255, 255),
        "highlight_color": (255, 255, 0),
    }
    
    if subtitle_config:
        overrides["subtitle"] = subtitle_config
    
    return config_py.get_test_config(case_id=full_case_id, overrides=overrides)


def run_pipeline(cfg: dict) -> None:
    """
    Run the video generation pipeline using the library API.
    
    This is a compatibility wrapper that converts the old config dict format
    to the new library API calls.
    
    Args:
        cfg: Configuration dictionary with keys:
            - input_text: Path to input text file
            - run_dir: Output directory path
            - width, height, fps, bg_color: Video settings
            - subtitle: Subtitle configuration dict
    """
    from pathlib import Path
    from api.library import generate_video_from_file
    from tts.config import TTSConfig
    from config.video_config import VideoConfig
    
    input_file = Path(cfg["input_text"])
    output_dir = Path(cfg["run_dir"])
    
    # Extract subtitle config
    subtitle_dict = cfg.get("subtitle", {})
    subtitle_config = SubtitleConfig.from_dict({"subtitle": subtitle_dict})
    
    # Create config objects
    tts_config = TTSConfig()  # Use defaults
    video_config = VideoConfig(
        width=cfg.get("width", 1920),
        height=cfg.get("height", 1080),
        fps=cfg.get("fps", 30),
        bg_color=cfg.get("bg_color", (0, 0, 0))
    )
    
    # Generate video
    generate_video_from_file(
        input_file=input_file,
        output_dir=output_dir,
        tts_config=tts_config,
        video_config=video_config,
        subtitle_config=subtitle_config
    )
