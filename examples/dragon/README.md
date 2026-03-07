# Dragon Legends Video Project

## Your Files

```
files/dragon/
├── input.txt                    # Your narration script
└── 10 dragon images            # Beautiful dragon artwork
```

## Two Ways to Create Your Video

### Option 1: Full Video with Narration (Recommended)

Creates a complete video with TTS narration and word-by-word subtitles.

```bash
# Activate environment
source .venv/bin/activate

# Run the full script
python create_dragon_video.py
```

**Output:** `output/dragon_legends/output_video.mp4`

**Features:**
- TTS narration from your input.txt
- Word-by-word karaoke-style subtitles
- 10 dragon images with cinematic motion
- 9 smooth transitions
- Epic color grading and effects
- Duration: ~36 seconds (with transitions)

**Time:** ~2-3 minutes to generate

### Option 2: Quick Visual Test (No Narration)

Creates a visual-only video for quick testing.

```bash
# Activate environment
source .venv/bin/activate

# Run the simple script
python create_dragon_video_simple.py
```

**Output:** `output/dragon_simple/dragon_showcase.mp4`

**Features:**
- Same visuals as Option 1
- No narration or subtitles
- Duration: ~24 seconds (with transitions)

**Time:** ~30-60 seconds to generate

## What's Included

### Motion Effects (Phase 1)
Each dragon image has cinematic camera movement:
- Ken Burns zoom in/out
- Pan left/right/up/down
- Zoom in/out

### Transitions (Phase 2)
Smooth blends between images:
- Crossfade (classic smooth)
- Fade through black (dramatic)
- Iris open (epic reveal)
- Slide left (dynamic)
- Zoom through (dramatic)

### Visual Effects (Phase 2)
Three color grading styles:

**Epic Grade** (6 clips):
- Slightly darker for drama
- High contrast
- Desaturated
- Strong vignette

**Fire Grade** (2 clips):
- Brighter
- High saturation
- Warm tones

**Mystical Grade** (2 clips):
- Desaturated
- Film grain texture
- Subtle vignette

## Your Narration Script

```
High above ancient mountains,
where the clouds drift across jagged peaks,
legends speak of dragons.

Enormous wings beat against the sky,
their scales shining like living armor in the sun.

Across cultures and continents,
stories tell of creatures that command fire,
guard lost treasures,
and rule the skies.

From the frozen north
to the heart of volcanic lands,
the dragon appears again and again
in the myths of humanity.

Were these giants purely imagination…

or echoes of ancient creatures
that once roamed our world?

In the boundary between myth and mystery,
the legend of the dragon still soars.
```

## Customization

### Change Clip Duration

Edit `create_dragon_video.py`:
```python
clip_duration = 4.5  # Change this value (seconds)
```

### Change Transitions

Replace any transition type:
```python
Transition(type=TransitionType.CROSSFADE, duration=1.0)
# Change to:
Transition(type=TransitionType.GLITCH, duration=0.8)
```

Available transitions:
- `CROSSFADE`, `FADE_THROUGH_BLACK`, `FADE_THROUGH_WHITE`
- `SLIDE_LEFT`, `SLIDE_RIGHT`, `SLIDE_UP`, `SLIDE_DOWN`
- `PUSH_LEFT`, `PUSH_RIGHT`, `PUSH_UP`, `PUSH_DOWN`
- `WIPE_LEFT`, `WIPE_RIGHT`, `WIPE_UP`, `WIPE_DOWN`
- `IRIS_OPEN`, `IRIS_CLOSE`, `CLOCK_WIPE`, `DIAMOND_WIPE`
- `BLINDS_HORIZONTAL`, `BLINDS_VERTICAL`
- `ZOOM_THROUGH`, `WHIP_PAN`, `PIXELATE`, `GLITCH`

### Change Color Grading

Modify the effect chains:
```python
# Make it darker and more dramatic
epic_grade = chain_effects(
    brightness(-0.15),      # Darker
    contrast(1.5),          # Higher contrast
    saturation(0.7),        # More desaturated
    vignette(intensity=0.7, radius=0.7)  # Stronger vignette
)
```

### Change Subtitle Style

Edit subtitle configuration:
```python
subtitle_config = SubtitleConfig(
    mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
    font_size=60,                    # Change size
    base_color=(220, 220, 220),      # Change color (R, G, B)
    highlight_color=(255, 200, 100), # Change highlight
    y_margin=0.15,                   # Change position
    vertical_align="bottom"          # or "top", "center"
)
```

## Troubleshooting

### "Image not found" error
Check that all images are in `files/dragon/` directory.

### "Virtual environment not activated"
```bash
source .venv/bin/activate
```

### Slow rendering
- Use the simple version first for testing
- Reduce FPS to 20 for faster rendering
- Reduce resolution to 1280x720

### Out of memory
- Close other applications
- Reduce clip duration
- Use fewer clips

## Output Files

After running `create_dragon_video.py`:

```
output/dragon_legends/
├── output_moviepy.wav        # Generated TTS audio
├── output_moviepy.json       # Subtitle timing data
└── output_video.mp4          # Final video ✨
```

## Next Steps

1. **Run the full version**: `python create_dragon_video.py`
2. **Watch your video**: `open output/dragon_legends/output_video.mp4`
3. **Customize**: Edit transitions, effects, or durations
4. **Share**: Your epic dragon video is ready!

## Technical Details

- **Resolution**: 1920x1080 (Full HD)
- **Frame Rate**: 30 fps
- **Codec**: H.264 (MP4)
- **Audio**: 24kHz WAV (TTS generated)
- **Subtitle Mode**: Sentence with word highlight
- **Total Clips**: 10
- **Total Transitions**: 9
- **Color Grades**: 3 different styles

Enjoy your dragon legends video! 🐉✨
