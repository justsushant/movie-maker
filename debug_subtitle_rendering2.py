"""Debug script to analyze the second segment issue."""

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
from subtitle.layouts import WordHighlightLayout, _build_single_line_chunks
from subtitle.renderer import PillowSubtitleRenderer
from subtitle.source import JsonSubtitleSource
from subtitle_config import SubtitleConfig


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
    
    subtitle_cfg = SubtitleConfig.from_dict(cfg2)
    context = SubtitleLayoutContext.from_config(cfg2["width"], cfg2["height"], subtitle_cfg)
    
    print(f"Video dimensions: {cfg2['width']}x{cfg2['height']}")
    print(f"Max text width: {context.max_text_width_px}px")
    
    source = JsonSubtitleSource(case2_dir / "output_moviepy.json")
    segments = source.get_all_segments()
    
    print(f"\nTotal segments: {len(segments)}")
    
    # Analyze second segment
    if len(segments) > 1:
        seg = segments[1]
        print(f"\nSecond segment:")
        print(f"  Text: '{seg.sentence_text}'")
        print(f"  Length: {len(seg.sentence_text)} chars")
        print(f"  Words: {len(seg.words)}")
        print(f"  Time: {seg.start_time:.2f}s - {seg.end_time:.2f}s")
        
        # Test actual text measurement
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", context.font_size)
        except:
            font = ImageFont.load_default()
        
        img = Image.new('RGB', (cfg2['width'], cfg2['height']))
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), seg.sentence_text, font=font)
        actual_width = bbox[2] - bbox[0]
        
        print(f"\nFull sentence measurement:")
        print(f"  Text width: {actual_width}px")
        print(f"  Max allowed: {context.max_text_width_px}px")
        print(f"  Overflow: {actual_width > context.max_text_width_px}")
        
        # Test chunking
        chunks = _build_single_line_chunks(seg, context, subtitle_cfg)
        print(f"\nChunks created: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            chunk_bbox = draw.textbbox((0, 0), chunk.text, font=font)
            chunk_width = chunk_bbox[2] - chunk_bbox[0]
            print(f"  Chunk {i+1}: '{chunk.text}'")
            print(f"    Width: {chunk_width}px (fits: {chunk_width <= context.max_text_width_px})")
            print(f"    Time: {chunk.start_time:.2f}s - {chunk.end_time:.2f}s")
        
        # Test word measurements
        print(f"\nIndividual words:")
        for word in seg.words:
            word_bbox = draw.textbbox((0, 0), word.text, font=font)
            word_width = word_bbox[2] - word_bbox[0]
            print(f"  '{word.text}': {word_width}px (time: {word.start_time:.2f}s - {word.end_time:.2f}s)")
        
        # Test layout at different times
        print(f"\nLayout at different times:")
        test_times = [seg.start_time, 1.5, 2.5, 3.5, seg.end_time]
        layout = WordHighlightLayout()
        
        for t in test_times:
            positioned = layout.layout_frame(t, [seg], context, subtitle_cfg)
            if positioned:
                words_shown = [p.text for p in positioned]
                total_width = sum(
                    draw.textbbox((0, 0), p.text, font=font)[2] - draw.textbbox((0, 0), p.text, font=font)[0]
                    for p in positioned
                )
                print(f"  t={t:.2f}s: {len(positioned)} words, total width: {total_width}px")
                print(f"    Words: {words_shown}")
