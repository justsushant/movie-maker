"""Frame composer: source -> layout -> renderer -> image."""

from __future__ import annotations

import numpy as np
from PIL import Image

from subtitle_config import SubtitleConfig, SubtitleMode

from subtitle.interfaces import (
    ISubtitleLayout,
    ISubtitleRenderer,
    ISubtitleSource,
    SubtitleLayoutContext,
)


class SubtitleFrameComposer:
    """
    Orchestrates subtitle source -> layout -> renderer per frame.
    Callable as make_frame(t) for MoviePy.
    """

    def __init__(
        self,
        subtitle_source: ISubtitleSource,
        layout: ISubtitleLayout,
        renderer: ISubtitleRenderer,
        subtitle_config: SubtitleConfig,
        video_settings: dict,
    ) -> None:
        self._source = subtitle_source
        self._layout = layout
        self._renderer = renderer
        self._subtitle_config = subtitle_config
        self._width = video_settings["width"]
        self._height = video_settings["height"]
        self._bg_color = video_settings["bg_color"]
        self._context = SubtitleLayoutContext.from_config(
            self._width,
            self._height,
            subtitle_config,
        )

    def __call__(self, t: float) -> np.ndarray:
        if self._subtitle_config.mode == SubtitleMode.ROLLING:
            segments = self._source.get_all_segments()
        else:
            segments = self._source.get_segments_for_time(t)

        layout_items = self._layout.layout_frame(
            t, segments, self._context, self._subtitle_config
        )

        image = Image.new("RGB", (self._width, self._height), self._bg_color)
        image = self._renderer.render_frame(
            image, layout_items, self._subtitle_config, self._context
        )
        return np.array(image)
