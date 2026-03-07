# Mahabharata - The Great War of Dharma

## Your Files

```
files/mahabharata/
├── input.txt                    # Your narration script
└── 12 Mahabharata images       # Epic artwork depicting the great war
```

## Two Ways to Create Your Video

### Option 1: Full Video with Narration (Recommended)

Creates a complete video with TTS narration and word-by-word subtitles.

```bash
# Activate environment
source .venv/bin/activate

# Run the full script
python examples/mahabharata/create_mahabharata_video.py
```

**Output:** `output/mahabharata_epic/output_video.mp4`

**Features:**
- TTS narration from your input.txt
- Word-by-word karaoke-style subtitles with saffron/gold highlights
- 12 images depicting the Mahabharata epic
- 11 dramatic transitions
- Epic color grading (war, divine, wisdom themes)
- Duration: ~35 seconds (with transitions)

**Time:** ~2-3 minutes to generate

### Option 2: Quick Visual Test (No Narration)

Creates a visual-only video for quick testing.

```bash
# Activate environment
source .venv/bin/activate

# Run the simple script
python examples/mahabharata/create_mahabharata_video_simple.py
```

**Output:** `output/mahabharata_simple/mahabharata_epic.mp4`

**Features:**
- Same visuals as Option 1
- No narration or subtitles
- Duration: ~27 seconds (with transitions)

**Time:** ~30-60 seconds to generate

## What's Included

### Your Narration Script

```
Title: The Great War of Dharma – Mahabharata

In ancient India, two royal families fought for a kingdom…
The Pandavas and the Kauravas.

The Pandavas stood for truth and righteousness,
while the Kauravas were driven by greed and power.

After years of betrayal, exile, and injustice,
the conflict led to the great battle of Kurukshetra War.

On the battlefield of Kurukshetra,
the warrior prince Arjuna hesitated to fight his own relatives.

Then his charioteer, Krishna, revealed the wisdom of duty, life, and the soul—
the sacred teachings of the Bhagavad Gita.

The war lasted eighteen days,
ending with the victory of dharma over adharma.

But the true lesson of the Mahabharata is timeless:

When faced with choices in life,
always stand for truth, duty, and righteousness.
```

### Motion Effects (Phase 1)
Each image has cinematic camera movement:
- Ken Burns zoom in/out
- Pan left/right/up/down
- Zoom in/out

### Transitions (Phase 2)
Dramatic blends between images:
- Crossfade (smooth)
- Fade through black (dramatic)
- Wipe left (conflict)
- Iris open (epic reveal)
- Fade through white (divine light)
- Zoom through (dramatic)

### Visual Effects (Phase 2)
Three thematic color grades:

**War Grade** (7 clips):
- Darker for drama
- High contrast
- Desaturated
- Strong vignette
- Used for battle and conflict scenes

**Divine Grade** (3 clips):
- Brighter
- Enhanced saturation
- Golden tones
- Used for Krishna and dharma scenes

**Wisdom Grade** (2 clips):
- Slightly desaturated
- Film grain texture
- Subtle vignette
- Used for philosophical moments

## Customization

### Change Clip Duration

Edit `create_mahabharata_video.py`:
```python
clip_duration = 3.75  # Change this value (seconds)
```

### Change Transitions

Replace any transition type:
```python
Transition(type=TransitionType.CROSSFADE, duration=1.0)
# Change to:
Transition(type=TransitionType.DIAMOND_WIPE, duration=0.8)
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
# Make it more dramatic
war_grade = chain_effects(
    brightness(-0.15),      # Darker
    contrast(1.5),          # Higher contrast
    saturation(0.6),        # More desaturated
    vignette(intensity=0.7, radius=0.65)  # Stronger vignette
)
```

### Change Subtitle Style

Edit subtitle configuration:
```python
subtitle_config = SubtitleConfig(
    mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
    font_size=58,                    # Change size
    base_color=(240, 240, 240),      # Change color (R, G, B)
    highlight_color=(255, 153, 51),  # Saffron/golden highlight
    y_margin=0.15,                   # Change position
    vertical_align="bottom"          # or "top", "center"
)
```

## Thematic Elements

### Color Symbolism
- **Saffron/Gold highlights**: Represents dharma, spirituality, and wisdom
- **Dark war scenes**: Represents conflict and moral dilemmas
- **Bright divine scenes**: Represents Krishna's teachings and enlightenment

### Scene Progression
1. **Introduction** (Clips 1-2): The two families
2. **Conflict** (Clips 3-5): Righteousness vs greed
3. **War** (Clips 6-7): The great battle
4. **Wisdom** (Clips 8-9): Arjuna's dilemma and Krishna's teachings
5. **Resolution** (Clips 10-11): Victory of dharma
6. **Lesson** (Clip 12): Timeless wisdom

## Troubleshooting

### "Image not found" error
Check that all images are in `files/mahabharata/` directory.

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

After running `create_mahabharata_video.py`:

```
output/mahabharata_epic/
├── output_moviepy.wav        # Generated TTS audio
├── output_moviepy.json       # Subtitle timing data
└── output_video.mp4          # Final video ✨
```

## Technical Details

- **Resolution**: 1920x1080 (Full HD)
- **Frame Rate**: 30 fps
- **Codec**: H.264 (MP4)
- **Audio**: 24kHz WAV (TTS generated)
- **Subtitle Mode**: Sentence with word highlight
- **Total Clips**: 12
- **Total Transitions**: 11
- **Color Grades**: 3 different themes

## Cultural Context

The Mahabharata is one of the two major Sanskrit epics of ancient India, the other being the Ramayana. It narrates the struggle between two groups of cousins in the Kurukshetra War and the fates of the Kaurava and the Pandava princes and their successors.

The Bhagavad Gita, a 700-verse Hindu scripture, is part of the Mahabharata and contains a conversation between Prince Arjuna and Krishna, who serves as his charioteer. This dialogue addresses the moral and philosophical dilemmas faced by Arjuna on the battlefield.

## Next Steps

1. **Run the full version**: `python examples/mahabharata/create_mahabharata_video.py`
2. **Watch your video**: `open output/mahabharata_epic/output_video.mp4`
3. **Customize**: Edit transitions, effects, or durations
4. **Share**: Your epic Mahabharata video is ready!

---

**Dharma** (righteousness) over **Adharma** (unrighteousness) 🕉️
