"""Video rendering: compositing subtitle frames over audio."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from moviepy import AudioFileClip, VideoClip

from subtitle.config import SubtitleConfig, SubtitleMode
from subtitle.composer import SubtitleFrameComposer
from subtitle.interfaces import ISubtitleLayout, ISubtitleRenderer, ISubtitleSource
from subtitle.layouts import StackingLayout, SentenceLayout, WordHighlightLayout, WordOnlyLayout
from subtitle.renderer import PillowSubtitleRenderer
from subtitle.source import JsonSubtitleSource


def load_data(json_file: str) -> list:
    """Loads the hierarchical subtitle JSON from the given path (legacy helper)."""
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def _layout_for_mode(mode: SubtitleMode):
    if mode == SubtitleMode.SENTENCE:
        return SentenceLayout()
    if mode == SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT:
        return WordHighlightLayout()
    if mode == SubtitleMode.WORD:
        return WordOnlyLayout()
    if mode == SubtitleMode.STACKING:
        return StackingLayout()
    return WordHighlightLayout()


def create_video(
    config: Dict[str, Any],
    *,
    subtitle_source: Optional[ISubtitleSource] = None,
    layout: Optional[ISubtitleLayout] = None,
    renderer: Optional[ISubtitleRenderer] = None,
) -> None:
    """
    Renders the final video by compositing subtitle frames over audio.

    Uses the modular subtitle pipeline. Optionally pass custom subtitle_source,
    layout, or renderer; otherwise they are built from config.
    """
    json_file = config["json_file"]
    audio_file = config["audio_file"]
    output_video = config["output_video"]
    fps = config["fps"]

    print("Loading data and audio...")
    subtitle_config = SubtitleConfig.from_dict(config)
    source = subtitle_source or JsonSubtitleSource(json_file)
    source.get_all_segments()

    audio_clip = AudioFileClip(audio_file)
    duration = audio_clip.duration
    all_segments = source.get_all_segments()
    max_end_time = all_segments[-1].end_time if all_segments else 0
    final_duration = max(duration, max_end_time)
    print(f"Video duration: {final_duration:.2f} seconds")

    layout_impl = layout or _layout_for_mode(subtitle_config.mode)
    renderer_impl = renderer or PillowSubtitleRenderer()
    video_settings = {
        "width": config["width"],
        "height": config["height"],
        "bg_color": config["bg_color"],
    }
    composer = SubtitleFrameComposer(
        subtitle_source=source,
        layout=layout_impl,
        renderer=renderer_impl,
        subtitle_config=subtitle_config,
        video_settings=video_settings,
    )

    print("Generating frames...")
    video_clip = VideoClip(
        lambda t: composer(t),
        duration=final_duration,
    )
    video_clip = video_clip.with_audio(audio_clip)

    print(f"Exporting to {output_video}...")
    video_clip.write_videofile(output_video, fps=fps, codec="libx264", audio_codec="aac")
    print("Export complete!")
