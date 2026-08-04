# Mahabharata Video - Phase 4 Effects Showcase

This script creates **8 different styled videos** from your Mahabharata images, each showcasing different Phase 4 visual effects tailored for epic storytelling.

## Usage

```bash
python examples/mahabharata/create_mahabharata_video_phase4.py
```

## Output

Creates 8 videos in `output/mahabharata_phase4/`:

### 1. Ancient Epic (`mahabharata_ancient.mp4`)
**Effects:** Sepia tone, vignette, film grain, gamma correction
**Style:** Aged, historical, ancient manuscript aesthetic
**Best for:** Traditional storytelling, historical presentations

### 2. Mystical/Divine (`mahabharata_mystical.mp4`)
**Effects:** Hue shift, light leak, blur, enhanced saturation
**Style:** Ethereal, glowing, divine, supernatural
**Best for:** Depicting divine characters, mystical scenes

### 3. Dramatic/Intense (`mahabharata_dramatic.mp4`)
**Effects:** High contrast, chromatic aberration, vignette
**Style:** Bold, intense, dramatic tension
**Best for:** Battle scenes, emotional moments, climactic events

### 4. Illustrated/Artistic (`mahabharata_illustrated.mp4`)
**Effects:** Sketch effect, enhanced saturation
**Style:** Hand-drawn illustration, artistic interpretation
**Best for:** Storybook presentations, artistic retellings

### 5. Modern Cinematic (`mahabharata_cinematic.mp4`)
**Effects:** Gamma correction, color temperature, subtle vignette, sharpening
**Style:** Professional, clean, modern film quality
**Best for:** Contemporary retellings, high-quality presentations

### 6. Duotone/Stylized (`mahabharata_duotone.mp4`)
**Effects:** Two-color mapping (dark blue to golden yellow), vignette
**Style:** Stylized, artistic, limited color palette
**Best for:** Unique visual identity, artistic presentations

### 7. Comic Book (`mahabharata_comic.mp4`)
**Effects:** Posterize, edge detection, enhanced saturation and contrast
**Style:** Graphic novel, comic book aesthetic
**Best for:** Modern adaptations, bold visual storytelling

### 8. Ethereal Dream (`mahabharata_ethereal.mp4`)
**Effects:** Heavy blur, light leak, hue shift, brightness boost
**Style:** Soft, dreamlike, heavenly, otherworldly
**Best for:** Dream sequences, divine visions, spiritual themes

## Requirements

- Mahabharata images in `files/mahabharata/` directory
- At least 10 images (JPG or PNG format)
- PRISM video engine with Phase 4 effects

## Performance

- Each video: ~30 seconds duration
- Resolution: 1920x1080 (Full HD)
- Frame rate: 30 FPS
- Total rendering time: ~6-12 minutes for all 8 videos (depends on hardware)

## Customization

Edit the effect presets in the script to create your own styles:

```python
# Example: Create a custom "War Scene" style
war_effects = [
    contrast(1.5),
    saturation(0.7),  # Desaturated
    vignette(0.8),
    chromatic_aberration(10),
]
```

## Style Guide

### For Different Story Elements:

- **Ancient** - Flashbacks, historical context, traditional narration
- **Mystical** - Divine interventions, supernatural events, blessings
- **Dramatic** - Battle scenes, confrontations, emotional peaks
- **Illustrated** - Chapter introductions, artistic interludes
- **Cinematic** - Main narrative, character development
- **Duotone** - Thematic sequences, symbolic moments
- **Comic** - Action sequences, dynamic moments
- **Ethereal** - Dream sequences, divine visions, spiritual moments

## Tips

- Mix different styles for different parts of the story
- **Ancient** style works great for opening/closing sequences
- **Mystical** enhances scenes with Krishna or divine characters
- **Dramatic** amplifies battle sequences (Kurukshetra)
- **Cinematic** is versatile for most narrative scenes
- **Ethereal** perfect for Bhagavad Gita sequences

## See Also

- `create_mahabharata_video_simple.py` - Basic version with Phase 2 effects
- `create_mahabharata_video_phase3.py` - Audio-reactive effects version
