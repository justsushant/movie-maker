"""
Phase 3 Audio-Reactive Video Demo

This example demonstrates Phase 3 audio-reactive features:
- Beat-synchronized transitions
- Onset-triggered flash effects
- Energy-driven zoom and brightness
- Spectral color shifting

The demo creates a video where visuals respond dynamically to audio features.
"""

from pathlib import Path
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType, BeatSync
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader
from engine.effects import (
    OnsetFlash, OnsetZoomPulse, EnergyZoom, EnergyBrightness,
    EnergyShake, SpectralColorShift, brightness, vignette, chain_effects
)
from moviepy.editor import ImageSequenceClip, AudioFileClip
import numpy as np


def create_test_images():
    """Create test images if they don't exist."""
    images_dir = Path("examples/images")
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Create simple colored images for testing
    from PIL import Image
    
    colors = [
        (100, 150, 200),  # Blue
        (200, 100, 150),  # Pink
        (150, 200, 100),  # Green
        (200, 150, 100),  # Orange
    ]
    
    for i, color in enumerate(colors):
        img_path = images_dir / f"test_image_{i+1}.jpg"
        if not img_path.exists():
            img = Image.new('RGB', (1920, 1080), color)
            img.save(img_path, quality=95)
            print(f"Created {img_path}")


def create_test_audio():
    """Create a simple test audio file with beats."""
    audio_path = Path("examples/audio/test_beat.wav")
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    
    if audio_path.exists():
        return audio_path
    
    # Create a simple audio file with clear beats
    import soundfile as sf
    
    duration = 10.0  # seconds
    sr = 22050
    t = np.linspace(0, duration, int(sr * duration))
    
    # Create a beat pattern (120 BPM = 2 beats per second)
    beat_freq = 2.0  # Hz
    
    # Bass drum on beats
    bass = np.sin(2 * np.pi * 60 * t) * np.exp(-10 * (t % (1/beat_freq)))
    
    # Hi-hat on eighth notes
    hihat = np.random.randn(len(t)) * 0.1 * np.exp(-50 * (t % (1/(beat_freq*2))))
    
    # Melody
    melody_freq = 440 * (1 + 0.2 * np.sin(2 * np.pi * 0.5 * t))
    melody = 0.3 * np.sin(2 * np.pi * melody_freq * t)
    
    # Mix
    audio = bass + hihat + melody
    audio = audio / np.max(np.abs(audio)) * 0.8  # Normalize
    
    sf.write(audio_path, audio, sr)
    print(f"Created test audio: {audio_path}")
    
    return audio_path


def demo_basic_audio_reactive():
    """Demo 1: Basic audio-reactive video with beat sync and onset flash."""
    print("\n=== Demo 1: Basic Audio-Reactive Video ===")
    
    # Create test assets
    create_test_images()
    audio_path = create_test_audio()
    
    # Create scene with audio
    scene = Scene(
        clips=[
            ImageClip(
                source="examples/images/test_image_1.jpg",
                duration=2.5,
                motion=MotionPreset.KEN_BURNS_ZOOM_IN
            ),
            ImageClip(
                source="examples/images/test_image_2.jpg",
                duration=2.5,
                motion=MotionPreset.PAN_LEFT
            ),
            ImageClip(
                source="examples/images/test_image_3.jpg",
                duration=2.5,
                motion=MotionPreset.ZOOM_OUT
            ),
            ImageClip(
                source="examples/images/test_image_4.jpg",
                duration=2.5,
                motion=MotionPreset.PAN_RIGHT
            ),
        ],
        transitions=[
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.5,
                sync=BeatSync.NEAREST_BEAT  # Snap to nearest beat
            ),
            Transition(
                type=TransitionType.SLIDE_LEFT,
                duration=0.5,
                sync=BeatSync.NEAREST_BEAT
            ),
            Transition(
                type=TransitionType.IRIS_OPEN,
                duration=0.5,
                sync=BeatSync.NEAREST_BEAT
            ),
        ],
        audio=str(audio_path),
        resolution=(1920, 1080),
        fps=30
    )
    
    # Plan scene (analyzes audio)
    print("Planning scene and analyzing audio...")
    planner = ScenePlanner()
    timeline = planner.plan(scene)
    
    if timeline.audio_sync is None:
        print("Warning: Audio analysis failed, continuing without audio features")
        return
    
    print(f"Audio analysis complete:")
    print(f"  - Beats detected: {len(timeline.audio_sync.beats)}")
    print(f"  - Onsets detected: {len(timeline.audio_sync.onsets)}")
    print(f"  - Energy samples: {len(timeline.audio_sync.energy_times)}")
    
    # Add audio-reactive effects to clips
    onset_flash = OnsetFlash(
        audio_sync=timeline.audio_sync,
        flash_duration=0.2,
        intensity=0.5
    )
    
    for clip in timeline.clips:
        clip.effects.append(onset_flash)
    
    # Render frames
    print("Rendering frames with audio-reactive effects...")
    image_loader = ImageLoader()
    renderer = FrameRenderer(timeline, image_loader)
    
    frames = []
    total_frames = int(timeline.total_duration * scene.fps)
    
    for frame_idx in range(total_frames):
        if frame_idx % 30 == 0:
            print(f"  Frame {frame_idx}/{total_frames}")
        t = frame_idx / scene.fps
        frame = renderer.render_frame(t)
        frames.append(frame)
    
    # Export video
    output_path = Path("output/demo_phase3_basic.mp4")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("Encoding video...")
    video_clip = ImageSequenceClip(frames, fps=scene.fps)
    audio_clip = AudioFileClip(str(audio_path))
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(str(output_path), codec='libx264', audio_codec='aac')
    
    print(f"✓ Video saved: {output_path}")


def demo_advanced_audio_reactive():
    """Demo 2: Advanced audio-reactive video with multiple effects."""
    print("\n=== Demo 2: Advanced Audio-Reactive Video ===")
    
    # Create test assets
    create_test_images()
    audio_path = create_test_audio()
    
    # Create scene
    scene = Scene(
        clips=[
            ImageClip(
                source="examples/images/test_image_1.jpg",
                duration=2.5,
                motion=MotionPreset.STATIC
            ),
            ImageClip(
                source="examples/images/test_image_2.jpg",
                duration=2.5,
                motion=MotionPreset.STATIC
            ),
            ImageClip(
                source="examples/images/test_image_3.jpg",
                duration=2.5,
                motion=MotionPreset.STATIC
            ),
            ImageClip(
                source="examples/images/test_image_4.jpg",
                duration=2.5,
                motion=MotionPreset.STATIC
            ),
        ],
        transitions=[
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.5,
                sync=BeatSync.BEAT_GRID  # Rhythm-locked
            ),
            Transition(
                type=TransitionType.SLIDE_LEFT,
                duration=0.5,
                sync=BeatSync.BEAT_GRID
            ),
            Transition(
                type=TransitionType.ZOOM_THROUGH,
                duration=0.5,
                sync=BeatSync.BEAT_GRID
            ),
        ],
        audio=str(audio_path),
        resolution=(1920, 1080),
        fps=30
    )
    
    # Plan scene
    print("Planning scene and analyzing audio...")
    planner = ScenePlanner()
    timeline = planner.plan(scene)
    
    if timeline.audio_sync is None:
        print("Warning: Audio analysis failed, continuing without audio features")
        return
    
    print(f"Audio analysis complete:")
    print(f"  - Beats: {len(timeline.audio_sync.beats)}")
    print(f"  - Onsets: {len(timeline.audio_sync.onsets)}")
    
    # Create multiple audio-reactive effects
    onset_flash = OnsetFlash(
        audio_sync=timeline.audio_sync,
        flash_duration=0.15,
        intensity=0.6
    )
    
    onset_zoom = OnsetZoomPulse(
        audio_sync=timeline.audio_sync,
        pulse_duration=0.25,
        zoom_magnitude=1.08
    )
    
    energy_zoom = EnergyZoom(
        audio_sync=timeline.audio_sync,
        zoom_range=(1.0, 1.15),
        energy_range=(0.0, 0.8)
    )
    
    energy_brightness = EnergyBrightness(
        audio_sync=timeline.audio_sync,
        brightness_range=(0.9, 1.1),
        energy_range=(0.0, 0.8)
    )
    
    spectral_color = SpectralColorShift(
        audio_sync=timeline.audio_sync,
        temperature_range=(-0.15, 0.15),
        centroid_range=(1000.0, 3000.0)
    )
    
    # Add effects to different clips
    timeline.clips[0].effects.extend([onset_flash, energy_brightness, vignette(0.3)])
    timeline.clips[1].effects.extend([onset_zoom, energy_zoom, brightness(0.05)])
    timeline.clips[2].effects.extend([onset_flash, spectral_color, vignette(0.4)])
    timeline.clips[3].effects.extend([onset_zoom, energy_brightness, energy_zoom])
    
    # Render
    print("Rendering frames with multiple audio-reactive effects...")
    image_loader = ImageLoader()
    renderer = FrameRenderer(timeline, image_loader)
    
    frames = []
    total_frames = int(timeline.total_duration * scene.fps)
    
    for frame_idx in range(total_frames):
        if frame_idx % 30 == 0:
            print(f"  Frame {frame_idx}/{total_frames}")
        t = frame_idx / scene.fps
        frame = renderer.render_frame(t)
        frames.append(frame)
    
    # Export
    output_path = Path("output/demo_phase3_advanced.mp4")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("Encoding video...")
    video_clip = ImageSequenceClip(frames, fps=scene.fps)
    audio_clip = AudioFileClip(str(audio_path))
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(str(output_path), codec='libx264', audio_codec='aac')
    
    print(f"✓ Video saved: {output_path}")


def demo_graceful_degradation():
    """Demo 3: Graceful degradation without audio."""
    print("\n=== Demo 3: Graceful Degradation (No Audio) ===")
    
    create_test_images()
    
    # Create scene WITHOUT audio
    scene = Scene(
        clips=[
            ImageClip(
                source="examples/images/test_image_1.jpg",
                duration=2.0,
                motion=MotionPreset.KEN_BURNS_ZOOM_IN
            ),
            ImageClip(
                source="examples/images/test_image_2.jpg",
                duration=2.0,
                motion=MotionPreset.PAN_LEFT
            ),
        ],
        transitions=[
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.5,
                sync=BeatSync.NEAREST_BEAT  # Will be ignored without audio
            ),
        ],
        audio=None,  # No audio
        resolution=(1920, 1080),
        fps=30
    )
    
    # Plan scene
    print("Planning scene without audio...")
    planner = ScenePlanner()
    timeline = planner.plan(scene)
    
    print(f"AudioSync: {timeline.audio_sync}")  # Should be None
    
    # Create audio-reactive effects with None AudioSync
    # These should gracefully return frames unchanged
    onset_flash = OnsetFlash(audio_sync=None, flash_duration=0.2, intensity=0.5)
    energy_zoom = EnergyZoom(audio_sync=None, zoom_range=(1.0, 1.2))
    
    for clip in timeline.clips:
        clip.effects.extend([onset_flash, energy_zoom, brightness(0.1)])
    
    # Render
    print("Rendering frames (audio-reactive effects will be inactive)...")
    image_loader = ImageLoader()
    renderer = FrameRenderer(timeline, image_loader)
    
    frames = []
    total_frames = int(timeline.total_duration * scene.fps)
    
    for frame_idx in range(total_frames):
        t = frame_idx / scene.fps
        frame = renderer.render_frame(t)
        frames.append(frame)
    
    # Export
    output_path = Path("output/demo_phase3_no_audio.mp4")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("Encoding video...")
    video_clip = ImageSequenceClip(frames, fps=scene.fps)
    video_clip.write_videofile(str(output_path), codec='libx264')
    
    print(f"✓ Video saved: {output_path}")
    print("Note: Audio-reactive effects were inactive (graceful degradation)")


if __name__ == "__main__":
    print("Phase 3 Audio-Reactive Video Demos")
    print("=" * 50)
    
    try:
        import librosa
        print("✓ librosa is installed")
    except ImportError:
        print("✗ librosa is not installed")
        print("  Install with: pip install librosa")
        print("  Demos will run but audio features will be disabled")
    
    # Run demos
    demo_basic_audio_reactive()
    demo_advanced_audio_reactive()
    demo_graceful_degradation()
    
    print("\n" + "=" * 50)
    print("All demos complete!")
    print("Check output/ directory for generated videos")
