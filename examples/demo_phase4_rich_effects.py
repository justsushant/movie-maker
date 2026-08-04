#!/usr/bin/env python3
"""
Phase 4 Rich Effects Showcase Demo

Demonstrates all Phase 4 effects categories:
- Color effects (20+)
- Blur effects (10+)
- Texture effects (11+)
- Stylization effects (14+)
- Advanced transitions (11)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np

from engine.scene import Scene, ImageClip, Transition, TransitionType, MotionPreset
from engine.effects import (
    # Color effects
    grayscale, invert, sepia, hue_shift, color_temperature, tint,
    gamma_correction, duotone, fade_to_color, posterize, solarize,
    # Blur effects
    box_blur, gaussian_blur, motion_blur, pixelate, sharpen,
    # Texture effects
    scan_lines, letterbox, vignette_simple, gradient_overlay, border,
    light_leak, progress_bar,
    # Stylization effects
    edge_detection, sketch, emboss, halftone, chromatic_aberration,
    glitch_rgb_split, crt_retro, threshold_bw, dithering,
    # Text overlay
    text_overlay,
)
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader
import cv2


def create_test_image(width: int, height: int, pattern: str = "gradient") -> np.ndarray:
    """Create a test image for demonstration."""
    if pattern == "gradient":
        # Horizontal gradient
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        for x in range(width):
            val = int(255 * x / width)
            frame[:, x] = [val, val, val]
        return frame
    elif pattern == "color_bars":
        # Color bars
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        bar_width = width // 7
        colors = [
            (255, 255, 255),  # White
            (255, 255, 0),    # Yellow
            (0, 255, 255),    # Cyan
            (0, 255, 0),      # Green
            (255, 0, 255),    # Magenta
            (255, 0, 0),      # Red
            (0, 0, 255),      # Blue
        ]
        for i, color in enumerate(colors):
            x_start = i * bar_width
            x_end = min((i + 1) * bar_width, width)
            frame[:, x_start:x_end] = color
        return frame
    else:  # checkerboard
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        square_size = 50
        for y in range(0, height, square_size):
            for x in range(0, width, square_size):
                if ((y // square_size) + (x // square_size)) % 2 == 0:
                    frame[y:y+square_size, x:x+square_size] = 255
        return frame


def save_test_images():
    """Create and save test images for the demo."""
    output_dir = Path("tests/fixtures/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test images
    gradient = create_test_image(1920, 1080, "gradient")
    color_bars = create_test_image(1920, 1080, "color_bars")
    checkerboard = create_test_image(1920, 1080, "checkerboard")
    
    # Save as PNG
    cv2.imwrite(str(output_dir / "gradient.png"), cv2.cvtColor(gradient, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(output_dir / "color_bars.png"), cv2.cvtColor(color_bars, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(output_dir / "checkerboard.png"), cv2.cvtColor(checkerboard, cv2.COLOR_RGB2BGR))
    
    print(f"✓ Test images saved to {output_dir}")


def demo_color_effects():
    """Demonstrate color effects."""
    print("\n=== Color Effects Demo ===")
    
    clips = [
        # Original
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[text_overlay("Original", position=(50, 50), font_scale=1.5)],
        ),
        # Grayscale
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                grayscale(),
                text_overlay("Grayscale", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Sepia
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                sepia(),
                text_overlay("Sepia", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Hue shift
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                hue_shift(120),
                text_overlay("Hue Shift (120°)", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Color temperature (warm)
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                color_temperature(3000),
                text_overlay("Color Temperature (Warm)", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Posterize
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                posterize(3),
                text_overlay("Posterize (3 levels)", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Invert
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                invert(),
                text_overlay("Invert", position=(50, 50), font_scale=1.5),
            ],
        ),
    ]
    
    scene = Scene(
        clips=clips,
        transitions=[Transition(TransitionType.CROSSFADE, 0.5) for _ in range(len(clips) - 1)],
        fps=30,
        resolution=(1920, 1080),
    )
    
    return scene


def demo_blur_effects():
    """Demonstrate blur effects."""
    print("\n=== Blur Effects Demo ===")
    
    clips = [
        # Original
        ImageClip(
            source="tests/fixtures/images/checkerboard.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[text_overlay("Original", position=(50, 50), font_scale=1.5)],
        ),
        # Gaussian blur
        ImageClip(
            source="tests/fixtures/images/checkerboard.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                gaussian_blur(15),
                text_overlay("Gaussian Blur", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Motion blur
        ImageClip(
            source="tests/fixtures/images/checkerboard.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                motion_blur(20, 45),
                text_overlay("Motion Blur (45°)", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Pixelate
        ImageClip(
            source="tests/fixtures/images/checkerboard.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                pixelate(20),
                text_overlay("Pixelate", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Sharpen
        ImageClip(
            source="tests/fixtures/images/checkerboard.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                sharpen(2.0),
                text_overlay("Sharpen", position=(50, 50), font_scale=1.5),
            ],
        ),
    ]
    
    scene = Scene(
        clips=clips,
        transitions=[Transition(TransitionType.CROSSFADE, 0.5) for _ in range(len(clips) - 1)],
        fps=30,
        resolution=(1920,
        1080),
    )
    
    return scene


def demo_texture_effects():
    """Demonstrate texture effects."""
    print("\n=== Texture Effects Demo ===")
    
    clips = [
        # Original
        ImageClip(
            source="tests/fixtures/images/gradient.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[text_overlay("Original", position=(50, 50), font_scale=1.5)],
        ),
        # Vignette
        ImageClip(
            source="tests/fixtures/images/gradient.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                vignette_simple(0.7),
                text_overlay("Vignette", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Scan lines
        ImageClip(
            source="tests/fixtures/images/gradient.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                scan_lines(3, 0.5),
                text_overlay("Scan Lines", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Border
        ImageClip(
            source="tests/fixtures/images/gradient.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                border(20, (255, 255, 255)),
                text_overlay("Border", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Letterbox
        ImageClip(
            source="tests/fixtures/images/gradient.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                letterbox(100, 100, (0, 0, 0)),
                text_overlay("Letterbox", position=(50, 150), font_scale=1.5),
            ],
        ),
        # Light leak
        ImageClip(
            source="tests/fixtures/images/gradient.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                light_leak(0.5),
                text_overlay("Light Leak", position=(50, 50), font_scale=1.5),
            ],
        ),
    ]
    
    scene = Scene(
        clips=clips,
        transitions=[Transition(TransitionType.CROSSFADE, 0.5) for _ in range(len(clips) - 1)],
        fps=30,
        resolution=(1920,
        1080),
    )
    
    return scene


def demo_stylization_effects():
    """Demonstrate stylization effects."""
    print("\n=== Stylization Effects Demo ===")
    
    clips = [
        # Original
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[text_overlay("Original", position=(50, 50), font_scale=1.5)],
        ),
        # Edge detection
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                edge_detection(),
                text_overlay("Edge Detection", position=(50, 50), font_scale=1.5)
            ],
        ),
        # Sketch
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                sketch(),
                text_overlay("Sketch", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Emboss
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                emboss(),
                text_overlay("Emboss", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Halftone
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                halftone(8),
                text_overlay("Halftone", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Chromatic aberration
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                chromatic_aberration(10),
                text_overlay("Chromatic Aberration", position=(50, 50), font_scale=1.5),
            ],
        ),
        # CRT retro
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                crt_retro(0.2),
                text_overlay("CRT Retro", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Threshold B&W
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                threshold_bw(128),
                text_overlay("Threshold B&W", position=(50, 50), font_scale=1.5),
            ],
        ),
    ]
    
    scene = Scene(
        clips=clips,
        transitions=[Transition(TransitionType.CROSSFADE, 0.5) for _ in range(len(clips) - 1)],
        fps=30,
        resolution=(1920,
        1080),
    )
    
    return scene


def demo_transition_effects():
    """Demonstrate advanced Phase 4 transitions."""
    print("\n=== Transition Effects Demo ===")
    
    # Create clips for transition showcase
    # We'll alternate between two distinct images to make transitions visible
    image_a = "tests/fixtures/images/color_bars.png"
    image_b = "tests/fixtures/images/checkerboard.png"
    
    clips = []
    transitions = []
    
    # Push transitions
    transitions_to_demo = [
        (TransitionType.PUSH_LEFT, "Push Left"),
        (TransitionType.PUSH_RIGHT, "Push Right"),
        (TransitionType.PUSH_UP, "Push Up"),
        (TransitionType.PUSH_DOWN, "Push Down"),
        (TransitionType.BLINDS_HORIZONTAL, "Blinds Horizontal"),
        (TransitionType.BLINDS_VERTICAL, "Blinds Vertical"),
        (TransitionType.DIAMOND_WIPE, "Diamond Wipe"),
        (TransitionType.ZOOM_THROUGH, "Zoom Through"),
        (TransitionType.WHIP_PAN, "Whip Pan"),
        (TransitionType.PIXELATE, "Pixelate"),
        (TransitionType.GLITCH, "Glitch"),
    ]
    
    # Create clips alternating between two images
    for i, (transition_type, name) in enumerate(transitions_to_demo):
        # Alternate between images
        source = image_a if i % 2 == 0 else image_b
        
        clips.append(
            ImageClip(
                source=source,
                duration=2.0,
                motion=MotionPreset.STATIC,
                effects=[text_overlay(f"Transition: {name}", position=(50, 50), font_scale=1.5)],
            )
        )
        
        # Add transition (except after last clip)
        if i < len(transitions_to_demo) - 1:
            transitions.append(Transition(transition_type, 1.0))
    
    # Add final clip
    clips.append(
        ImageClip(
            source=image_a if len(transitions_to_demo) % 2 == 0 else image_b,
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[text_overlay("End", position=(50, 50), font_scale=1.5)],
        )
    )
    
    scene = Scene(
        clips=clips,
        transitions=transitions,
        fps=30,
        resolution=(1920, 1080),
    )
    
    return scene


def demo_effect_chains():
    """Demonstrate effect chains (combining multiple effects)."""
    print("\n=== Effect Chains Demo ===")
    
    clips = [
        # Original
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[text_overlay("Original", position=(50, 50), font_scale=1.5)],
        ),
        # Cinematic look (vignette + color grading)
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                vignette_simple(0.5),
                color_temperature(6500),
                gamma_correction(1.2),
                text_overlay("Cinematic Look", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Retro look (CRT + scan lines + color shift)
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                crt_retro(0.15),
                scan_lines(2, 0.3),
                hue_shift(15),
                text_overlay("Retro Look", position=(50, 50), font_scale=1.5),
            ],
        ),
        # Dreamy look (blur + light leak + tint)
        ImageClip(
            source="tests/fixtures/images/color_bars.png",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[
                gaussian_blur(5),
                light_leak(0.4),
                tint((255, 200, 150), 0.3),
                text_overlay("Dreamy Look", position=(50, 50), font_scale=1.5),
            ],
        ),
    ]
    
    scene = Scene(
        clips=clips,
        transitions=[Transition(TransitionType.CROSSFADE, 0.5) for _ in range(len(clips) - 1)],
        fps=30,
        resolution=(1920,
        1080),
    )
    
    return scene


def render_scene_to_frames(scene: Scene, output_prefix: str):
    """Render a scene to individual frames."""
    print(f"  Rendering {output_prefix}...")
    
    image_loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, image_loader)
    renderer = FrameRenderer(timeline, image_loader)
    
    output_dir = Path("output/phase4_demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Render a few sample frames
    total_duration = sum(clip.duration for clip in scene.clips)
    sample_times = [0.0, total_duration * 0.25, total_duration * 0.5, total_duration * 0.75, total_duration - 0.1]
    
    for i, t in enumerate(sample_times):
        if t < total_duration:
            frame = renderer.render_frame(t)
            output_path = output_dir / f"{output_prefix}_frame_{i:03d}.png"
            cv2.imwrite(str(output_path), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    
    print(f"  ✓ Saved sample frames to {output_dir}")


def main():
    """Run the Phase 4 effects showcase demo."""
    print("=" * 60)
    print("Phase 4 Rich Effects Showcase Demo")
    print("=" * 60)
    
    # Create test images
    save_test_images()
    
    # Demo each category
    scenes = {
        "color_effects": demo_color_effects(),
        "blur_effects": demo_blur_effects(),
        "texture_effects": demo_texture_effects(),
        "stylization_effects": demo_stylization_effects(),
        "transition_effects": demo_transition_effects(),
        "effect_chains": demo_effect_chains(),
    }
    
    # Render sample frames from each scene
    for name, scene in scenes.items():
        render_scene_to_frames(scene, name)
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nSample frames saved to: output/phase4_demo/")
    print("\nEffect categories demonstrated:")
    print("  • Color effects (grayscale, sepia, hue shift, etc.)")
    print("  • Blur effects (gaussian, motion, pixelate, etc.)")
    print("  • Texture effects (vignette, scan lines, borders, etc.)")
    print("  • Stylization effects (edge detection, sketch, emboss, etc.)")
    print("  • Transition effects (push, blinds, diamond, zoom, whip pan, etc.)")
    print("  • Effect chains (combining multiple effects)")


if __name__ == "__main__":
    main()
