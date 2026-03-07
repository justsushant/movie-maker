#!/usr/bin/env python3
"""
Generate a video from Nietzsche's Overman text in two stages:
1. Generate audio and subtitle data
2. Render the final video

This demonstrates how to use the library's components separately for
more control over the pipeline.
"""

from pathlib import Path

from tts.config import TTSConfig
from tts.kokoro_engine import KokoroTTSEngine
from config.video_config import VideoConfig
from subtitle.config import SubtitleConfig
from processing.punctuation import PunctuationMerger
from processing.grouping import SentenceGrouper
from io_adapters.implementations import FileAudioWriter, JsonMetadataWriter
from pipeline.orchestrator import TTSPipeline
from rendering.video import create_video


# The text to convert to video
text = """
Foes and false friends are all around me, Lord Davos. 

They infest my city like roaches, and at night I feel them crawling over me.
The fat man's fingers coiled into a fist, and all his chins trembled. 
My son Wendel came to the Twins a guest. He ate Lord Walder's bread and salt, and hung his sword upon the wall to feast with his friends. And they murdered him. Murdered, I say, and may the Freys choke upon their fables. I drink with Jared, jape with Symond, promise Rhaegar the hand of my own beloved granddaughter…but never think that means I have forgotten. The north remembers, Lord Davos. The north remembers, and the mummer's farce is almost done. My son is home.
"""


def stage_1_generate_audio_and_subtitles(output_dir: Path):
    """
    Stage 1: Generate TTS audio and subtitle timing data.
    
    This stage:
    - Converts text to speech using Kokoro TTS
    - Extracts word-level timing information
    - Merges punctuation into words
    - Groups words into sentence segments
    - Writes audio (WAV) and subtitle data (JSON)
    """
    print("=" * 60)
    print("STAGE 1: Generating audio and subtitle data")
    print("=" * 60)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define output file paths
    audio_file = output_dir / "output_moviepy.wav"
    json_file = output_dir / "output_moviepy.json"
    
    # Configure TTS (American English, af_heart voice, normal speed)
    tts_config = TTSConfig()
    
    # Instantiate pipeline components
    tts_engine = KokoroTTSEngine(tts_config)
    punctuation_merger = PunctuationMerger()
    sentence_grouper = SentenceGrouper()
    audio_writer = FileAudioWriter(audio_file)
    metadata_writer = JsonMetadataWriter(json_file)
    
    # Create and run TTS pipeline
    pipeline = TTSPipeline(
        tts_engine=tts_engine,
        punctuation_merger=punctuation_merger,
        sentence_grouper=sentence_grouper,
        audio_writer=audio_writer,
        metadata_writer=metadata_writer
    )
    
    print(f"Processing text ({len(text)} characters)...")
    sentences = pipeline.process(text)
    
    print(f"\n✓ Audio generated: {audio_file}")
    print(f"✓ Subtitle data generated: {json_file}")
    print(f"  - {len(sentences)} sentence segments")
    total_words = sum(len(s.words) for s in sentences)
    print(f"  - {total_words} words with timing data")
    
    return audio_file, json_file


def stage_2_render_video(output_dir: Path, audio_file: Path, json_file: Path):
    """
    Stage 2: Render the final video with subtitles.
    
    This stage:
    - Loads the pre-generated audio and subtitle data
    - Composites subtitle frames over the audio
    - Exports the final MP4 video
    """
    print("\n" + "=" * 60)
    print("STAGE 2: Rendering video with subtitles")
    print("=" * 60)
    
    video_file = output_dir / "output_video.mp4"
    
    # Configure video settings for phone (vertical format: 1080x1920)
    video_config = VideoConfig(width=1080, height=1920)
    subtitle_config = SubtitleConfig()
    
    # Build config dict for renderer
    renderer_config = {
        "json_file": str(json_file),
        "audio_file": str(audio_file),
        "output_video": str(video_file),
        "width": video_config.width,
        "height": video_config.height,
        "fps": video_config.fps,
        "bg_color": video_config.bg_color,
        "subtitle": subtitle_config.to_dict(),
    }
    
    # Render video
    create_video(
        renderer_config,
        subtitle_source=None,  # Will use JsonSubtitleSource from json_file
        layout=None,  # Will be chosen based on subtitle_config.mode
        renderer=None  # Will use PillowSubtitleRenderer
    )
    
    print(f"\n✓ Video rendered: {video_file}")
    
    return video_file


if __name__ == "__main__":
    # Output directory for this video
    output_dir = Path("output/overman_staged")
    
    print("Starting staged video generation...")
    print(f"Output directory: {output_dir}\n")
    
    # Stage 1: Generate audio and subtitle data
    audio_file, json_file = stage_1_generate_audio_and_subtitles(output_dir)
    
    # At this point, you could:
    # - Inspect or modify the subtitle JSON
    # - Process the audio file
    # - Wait before rendering
    # - Render with different settings
    
    # Stage 2: Render the final video
    video_path = stage_2_render_video(output_dir, audio_file, json_file)
    
    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)
    print(f"\nAll files in {output_dir}:")
    print(f"  - {audio_file.name} (audio)")
    print(f"  - {json_file.name} (subtitle timing data)")
    print(f"  - {video_path.name} (final video)")
