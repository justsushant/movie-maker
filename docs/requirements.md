# What You Need to Create Videos with Phase 2

## Essential Requirements

### 1. Images 📸

**What formats?**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- Any format supported by PIL/Pillow

**How many?**
- Minimum: 1 image (for a single clip)
- Typical: 3-5 images for a short video
- No maximum limit

**Where to put them?**
- Anywhere accessible to your script
- Example: `images/`, `photos/`, `assets/`
- Or use test images: `tests/fixtures/images/`

**Recommended specs:**
- Resolution: 1920x1080 or higher
- Aspect ratio: Match your target video (16:9 for 1920x1080)
- File size: Any (will be loaded and resized)
- Quality: Higher quality = better results

### 2. Text Script (Optional) 📝

**For narrated videos:**
- Plain text file (UTF-8 encoded)
- Example: `files/input.txt`
- Or pass text directly as a string

**For visual-only videos:**
- No text needed!
- Just use the video engine directly

### 3. Python Environment 🐍

**Setup:**
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies (if not already done)
make setup
```

**Required packages:**
- moviepy (video encoding)
- numpy (frame arrays)
- opencv-python (image transforms)
- pillow (image loading, subtitle rendering)
- kokoro (TTS, only for narrated videos)

### 4. Python Script 📄

**Minimal script:**
```python
from pathlib import Path
from api.library import generate_video_from_text
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType

scene = Scene(
    clips=[
        ImageClip("image1.jpg", duration=3.0, motion=MotionPreset.ZOOM_IN),
        ImageClip("image2.jpg", duration=3.0, motion=MotionPreset.PAN_LEFT),
    ],
    transitions=[
        Transition(type=TransitionType.CROSSFADE, duration=0.5)
    ],
    resolution=(1920, 1080),
    fps=30
)

video_path = generate_video_from_text(
    text="Your narration.",
    output_dir=Path("output/my_video"),
    scene=scene
)
```

## What You Get

### Output Files

When you run the script, you'll get:

```
output/my_video/
├── output_moviepy.wav        # Generated audio (if using TTS)
├── output_moviepy.json       # Subtitle timing data (if using TTS)
└── output_video.mp4          # Final video ✨
```

### Video Specifications

**Default settings:**
- Resolution: 1920x1080 (configurable)
- Frame rate: 30 fps (configurable)
- Codec: H.264 (MP4)
- Audio: 24kHz WAV (if using TTS)

## Quick Start Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed (`make setup`)
- [ ] Images ready (at least 1)
- [ ] Text script prepared (if using narration)
- [ ] Python script created
- [ ] Output directory specified

## Example Workflows

### Workflow 1: Narrated Video with Effects

**You need:**
1. 3-5 images
2. Text script
3. Python script with Scene definition

**You get:**
- Video with TTS narration
- Word-by-word subtitle highlighting
- Motion effects on images
- Smooth transitions between clips
- Visual effects (color grading, vignettes)

**Time:** ~30 seconds to 2 minutes (depending on length)

### Workflow 2: Visual-Only Slideshow

**You need:**
1. Images
2. Python script (no text needed)

**You get:**
- Silent video with image sequence
- Motion effects
- Transitions
- Visual effects

**Time:** ~10-30 seconds

### Workflow 3: Quick Test

**You need:**
1. Test images (already in `tests/fixtures/images/`)
2. Demo script (already created)

**You get:**
- Sample video showcasing all features

**Time:** ~30 seconds

```bash
python demo_phase2_showcase.py
```

## Feature Checklist

### Phase 1 Features (Available)
- [x] Image-based video composition
- [x] 9 motion presets (zoom, pan, Ken Burns)
- [x] Smooth easing functions
- [x] Virtual camera system
- [x] Image caching for performance

### Phase 2 Features (Available)
- [x] 24 transition types
  - [x] Blend transitions (crossfade, fade through colors)
  - [x] Geometric transitions (slides, pushes, wipes)
  - [x] Shape transitions (iris, clock, diamond, blinds)
  - [x] Animated transitions (zoom through, whip pan, pixelate, glitch)
- [x] Visual effects
  - [x] Color grading (brightness, contrast, saturation)
  - [x] Vignette
  - [x] Film grain
  - [x] Fade in/out
  - [x] Pulse effect
- [x] Effect chaining
- [x] Transition overlap calculation
- [x] Full backward compatibility with Phase 1

## Common Questions

**Q: Do I need audio for every video?**
A: No! You can create visual-only videos without TTS.

**Q: Can I use my own audio?**
A: Yes, but you'll need to modify the pipeline. The current API generates TTS audio.

**Q: How long does rendering take?**
A: ~2-3ms per frame at 1080p without effects. A 10-second video (300 frames) takes ~1-2 seconds to render, plus encoding time.

**Q: Can I use different image sizes?**
A: Yes! Images are automatically resized to match your target resolution.

**Q: Do all clips need the same duration?**
A: No, each clip can have its own duration.

**Q: How many transitions can I have?**
A: Maximum of N-1 transitions for N clips (one between each pair).

**Q: Can I apply multiple effects to one clip?**
A: Yes! Use `chain_effects()` or pass a list of effects.

**Q: What if I don't have images?**
A: Use the test images in `tests/fixtures/images/` to get started.

## Resources

### Documentation
- `QUICK_START.md` - Get started in 30 seconds
- `PHASE2_USAGE_GUIDE.md` - Complete feature documentation
- `.kiro/specs/video-engine-phase-2/design.md` - Technical design

### Demo Scripts
- `demo_phase2_showcase.py` - Full feature showcase with TTS
- `demo_phase2_simple.py` - Visual-only demo without TTS
- `test_real_video.py` - Original Phase 1 demo

### Test Images
- `tests/fixtures/images/landscape.jpg`
- `tests/fixtures/images/portrait.jpg`
- `tests/fixtures/images/square.jpg`

### Example Code
- `tests/test_phase2_integration.py` - Integration test examples
- `tests/test_transitions.py` - Transition examples
- `tests/test_effects.py` - Effect examples

## Getting Help

1. **Run the demos first**: See working examples
2. **Check the tests**: Real usage patterns
3. **Read the guides**: Detailed documentation
4. **Review error messages**: Usually indicate missing files or invalid parameters

## Ready to Start?

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run showcase demo
python demo_phase2_showcase.py

# 3. Check output
open output/phase2_showcase/output_video.mp4
```

That's it! You now have everything you need to create professional videos with transitions and effects. 🎬
