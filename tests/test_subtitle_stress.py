from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

from config import get_test_config
from main import run_pipeline
from subtitle.composer import SubtitleFrameComposer
from subtitle.interfaces import SubtitleLayoutContext
from subtitle.layouts import RollingLayout, SentenceLayout, WordHighlightLayout, WordOnlyLayout
from subtitle.renderer import PillowSubtitleRenderer
from subtitle.source import JsonSubtitleSource
from subtitle_config import SubtitleConfig, SubtitleMode


def _layout_for_mode(mode: SubtitleMode):
    if mode == SubtitleMode.SENTENCE:
        return SentenceLayout()
    if mode == SubtitleMode.WORD:
        return WordOnlyLayout()
    if mode == SubtitleMode.ROLLING:
        return RollingLayout()
    return WordHighlightLayout()


def _assert_frame_has_subtitle_pixels(cfg: dict, json_path: Path, subtitle_time: float) -> None:
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


def _assert_no_horizontal_edge_clipping(cfg: dict, json_path: Path, subtitle_time: float) -> None:
    """
    Ensure visible subtitle pixels are not clipped into frame edges.
    We treat non-background pixels in first/last column as clipping risk.
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


def _assert_sentence_layout_wraps(cfg: dict, json_path: Path, subtitle_time: float) -> None:
    """Assert sentence mode creates multiple lines for long-paragraph overflow cases."""
    subtitle_cfg = SubtitleConfig.from_dict(cfg)
    context = SubtitleLayoutContext.from_config(cfg["width"], cfg["height"], subtitle_cfg)
    source = JsonSubtitleSource(json_path)
    segments = source.get_segments_for_time(subtitle_time)
    laid_out = SentenceLayout().layout_frame(subtitle_time, segments, context, subtitle_cfg)
    assert len(laid_out) >= 2, "Expected wrapped multi-line sentence layout for long paragraph"


TEXT_CASES = [
    "short_single_sentence.txt",
    "long_paragraph.txt",
    "multi_paragraph.txt",
    "punctuation_heavy.txt",
    "unicode_sample.txt",
    "single_word.txt",
]

VIDEO_VARIANTS = [
    {
        "id": "1080_sentence_highlight",
        "width": 1920,
        "height": 1080,
        "subtitle": {"mode": "sentence_with_word_highlight"},
    },
    {
        "id": "720_sentence",
        "width": 1280,
        "height": 720,
        "subtitle": {"mode": "sentence", "vertical_align": "bottom"},
    },
    {
        "id": "1080_word",
        "width": 1920,
        "height": 1080,
        "subtitle": {"mode": "word", "vertical_align": "center"},
    },
    {
        "id": "1080_rolling",
        "width": 1920,
        "height": 1080,
        "subtitle": {
            "mode": "rolling",
            "rolling": {"max_visible_lines": 3, "direction": "up"},
        },
    },
    {
        "id": "phone_720x1280_sentence",
        "width": 720,
        "height": 1280,
        "subtitle": {"mode": "sentence", "vertical_align": "bottom"},
    },
    {
        "id": "phone_1080x1920_sentence_highlight",
        "width": 1080,
        "height": 1920,
        "subtitle": {"mode": "sentence_with_word_highlight", "vertical_align": "bottom"},
    },
]


@pytest.mark.parametrize("text_filename", TEXT_CASES)
@pytest.mark.parametrize("variant", VIDEO_VARIANTS, ids=[v["id"] for v in VIDEO_VARIANTS])
def test_subtitle_stress_rendering(
    fixture_text_dir: Path,
    text_filename: str,
    variant: dict,
) -> None:
    text_path = fixture_text_dir / text_filename

    case_id = f"{Path(text_filename).stem}_{variant['id']}"
    cfg = get_test_config(
        case_id=case_id,
        overrides={
            "width": variant["width"],
            "height": variant["height"],
            "fps": 24,
            "bg_color": (0, 0, 0),
            "text_color": (255, 255, 255),
            "highlight_color": (255, 255, 0),
            "subtitle": variant["subtitle"],
        },
    )

    case_dir = Path(cfg["run_dir"])
    cfg["input_text"] = str(text_path)
    run_pipeline(cfg)

    assert str(case_dir).startswith(os.path.join("output", "test"))
    assert Path(cfg["audio_file"]).exists(), "Expected output WAV file to be created"
    assert Path(cfg["json_file"]).exists(), "Expected output subtitle JSON to be created"
    assert Path(cfg["output_video"]).exists(), "Expected output video file to be created"
    assert Path(cfg["audio_file"]).stat().st_size > 0, "Output WAV file is empty"
    assert Path(cfg["output_video"]).stat().st_size > 0, "Output video file is empty"

    segments = JsonSubtitleSource(Path(cfg["json_file"])).get_all_segments()
    assert segments, "Expected subtitle segments from Kokoro extractor"
    visible_time = (segments[0].start_time + segments[0].end_time) / 2.0
    _assert_frame_has_subtitle_pixels(cfg, Path(cfg["json_file"]), visible_time)

    is_long_sentence_case = text_filename == "long_paragraph.txt" and variant["id"] in {
        "720_sentence",
        "phone_720x1280_sentence",
    }
    if is_long_sentence_case:
        _assert_sentence_layout_wraps(cfg, Path(cfg["json_file"]), visible_time)
        _assert_no_horizontal_edge_clipping(cfg, Path(cfg["json_file"]), visible_time)
