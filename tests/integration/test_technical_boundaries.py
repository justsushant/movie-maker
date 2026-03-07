"""
Technical boundary integration tests for KokoroMoviePy.

These tests validate algorithm correctness at edge cases and boundary conditions.
Each test focuses on a specific technical aspect with automated assertions.

Validation approach:
- Automated assertions for all tests
- Pixel-level checks where appropriate
- Layout correctness validation
- No manual review required

Output location: output/test_technical_boundaries/
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from api.library import generate_video_from_file
from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle.config import SubtitleConfig, SubtitleMode
from subtitle.source import JsonSubtitleSource
from tests.integration.helpers import (
    validate_subtitle_json_structure,
    assert_frame_has_subtitle_pixels,
    assert_no_horizontal_edge_clipping,
    assert_sentence_layout_wraps,
    assert_single_line_layout,
    get_integration_test_config,
    run_pipeline
)

from tests.integration.helpers import (
    assert_frame_has_subtitle_pixels,
    assert_no_horizontal_edge_clipping,
    assert_sentence_layout_wraps,
    assert_single_line_layout,
    get_integration_test_config,
    validate_subtitle_json_structure,
)


def test_multiline_wrapping_narrow_width(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Test that long text wraps correctly in narrow portrait layouts.
    
    Validates:
    - SentenceLayout creates multiple lines
    - No horizontal edge clipping
    - Text remains readable
    """
    input_file = technical_fixture_dir / "multiline_wrap_test.txt"
    output_dir = technical_output_dir / "multiline_wrapping"
    
    cfg = get_integration_test_config(
        case_id="multiline_wrapping",
        width=720,
        height=1280,  # Portrait
        subtitle_config={
            "mode": "sentence",
            "multiline_enabled": True,
            "vertical_align": "bottom"
        },
        test_suite="test_technical_boundaries"
    )
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Validate JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))
    
    # Get visible time for assertions
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0
    visible_time = (segments[0].start_time + segments[0].end_time) / 2.0
    
    # Assert multiline wrapping occurred
    assert_sentence_layout_wraps(cfg, Path(cfg["json_file"]), visible_time)
    
    # Assert no edge clipping
    assert_no_horizontal_edge_clipping(cfg, Path(cfg["json_file"]), visible_time)


def test_single_line_truncation(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Test that long text stays on single line when multiline is disabled.
    
    Validates:
    - SentenceLayout produces single line
    - No horizontal edge clipping (text should be truncated/chunked)
    """
    input_file = technical_fixture_dir / "multiline_wrap_test.txt"
    output_dir = technical_output_dir / "single_line_truncation"
    
    cfg = get_integration_test_config(
        case_id="single_line_truncation",
        width=720,
        height=1280,  # Portrait
        subtitle_config={
            "mode": "sentence",
            "multiline_enabled": False,
            "vertical_align": "bottom"
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Validate JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))
    
    # Get visible time for assertions
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0
    visible_time = (segments[0].start_time + segments[0].end_time) / 2.0
    
    # Assert single line layout
    assert_single_line_layout(cfg, Path(cfg["json_file"]), visible_time)
    
    # Assert no edge clipping
    assert_no_horizontal_edge_clipping(cfg, Path(cfg["json_file"]), visible_time)


def test_stacking_overflow(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Test stacking mode with more content than max_visible_lines.
    
    Validates:
    - Pipeline completes without errors
    - Stacking mode handles overflow gracefully
    """
    input_file = technical_fixture_dir / "multiline_wrap_test.txt"
    output_dir = technical_output_dir / "stacking_overflow"
    
    cfg = get_integration_test_config(
        case_id="stacking_overflow",
        width=1920,
        height=1080,
        subtitle_config={
            "mode": "stacking",
            "stacking": {
                "max_visible_lines": 2,
                "direction": "up"
            },
            "vertical_align": "bottom"
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Validate JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))
    
    # Verify we have subtitle segments
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0


def test_no_clipping_portrait_narrow(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Ensure text doesn't touch edges in narrow portrait layout (720x1280).
    
    Validates:
    - No pixels at left/right edges
    - Subtitle is rendered
    """
    input_file = technical_fixture_dir / "multiline_wrap_test.txt"
    output_dir = technical_output_dir / "no_clipping_portrait"
    
    cfg = get_integration_test_config(
        case_id="no_clipping_portrait",
        width=720,
        height=1280,
        subtitle_config={
            "mode": "sentence",
            "multiline_enabled": True,
            "vertical_align": "bottom"
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Get visible time for assertions
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0
    visible_time = (segments[0].start_time + segments[0].end_time) / 2.0
    
    # Assert no edge clipping
    assert_no_horizontal_edge_clipping(cfg, Path(cfg["json_file"]), visible_time)
    
    # Assert subtitle is rendered
    assert_frame_has_subtitle_pixels(cfg, Path(cfg["json_file"]), visible_time)


def test_no_clipping_landscape_wide(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Ensure text doesn't touch edges in wide landscape layout (1920x1080).
    
    Validates:
    - No pixels at left/right edges
    - Subtitle is rendered
    """
    input_file = technical_fixture_dir / "multiline_wrap_test.txt"
    output_dir = technical_output_dir / "no_clipping_landscape"
    
    cfg = get_integration_test_config(
        case_id="no_clipping_landscape",
        width=1920,
        height=1080,
        subtitle_config={
            "mode": "sentence",
            "vertical_align": "bottom"
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Get visible time for assertions
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0
    visible_time = (segments[0].start_time + segments[0].end_time) / 2.0
    
    # Assert no edge clipping
    assert_no_horizontal_edge_clipping(cfg, Path(cfg["json_file"]), visible_time)
    
    # Assert subtitle is rendered
    assert_frame_has_subtitle_pixels(cfg, Path(cfg["json_file"]), visible_time)


def test_unicode_rendering(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Test rendering of unicode characters (emoji, accented chars, CJK).
    
    Validates:
    - Pipeline completes without errors
    - Subtitle JSON is created
    - Output video is generated
    """
    input_file = technical_fixture_dir / "unicode_stress.txt"
    output_dir = technical_output_dir / "unicode_rendering"
    
    cfg = get_integration_test_config(
        case_id="unicode_rendering",
        width=1920,
        height=1080,
        subtitle_config={
            "mode": "sentence",
            "vertical_align": "center"
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Validate JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))
    
    # Verify we have subtitle segments
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0


def test_punctuation_heavy(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Test handling of heavy punctuation (quotes, dashes, multiple marks).
    
    Validates:
    - Pipeline completes without errors
    - Punctuation is merged into words
    - Subtitle JSON is valid
    """
    input_file = technical_fixture_dir / "punctuation_heavy.txt"
    output_dir = technical_output_dir / "punctuation_heavy"
    
    cfg = get_integration_test_config(
        case_id="punctuation_heavy",
        width=1920,
        height=1080,
        subtitle_config={
            "mode": "sentence_with_word_highlight",
            "vertical_align": "bottom"
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Validate JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))
    
    # Verify we have subtitle segments
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0
    
    # Check that punctuation is merged into words (not standalone)
    all_words = []
    for segment in segments:
        all_words.extend([w.text for w in segment.words])
    
    # At least some words should have punctuation attached
    words_with_punct = [w for w in all_words if any(p in w for p in "!?,.;:\"'()—")]
    assert len(words_with_punct) > 0, "Punctuation should be merged into words"


def test_ultra_wide_4k(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Test extreme aspect ratio: 4K ultra-wide (3840x2160).
    
    Validates:
    - Pipeline handles high resolution
    - No edge clipping
    - Subtitle is rendered
    """
    input_file = technical_fixture_dir / "multiline_wrap_test.txt"
    output_dir = technical_output_dir / "ultra_wide_4k"
    
    cfg = get_integration_test_config(
        case_id="ultra_wide_4k",
        width=3840,
        height=2160,
        subtitle_config={
            "mode": "sentence",
            "vertical_align": "bottom",
            "font_size": 72
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Get visible time for assertions
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0
    visible_time = (segments[0].start_time + segments[0].end_time) / 2.0
    
    # Assert no edge clipping
    assert_no_horizontal_edge_clipping(cfg, Path(cfg["json_file"]), visible_time)


def test_portrait_phone(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Test extreme aspect ratio: Portrait phone (720x1280).
    
    Validates:
    - Pipeline handles portrait orientation
    - Multiline wrapping works
    - No edge clipping
    """
    input_file = technical_fixture_dir / "multiline_wrap_test.txt"
    output_dir = technical_output_dir / "portrait_phone"
    
    cfg = get_integration_test_config(
        case_id="portrait_phone",
        width=720,
        height=1280,
        subtitle_config={
            "mode": "sentence",
            "multiline_enabled": True,
            "vertical_align": "bottom"
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Get visible time for assertions
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0
    visible_time = (segments[0].start_time + segments[0].end_time) / 2.0
    
    # Assert multiline wrapping
    assert_sentence_layout_wraps(cfg, Path(cfg["json_file"]), visible_time)
    
    # Assert no edge clipping
    assert_no_horizontal_edge_clipping(cfg, Path(cfg["json_file"]), visible_time)


def test_square_format(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Test square aspect ratio (1080x1080).
    
    Validates:
    - Pipeline handles square format
    - Subtitle is rendered
    """
    input_file = technical_fixture_dir / "multiline_wrap_test.txt"
    output_dir = technical_output_dir / "square_format"
    
    cfg = get_integration_test_config(
        case_id="square_format",
        width=1080,
        height=1080,
        subtitle_config={
            "mode": "sentence",
            "vertical_align": "bottom"
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Get visible time for assertions
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0
    visible_time = (segments[0].start_time + segments[0].end_time) / 2.0
    
    # Assert subtitle is rendered
    assert_frame_has_subtitle_pixels(cfg, Path(cfg["json_file"]), visible_time)


def test_word_only_mode(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Test word-only subtitle mode (single word display).
    
    Validates:
    - Pipeline completes with word mode
    - Subtitle is rendered
    """
    input_file = technical_fixture_dir / "single_word.txt"
    output_dir = technical_output_dir / "word_only_mode"
    
    cfg = get_integration_test_config(
        case_id="word_only_mode",
        width=1920,
        height=1080,
        subtitle_config={
            "mode": "word",
            "vertical_align": "center"
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Validate JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))
    
    # Get visible time for assertions
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0
    visible_time = (segments[0].start_time + segments[0].end_time) / 2.0
    
    # Assert subtitle is rendered
    assert_frame_has_subtitle_pixels(cfg, Path(cfg["json_file"]), visible_time)


def test_stacking_mode_direction_up(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Test stacking mode with upward direction.
    
    Validates:
    - Pipeline completes with stacking mode
    - Upward direction works correctly
    """
    input_file = technical_fixture_dir / "multiline_wrap_test.txt"
    output_dir = technical_output_dir / "stacking_direction_up"
    
    cfg = get_integration_test_config(
        case_id="stacking_direction_up",
        width=1920,
        height=1080,
        subtitle_config={
            "mode": "stacking",
            "stacking": {
                "max_visible_lines": 3,
                "direction": "up"
            },
            "vertical_align": "bottom"
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Validate JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))


def test_sentence_highlight_mode(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Test sentence with word highlighting mode.
    
    Validates:
    - Pipeline completes with highlight mode
    - Subtitle is rendered
    """
    input_file = technical_fixture_dir / "multiline_wrap_test.txt"
    output_dir = technical_output_dir / "sentence_highlight"
    
    cfg = get_integration_test_config(
        case_id="sentence_highlight",
        width=1920,
        height=1080,
        subtitle_config={
            "mode": "sentence_with_word_highlight",
            "vertical_align": "bottom"
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Get visible time for assertions
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0
    visible_time = (segments[0].start_time + segments[0].end_time) / 2.0
    
    # Assert subtitle is rendered
    assert_frame_has_subtitle_pixels(cfg, Path(cfg["json_file"]), visible_time)


def test_single_word_input(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Test minimal input: single word.
    
    Validates:
    - Pipeline handles minimal input
    - Subtitle is rendered
    """
    input_file = technical_fixture_dir / "single_word.txt"
    output_dir = technical_output_dir / "single_word_input"
    
    cfg = get_integration_test_config(
        case_id="single_word_input",
        width=1920,
        height=1080,
        subtitle_config={
            "mode": "sentence",
            "vertical_align": "center"
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Validate JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))
    
    # Get visible time for assertions
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0
    visible_time = (segments[0].start_time + segments[0].end_time) / 2.0
    
    # Assert subtitle is rendered
    assert_frame_has_subtitle_pixels(cfg, Path(cfg["json_file"]), visible_time)


def test_very_long_word(
    technical_fixture_dir: Path, technical_output_dir: Path
) -> None:
    """
    Test word longer than typical line width.
    
    Validates:
    - Pipeline handles very long words
    - No edge clipping (word should fit or be handled gracefully)
    """
    input_file = technical_fixture_dir / "extreme_long_word.txt"
    output_dir = technical_output_dir / "very_long_word"
    
    cfg = get_integration_test_config(
        case_id="very_long_word",
        width=1920,
        height=1080,
        subtitle_config={
            "mode": "sentence",
            "vertical_align": "center"
        }
    , test_suite="test_technical_boundaries")
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists()
    assert Path(cfg["json_file"]).exists()
    
    # Validate JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))
    
    # Get visible time for assertions
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0
    visible_time = (segments[0].start_time + segments[0].end_time) / 2.0
    
    # Assert subtitle is rendered
    assert_frame_has_subtitle_pixels(cfg, Path(cfg["json_file"]), visible_time)
