"""
Real-world scenario integration tests for PRISM.

These tests validate the complete pipeline with realistic content creator scripts.
Each test represents an actual use case and uses appropriate configuration for
that content type.

Validation approach:
- Automated: Files exist, structure valid, no crashes
- Manual: Developer reviews output videos for quality

Output location: output/test_real_world_scenarios/
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
    get_integration_test_config,
    run_pipeline
)

from tests.integration.helpers import get_integration_test_config, validate_subtitle_json_structure


def test_educational_explainer(real_world_fixture_dir: Path, real_world_output_dir: Path) -> None:
    """
    Test educational content with technical terms and moderate pacing.
    
    Content: Machine learning fundamentals explanation
    Config: 1080p landscape, sentence_with_word_highlight mode
    
    Manual review checklist:
    - Technical terms are readable
    - Pacing allows comprehension
    - Word highlighting is clear
    """
    input_file = real_world_fixture_dir / "educational_explainer.txt"
    output_dir = real_world_output_dir / "educational_explainer"
    
    cfg = get_integration_test_config(
        case_id="educational_explainer",
        width=1920,
        height=1080,
        fps=30,
        subtitle_config={
            "mode": "sentence_with_word_highlight",
            "vertical_align": "bottom",
            "font_size": 48
        },
        test_suite="test_real_world_scenarios"
    )
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists(), "Video file should be created"
    assert Path(cfg["audio_file"]).exists(), "Audio file should be created"
    assert Path(cfg["json_file"]).exists(), "Subtitle JSON should be created"
    
    # Verify files are not empty
    assert Path(cfg["output_video"]).stat().st_size > 0, "Video file should not be empty"
    assert Path(cfg["audio_file"]).stat().st_size > 0, "Audio file should not be empty"
    
    # Validate subtitle JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))
    
    # Verify we have subtitle segments
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0, "Should have at least one subtitle segment"


def test_product_demo(real_world_fixture_dir: Path, real_world_output_dir: Path) -> None:
    """
    Test product demo with marketing language and calls to action.
    
    Content: SmartHome Hub product demonstration
    Config: 1080p landscape, sentence_with_word_highlight mode
    
    Manual review checklist:
    - Marketing language is engaging
    - Calls to action are prominent
    - Professional appearance
    """
    input_file = real_world_fixture_dir / "product_demo.txt"
    output_dir = real_world_output_dir / "product_demo"
    
    cfg = get_integration_test_config(
        case_id="product_demo",
        width=1920,
        height=1080,
        fps=30,
        subtitle_config={
            "mode": "sentence_with_word_highlight",
            "vertical_align": "bottom",
            "font_size": 52
        },
        test_suite="test_real_world_scenarios"
    )
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists(), "Video file should be created"
    assert Path(cfg["audio_file"]).exists(), "Audio file should be created"
    assert Path(cfg["json_file"]).exists(), "Subtitle JSON should be created"
    
    # Verify files are not empty
    assert Path(cfg["output_video"]).stat().st_size > 0, "Video file should not be empty"
    
    # Validate subtitle JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))
    
    # Verify we have subtitle segments
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0, "Should have at least one subtitle segment"


def test_story_narration(real_world_fixture_dir: Path, real_world_output_dir: Path) -> None:
    """
    Test story narration with dialogue and emotional variation.
    
    Content: Lighthouse story with dialogue
    Config: 1080p landscape, sentence mode
    
    Manual review checklist:
    - Dialogue is clear and readable
    - Emotional pacing feels natural
    - Sentence mode works well for narrative
    """
    input_file = real_world_fixture_dir / "story_narration.txt"
    output_dir = real_world_output_dir / "story_narration"
    
    cfg = get_integration_test_config(
        case_id="story_narration",
        width=1920,
        height=1080,
        fps=30,
        subtitle_config={
            "mode": "sentence",
            "vertical_align": "bottom",
            "font_size": 48
        },
        test_suite="test_real_world_scenarios"
    )
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists(), "Video file should be created"
    assert Path(cfg["audio_file"]).exists(), "Audio file should be created"
    assert Path(cfg["json_file"]).exists(), "Subtitle JSON should be created"
    
    # Verify files are not empty
    assert Path(cfg["output_video"]).stat().st_size > 0, "Video file should not be empty"
    
    # Validate subtitle JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))
    
    # Verify we have subtitle segments
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0, "Should have at least one subtitle segment"


def test_tutorial_walkthrough(real_world_fixture_dir: Path, real_world_output_dir: Path) -> None:
    """
    Test tutorial with step-by-step instructions.
    
    Content: Development environment setup tutorial
    Config: 720p landscape, sentence_with_word_highlight mode
    
    Manual review checklist:
    - Instructions are clear and easy to follow
    - Technical commands are readable
    - Pacing allows note-taking
    """
    input_file = real_world_fixture_dir / "tutorial_walkthrough.txt"
    output_dir = real_world_output_dir / "tutorial_walkthrough"
    
    cfg = get_integration_test_config(
        case_id="tutorial_walkthrough",
        width=1280,
        height=720,
        fps=30,
        subtitle_config={
            "mode": "sentence_with_word_highlight",
            "vertical_align": "bottom",
            "font_size": 42
        },
        test_suite="test_real_world_scenarios"
    )
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists(), "Video file should be created"
    assert Path(cfg["audio_file"]).exists(), "Audio file should be created"
    assert Path(cfg["json_file"]).exists(), "Subtitle JSON should be created"
    
    # Verify files are not empty
    assert Path(cfg["output_video"]).stat().st_size > 0, "Video file should not be empty"
    
    # Validate subtitle JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))
    
    # Verify we have subtitle segments
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0, "Should have at least one subtitle segment"


def test_news_announcement(real_world_fixture_dir: Path, real_world_output_dir: Path) -> None:
    """
    Test news announcement with formal, concise language.
    
    Content: Technology sector regulatory announcement
    Config: 1080p landscape, sentence mode
    
    Manual review checklist:
    - Formal tone is maintained
    - Information is clear and concise
    - Professional appearance
    """
    input_file = real_world_fixture_dir / "news_announcement.txt"
    output_dir = real_world_output_dir / "news_announcement"
    
    cfg = get_integration_test_config(
        case_id="news_announcement",
        width=1920,
        height=1080,
        fps=30,
        subtitle_config={
            "mode": "sentence",
            "vertical_align": "bottom",
            "font_size": 48
        },
        test_suite="test_real_world_scenarios"
    )
    
    cfg["input_text"] = str(input_file)
    run_pipeline(cfg)
    
    # Verify output files exist
    assert Path(cfg["output_video"]).exists(), "Video file should be created"
    assert Path(cfg["audio_file"]).exists(), "Audio file should be created"
    assert Path(cfg["json_file"]).exists(), "Subtitle JSON should be created"
    
    # Verify files are not empty
    assert Path(cfg["output_video"]).stat().st_size > 0, "Video file should not be empty"
    
    # Validate subtitle JSON structure
    validate_subtitle_json_structure(Path(cfg["json_file"]))
    
    # Verify we have subtitle segments
    source = JsonSubtitleSource(Path(cfg["json_file"]))
    segments = source.get_all_segments()
    assert len(segments) > 0, "Should have at least one subtitle segment"
