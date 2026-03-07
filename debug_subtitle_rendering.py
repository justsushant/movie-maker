"""Debug script to analyze subtitle rendering issues."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from PIL import ImageFont, ImageDraw, Image

# Import config module
_config_spec = importlib.util.spec_from_file_location("config_module", "config.py")
config_py = importlib.util.module_from_spec(_config_spec)
_config_spec.loader.exec_module(config_py)

from subtitle.composer import SubtitleFrameComposer
from subtitle.interfaces import SubtitleLayoutContext
from subtitle.layouts import SentenceLayout, WordHighlightLayout
from subtitle.renderer import PillowSubtitleRenderer
from subtitle.source import JsonSubtitleSource
from subtitle_config import SubtitleConfig, SubtitleMode


def analyze_case(case_name: str, json_path: Path, cfg: dict):
    """Analyze a specific test case for rendering issues."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {case_name}")
    print(f"{'='*80}")
    
    subtitle_cfg = SubtitleConfig.from_dict(cfg)
    context = SubtitleLayoutContext.from_config(cfg["width"], cfg["height"], subtitle_cfg)
    
    print(f"\nVideo dimensions: {cfg['width']}x{cfg['height']}")
    print(f"Subtitle mode: {subtitle_cfg.mode}")
    print(f"\nLayout Context:")
    print(f"  Font size: {context.font_size}px")
    print(f"  X margin: {context.x_margin_px}px ({subtitle_cfg.x_margin * 100}%)")
    print(f"  Y margin: {context.y_margin_px}px ({subtitle_cfg.y_margin * 100}%)")
    print(f"  Max text width: {context.max_text_width_px}px ({subtitle_cfg.max_width_ratio * 100}%)")
    print(f"  Available width: {cfg['width'] - 2 * context.x_margin_px}px")
    print(f"  Line height: {context.line_height_px}px")
    
    # Calculate character estimation
    avg_char_px = max(1, int(context.font_size * 0.55))
    max_chars = max(8, context.max_text_width_px // avg_char_px)
    print(f"\nCharacter width estimation:")
    print(f"  Avg char width: {avg_char_px}px (font_size * 0.55)")
    print(f"  Max chars per line: {max_chars}")
    
    # Load actual subtitle data
    source = JsonSubtitleSource(json_path)
    segments = source.get_all_segments()
    
    print(f"\nSubtitle segments: {len(segments)}")
    
    # Analyze first segment
    if segments:
        seg = segments[0]
        print(f"\nFirst segment:")
        print(f"  Text: '{seg.sentence_text}'")
        print(f"  Length: {len(seg.sentence_text)} chars")
        print(f"  Words: {len(seg.words)}")
        
        # Test actual text measurement with PIL
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", context.font_size)
        except:
            font = ImageFont.load_default()
        
        img = Image.new('RGB', (cfg['width'], cfg['height']))
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), seg.sentence_text, font=font)
        actual_width = bbox[2] - bbox[0]
        
        print(f"\nActual PIL measurement:")
        print(f"  Text width: {actual_width}px")
        print(f"  Max allowed: {context.max_text_width_px}px")
        print(f"  Overflow: {actual_width > context.max_text_width_px}")
        print(f"  Overflow amount: {actual_width - context.max_text_width_px}px")
        
        # Check if it fits in available width
        available = cfg['width'] - 2 * context.x_margin_px
        print(f"  Fits in available width: {actual_width <= available}")
        
        # Test word-by-word measurement
        if seg.words:
            print(f"\nWord measurements:")
            total_word_width = 0
            for i, word in enumerate(seg.words[:5]):  # First 5 words
                word_bbox = draw.textbbox((0, 0), word.text, font=font)
                word_width = word_bbox[2] - word_bbox[0]
                total_word_width += word_width
                print(f"    '{word.text}': {word_width}px")
            
            if len(seg.words) > 5:
                print(f"    ... ({len(seg.words) - 5} more words)")
                for word in seg.words[5:]:
                    word_bbox = draw.textbbox((0, 0), word.text, font=font)
                    total_word_width += word_bbox[2] - word_bbox[0]
            
            print(f"  Total word widths: {total_word_width}px")


# Test case 1: long_paragraph_720_sentence_multiline
case1_dir = Path("output/test/long_paragraph_720_sentence_multiline")
if case1_dir.exists():
    cfg1 = config_py.get_test_config(
        case_id="long_paragraph_720_sentence_multiline",
        overrides={
            "width": 1280,
            "height": 720,
            "fps": 24,
            "bg_color": (0, 0, 0),
            "text_color": (255, 255, 255),
            "highlight_color": (255, 255, 0),
            "subtitle": {"mode": "sentence", "vertical_align": "bottom", "multiline_enabled": True},
        },
    )
    analyze_case("long_paragraph_720_sentence_multiline", case1_dir / "output_moviepy.json", cfg1)

# Test case 2: punctuation_heavy_phone_1080x1920_sentence_highlight
case2_dir = Path("output/test/punctuation_heavy_phone_1080x1920_sentence_highlight")
if case2_dir.exists():
    cfg2 = config_py.get_test_config(
        case_id="punctuation_heavy_phone_1080x1920_sentence_highlight",
        overrides={
            "width": 1080,
            "height": 1920,
            "fps": 24,
            "bg_color": (0, 0, 0),
            "text_color": (255, 255, 255),
            "highlight_color": (255, 255, 0),
            "subtitle": {"mode": "sentence_with_word_highlight", "vertical_align": "bottom"},
        },
    )
    analyze_case("punctuation_heavy_phone_1080x1920_sentence_highlight", case2_dir / "output_moviepy.json", cfg2)

print("\n" + "="*80)
print("Analysis complete")
print("="*80)
