# Text Overlay Effect Usage

The `text_overlay` effect allows you to add text labels to video frames, useful for demos, tutorials, and effect identification.

## Basic Usage

```python
from engine.effects import text_overlay
from engine.scene import Scene, ImageClip, MotionPreset

clip = ImageClip(
    source="image.jpg",
    duration=5.0,
    motion=MotionPreset.STATIC,
    effects=[
        text_overlay("My Effect Name", position=(50, 50))
    ]
)
```

## Parameters

- **text** (str): Text string to display
- **position** (tuple[int, int]): (x, y) position of text top-left corner (default: (50, 50))
- **font_scale** (float): Font size multiplier (default: 1.0, range: 0.5-3.0)
- **color** (tuple[int, int, int]): Text color as RGB tuple (default: white (255, 255, 255))
- **thickness** (int): Text stroke thickness in pixels (default: 2, range: 1-5)
- **bg_color** (tuple[int, int, int] | None): Background color as RGB tuple, or None for no background (default: black (0, 0, 0))
- **bg_opacity** (float): Background opacity (default: 0.7, range: 0.0-1.0)
- **padding** (int): Padding around text in pixels (default: 10)

## Examples

### Text with Semi-Transparent Background

```python
text_overlay(
    "Grayscale Effect",
    position=(50, 50),
    font_scale=1.5,
    color=(255, 255, 255),
    bg_color=(0, 0, 0),
    bg_opacity=0.7,
    padding=10
)
```

### Text Without Background

```python
text_overlay(
    "No Background",
    position=(50, 50),
    font_scale=1.2,
    color=(255, 255, 0),  # Yellow
    bg_color=None
)
```

### Large Title Text

```python
text_overlay(
    "TITLE",
    position=(100, 100),
    font_scale=3.0,
    color=(255, 255, 255),
    thickness=4,
    bg_color=(0, 0, 0),
    bg_opacity=0.8,
    padding=20
)
```

### Combining with Other Effects

```python
clip = ImageClip(
    source="image.jpg",
    duration=5.0,
    effects=[
        grayscale(),  # Apply grayscale first
        vignette_simple(0.5),  # Add vignette
        text_overlay("Grayscale + Vignette", position=(50, 50))  # Label last
    ]
)
```

## Best Practices

1. **Apply text overlay last**: Add text_overlay as the last effect in the chain so text appears on top of all other effects
2. **Use readable colors**: White text on dark background or dark text on light background
3. **Position carefully**: Avoid placing text where it might be cut off or overlap important content
4. **Consistent positioning**: Use the same position across clips for a professional look
5. **Appropriate font size**: Use larger font_scale (1.5-2.0) for 1080p videos, smaller (0.8-1.0) for lower resolutions

## Performance

- **Rendering time**: ~2-5ms per frame at 1080p
- **Memory**: Minimal overhead (creates one copy of frame)
- **Compatibility**: Works with all other effects and transitions

## Demo Usage

See `examples/demo_phase4_rich_effects.py` for a complete example of using text overlays to label different effects in a showcase video.

## Notes

- Text is rendered using OpenCV's `cv2.putText` with anti-aliasing
- Multiline text is not supported (newlines are treated as part of the text string)
- Background rectangle is automatically sized to fit the text with padding
- Position coordinates are clamped to frame boundaries to prevent errors
