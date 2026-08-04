# Dragon Video - Phase 4 Effects Showcase

This script creates **7 different styled videos** from your dragon images, each showcasing different Phase 4 visual effects.

## Usage

```bash
python examples/dragon/create_dragon_video_phase4.py
```

## Output

Creates 7 videos in `output/dragon_phase4/`:

### 1. Cinematic Epic (`dragon_cinematic.mp4`)
**Effects:** Gamma correction, desaturated colors, vignette, color temperature
**Style:** Professional, epic, movie-like quality
**Best for:** Dramatic storytelling, high-quality presentations

### 2. Retro VHS (`dragon_retro.mp4`)
**Effects:** CRT scan lines, chromatic aberration, hue shift
**Style:** 80s/90s VHS tape aesthetic
**Best for:** Nostalgic, vintage, retro-futuristic themes

### 3. Sketch/Artistic (`dragon_sketch.mp4`)
**Effects:** Pencil sketch effect
**Style:** Hand-drawn, artistic, illustration-like
**Best for:** Storyboards, concept art presentations

### 4. Glitch Cyberpunk (`dragon_glitch.mp4`)
**Effects:** RGB split, chromatic aberration, scan lines
**Style:** Digital glitch, cyberpunk, futuristic
**Best for:** Tech themes, sci-fi, modern digital art

### 5. Dreamy Ethereal (`dragon_dreamy.mp4`)
**Effects:** Gaussian blur, light leak, hue shift, enhanced saturation
**Style:** Soft, glowing, magical, dreamlike
**Best for:** Fantasy themes, mystical storytelling

### 6. Posterized Comic (`dragon_comic.mp4`)
**Effects:** Posterize, edge detection, enhanced saturation
**Style:** Comic book, graphic novel aesthetic
**Best for:** Bold, stylized presentations

### 7. Noir/High Contrast (`dragon_noir.mp4`)
**Effects:** Black & white threshold, heavy vignette
**Style:** Film noir, dramatic black and white
**Best for:** Dramatic, moody, high-contrast storytelling

## Requirements

- Dragon images in `files/dragon/` directory
- At least 10 images (JPG or PNG format)
- movie-maker video engine with Phase 4 effects

## Performance

- Each video: ~30 seconds duration
- Resolution: 1920x1080 (Full HD)
- Frame rate: 30 FPS
- Total rendering time: ~5-10 minutes for all 7 videos (depends on hardware)

## Customization

Edit the effect presets in the script to create your own styles:

```python
# Example: Create your own style
custom_effects = [
    hue_shift(45),
    saturation(1.5),
    vignette(0.7),
]
```

## Tips

- **Cinematic** works well for professional presentations
- **Retro** is great for nostalgic or vintage themes
- **Sketch** is perfect for concept art or storyboards
- **Glitch** fits cyberpunk or tech-themed content
- **Dreamy** enhances fantasy and magical themes
- **Comic** creates bold, graphic novel aesthetics
- **Noir** adds drama and intensity

## See Also

- `create_dragon_video_simple.py` - Basic version with Phase 2 effects
- `create_dragon_video_phase3.py` - Audio-reactive effects version
