"""Video rendering: compositing subtitle frames over audio."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, TYPE_CHECKING

import numpy as np
from moviepy import AudioFileClip, VideoClip
from PIL import Image

from subtitle.config import SubtitleConfig, SubtitleMode
from subtitle.composer import SubtitleFrameComposer
from subtitle.interfaces import ISubtitleLayout, ISubtitleRenderer, ISubtitleSource, SubtitleLayoutContext
from subtitle.layouts import StackingLayout, SentenceLayout, WordHighlightLayout, WordOnlyLayout
from subtitle.renderer import PillowSubtitleRenderer
from subtitle.source import JsonSubtitleSource

if TYPE_CHECKING:
    from engine.scene import Scene


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
    scene: Optional['Scene'] = None,
) -> None:
    """
    Renders the final video by compositing subtitle frames over audio.

    Uses the modular subtitle pipeline. Optionally pass custom subtitle_source,
    layout, or renderer; otherwise they are built from config.
    
    If scene is provided, uses the video engine to generate base frames with
    image sequences and motion effects. Otherwise, uses solid color background.
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
    
    layout_impl = layout or _layout_for_mode(subtitle_config.mode)
    renderer_impl = renderer or PillowSubtitleRenderer()
    
    if scene is not None:
        # Use engine renderer for base frames
        from engine.image_loader import ImageLoader
        from engine.planner import ScenePlanner
        from engine.renderer import FrameRenderer
        
        print("Initializing video engine...")
        image_loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, image_loader)
        frame_renderer = FrameRenderer(timeline, image_loader)
        
        # Override resolution and fps from scene
        config["width"] = scene.resolution[0]
        config["height"] = scene.resolution[1]
        config["fps"] = scene.fps
        fps = scene.fps
        
        # Use timeline duration if longer than audio
        final_duration = max(final_duration, timeline.duration)
        print(f"Video duration: {final_duration:.2f} seconds (engine timeline: {timeline.duration:.2f}s)")
        
        # Create layout context for subtitles
        context = SubtitleLayoutContext.from_config(
            scene.resolution[0],
            scene.resolution[1],
            subtitle_config,
        )
        
        def make_frame_with_engine(t: float) -> np.ndarray:
            """Generate frame with engine base + subtitle overlay."""
            # Get base frame from engine
            base_frame = frame_renderer.render_frame(t)
            
            # Convert to PIL Image for subtitle rendering
            base_image = Image.fromarray(base_frame)
            
            # Get subtitle segments
            if subtitle_config.mode == SubtitleMode.STACKING:
                segments = source.get_all_segments()
            else:
                segments = source.get_segments_for_time(t)
            
            # Layout and render subtitles
            layout_items = layout_impl.layout_frame(
                t, segments, context, subtitle_config
            )
            final_image = renderer_impl.render_frame(
                base_image, layout_items, subtitle_config, context
            )
            
            return np.array(final_image)
        
        print("Generating frames with video engine...")
        video_clip = VideoClip(make_frame_with_engine, duration=final_duration)
    else:
        # Use existing solid background approach
        print(f"Video duration: {final_duration:.2f} seconds")
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
