# Phase 4 Effects Showcase - Video Generation Scripts

This document describes the Phase 4 effect showcase scripts for generating multiple styled videos from your image collections.

## Overview

Phase 4 adds **56+ rich visual effects** to the movie-maker video engine:
- **20+ color effects** (sepia, hue shift, posterize, etc.)
- **10+ blur effects** (gaussian, motion, pixelate, etc.)
- **11+ texture effects** (scan lines, vignette, light leak, etc.)
- **14+ stylization effects** (sketch, glitch, CRT, etc.)

## Available Scripts

### 1. Dragon Videos (`examples/dragon/create_dragon_video_phase4.py`)

Creates **7 different styled dragon videos**:

| Style | Effects | Duration | Best For |
|-------|---------|----------|----------|
| Cinematic Epic | Color grading, vignette | ~30s | Professional presentations |
| Retro VHS | CRT, scan lines, chromatic aberration | ~30s | Vintage/nostalgic themes |
| Sketch/Artistic | Pencil sketch | ~30s | Concept art, storyboards |
| Glitch Cyberpunk | RGB split, glitch effects | ~30s | Sci-fi, tech themes |
| Dreamy Ethereal | Blur, light leak, hue shift | ~30s | Fantasy, magical themes |
| Posterized Comic | Posterize, edge detection | ~30s | Graphic novel style |
| Noir/High Contrast | B&W threshold, vignette | ~30s | Dramatic, moody |

**Usage:**
```bash
python examples/dragon/create_dragon_video_phase4.py
```

**Output:** `output/dragon_phase4/*.mp4` (7 videos)

---

### 2. Mahabharata Videos (`examples/mahabharata/create_mahabharata_video_phase4.py`)

Creates **8 different styled Mahabharata videos**:

| Style | Effects | Duration | Best For |
|-------|---------|----------|----------|
| Ancient Epic | Sepia, film grain, vignette | ~30s | Historical, traditional |
| Mystical/Divine | Hue shift, light leak, glow | ~30s | Divine characters, supernatural |
| Dramatic/Intense | High contrast, chromatic aberration | ~30s | Battle scenes, emotional peaks |
| Illustrated/Artistic | Sketch, enhanced saturation | ~30s | Storybook presentations |
| Modern Cinematic | Color grading, sharpening | ~30s | Contemporary retellings |
| Duotone/Stylized | Two-color mapping | ~30s | Unique visual identity |
| Comic Book | Posterize, edge detection | ~30s | Modern adaptations |
| Ethereal Dream | Heavy blur, light leak | ~30s | Dream sequences, visions |

**Usage:**
```bash
python examples/mahabharata/create_mahabharata_video_phase4.py
```

**Output:** `output/mahabharata_phase4/*.mp4` (8 videos)

---

## Requirements

### Image Files
- **Dragon:** Place images in `files/dragon/` (JPG or PNG)
- **Mahabharata:** Place images in `files/mahabharata/` (JPG or PNG)
- Minimum: 10 images per collection
- Recommended: High resolution (1920x1080 or higher)

### System Requirements
- Python 3.10+
- movie-maker with Phase 4 effects installed
- ~2GB RAM per video render
- ~500MB disk space per output video

## Performance

### Rendering Times (approximate)
- **Per video:** 1-2 minutes (depends on hardware)
- **Dragon (7 videos):** 7-14 minutes total
- **Mahabharata (8 videos):** 8-16 minutes total

### Output Specifications
- **Resolution:** 1920x1080 (Full HD)
- **Frame rate:** 30 FPS
- **Duration:** ~30 seconds per video
- **Codec:** H.264 (libx264)
- **File size:** ~20-50 MB per video

## Effect Categories

### Color Effects
- `sepia()` - Warm, aged tone
- `hue_shift(degrees)` - Shift color spectrum
- `color_temperature(kelvin)` - Warm/cool tint
- `posterize(bits)` - Reduce color levels
- `duotone(shadow, highlight)` - Two-color mapping
- `gamma_correction(gamma)` - Brightness curve
- `invert()` - Invert colors

### Blur Effects
- `gaussian_blur(radius)` - Smooth blur
- `motion_blur(length, angle)` - Directional blur
- `pixelate(factor)` - Blocky pixelation
- `sharpen(amount)` - Enhance edges

### Texture Effects
- `scan_lines(spacing, intensity)` - Horizontal lines
- `vignette(intensity)` - Darken edges
- `light_leak(intensity)` - Colorful glow
- `film_grain(intensity)` - Analog grain
- `border(thickness, color)` - Frame border

### Stylization Effects
- `sketch()` - Pencil drawing
- `edge_detection()` - Outline edges
- `halftone(dot_size)` - Dot pattern
- `chromatic_aberration(offset)` - Color fringing
- `glitch_rgb_split(offset)` - RGB channel separation
- `crt_retro(intensity)` - CRT monitor effect
- `threshold_bw(threshold)` - Black & white
- `emboss()` - 3D relief effect

## Customization

### Creating Custom Styles

Edit the effect lists in the scripts:

```python
# Example: Create a "Fire Dragon" style
fire_dragon_effects = [
    hue_shift(15),           # Shift to red/orange
    saturation(1.5),         # Boost saturation
    brightness(0.1),         # Slightly brighter
    chromatic_aberration(5), # Add heat distortion
    vignette(0.4),          # Focus center
]
```

### Combining Effects

Effects are applied in order:

```python
# Order matters!
effects = [
    gaussian_blur(3),    # 1. Blur first
    hue_shift(30),       # 2. Then shift colors
    vignette(0.5),       # 3. Finally add vignette
]
```

### Adjusting Parameters

Most effects accept intensity parameters:

```python
# Subtle effect
light_leak(0.2)

# Strong effect
light_leak(0.8)
```

## Tips & Best Practices

### Style Selection
- **Cinematic** - Versatile, works for most content
- **Retro** - Great for 80s/90s themes
- **Sketch** - Perfect for concept presentations
- **Glitch** - Modern, tech-focused content
- **Dreamy** - Fantasy and magical themes
- **Ancient** - Historical or traditional content
- **Noir** - Dramatic, high-contrast scenes

### Performance Optimization
- Reduce resolution for faster previews: `resolution=(1280, 720)`
- Lower FPS for testing: `fps=15`
- Render fewer clips for quick tests

### Quality Settings
- **Draft:** `ffmpeg_params=['-crf', '28']` (smaller files)
- **Standard:** `ffmpeg_params=['-crf', '23']` (balanced)
- **High Quality:** `ffmpeg_params=['-crf', '18']` (larger files)
- **Lossless:** `ffmpeg_params=['-crf', '0']` (very large)

## Troubleshooting

### "No images found"
- Check image paths: `files/dragon/` or `files/mahabharata/`
- Ensure images are JPG or PNG format
- Verify at least 10 images exist

### "Out of memory"
- Reduce resolution: `resolution=(1280, 720)`
- Process fewer images at once
- Close other applications

### "Rendering too slow"
- Use draft quality for testing
- Reduce FPS: `fps=15`
- Disable heavy effects (blur, sketch)

### "Video quality poor"
- Increase CRF quality: `'-crf', '15'`
- Use higher resolution source images
- Adjust effect intensities

## Next Steps

1. **Generate videos:** Run the scripts to create all variations
2. **Review output:** Check `output/dragon_phase4/` and `output/mahabharata_phase4/`
3. **Select favorites:** Choose the styles that work best for your content
4. **Customize:** Modify effect parameters to fine-tune the look
5. **Add audio:** Combine with TTS narration using Phase 3 scripts

## See Also

- `examples/demo_phase4_rich_effects.py` - Phase 4 effects demo
- `examples/dragon/create_dragon_video_simple.py` - Basic dragon video
- `examples/mahabharata/create_mahabharata_video_simple.py` - Basic mahabharata video
- `docs/video_engine.md` - Complete video engine documentation

## Support

For issues or questions:
1. Check the README files in each example directory
2. Review the effect documentation in `docs/video_engine.md`
3. Test with the demo script: `examples/demo_phase4_rich_effects.py`
