"""PIL-based subtitle renderer."""

from __future__ import annotations

from typing import List

from PIL import Image, ImageDraw, ImageFont

from subtitle.config import SubtitleConfig

from subtitle.interfaces import PositionedSubtitle, SubtitleLayoutContext


def _resolve_font(font_size: int, font_path: str | None = None) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a TrueType font; fall back to default if path missing or invalid."""
    if font_path:
        try:
            return ImageFont.truetype(font_path, font_size)
        except OSError:
            pass
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except OSError:
        try:
            return ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            return ImageFont.load_default()


class PillowSubtitleRenderer:
    """Draws PositionedSubtitle list onto a PIL Image using ImageDraw."""

    def render_frame(
        self,
        base_image: Image.Image,
        layout: List[PositionedSubtitle],
        subtitle_config: SubtitleConfig,
        context: SubtitleLayoutContext,
    ) -> Image.Image:
        if not layout:
            return base_image

        draw = ImageDraw.Draw(base_image)

        # Group items by y (same line) so we can center a line of words
        by_y: dict[int, list[PositionedSubtitle]] = {}
        for item in layout:
            by_y.setdefault(item.y, []).append(item)

        for y, items in by_y.items():
            fonts = [_resolve_font(it.font_size, subtitle_config.font_path) for it in items]
            bboxes = [
                draw.textbbox((0, 0), it.text, font=font)
                for it, font in zip(items, fonts)
            ]
            widths = [r - l for (l, _, r, _) in bboxes]
            total_width = sum(widths)

            if context.align == "left":
                x: float = float(context.x_margin_px)
            elif context.align == "right":
                x = float(context.width - context.x_margin_px - total_width)
            else:
                x = (context.width - total_width) / 2

            for item, font, w in zip(items, fonts, widths):
                draw.text((int(x), y), item.text, font=font, fill=item.color)
                x += w

        return base_image
