"""Test script to generate a real video with the video engine."""

from pathlib import Path

from api.library import generate_video_from_text
from config.video_config import VideoConfig
from engine.scene import ImageClip, MotionPreset, Scene
from subtitle.config import SubtitleConfig, SubtitleMode

# Create output directory
output_dir = Path("output/test_engine")
output_dir.mkdir(parents=True, exist_ok=True)

# Sample text for narration
text = """
Welcome to the video engine test. 
This demonstrates the new image composition system with motion effects.
Watch as the camera smoothly zooms and pans across the image.
"""

# Estimate audio duration (rough: ~2 seconds per sentence)
# For production, you'd generate TTS first to get exact duration
estimated_audio_duration = 12.0  # seconds

# Create a scene with the real image
# Make sure total clip duration matches or exceeds audio duration
scene = Scene(
    clips=[
        ImageClip(
            source="files/x1080.jpeg",
            duration=3.0,
            motion=MotionPreset.KEN_BURNS_ZOOM_IN
        ),
        ImageClip(
            source="files/x1080.jpeg",
            duration=3.0,
            motion=MotionPreset.PAN_LEFT
        ),
        ImageClip(
            source="files/x1080.jpeg",
            duration=6.0,  # Extended to cover remaining audio
            motion=MotionPreset.ZOOM_OUT
        ),
    ],
    resolution=(1920, 1080),
    fps=30
)

# Configure video settings
video_config = VideoConfig(
    width=1920,
    height=1080,
    fps=30,
    bg_color=(0, 0, 0)
)

# Configure subtitles
subtitle_config = SubtitleConfig(
    mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
    font_size=48,
    base_color=(255, 255, 255),
    highlight_color=(255, 255, 0),
    y_margin=0.1,
    vertical_align="bottom"
)

print("Generating video with scene...")
print(f"Scene duration: {sum(clip.duration for clip in scene.clips)} seconds")
print(f"Number of clips: {len(scene.clips)}")
print(f"Motion presets: {[clip.motion.value for clip in scene.clips]}")

# Generate the video
try:
    video_path = generate_video_from_text(
        text=text,
        output_dir=output_dir,
        video_config=video_config,
        subtitle_config=subtitle_config,
        scene=scene
    )
    
    print(f"\n✓ Video generated successfully!")
    print(f"Output: {video_path}")
    print(f"File size: {video_path.stat().st_size / (1024*1024):.2f} MB")
    
except Exception as e:
    print(f"\n✗ Error generating video: {e}")
    import traceback
    traceback.print_exc()
