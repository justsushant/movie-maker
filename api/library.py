"""
Library API for generating narrated videos from text.

This module provides the main entry points for the movie-maker library,
offering a clean, library-first API for programmatic video generation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any, TYPE_CHECKING

from tts.config import TTSConfig
from tts.kokoro_engine import KokoroTTSEngine
from config.video_config import VideoConfig
from subtitle.config import SubtitleConfig
from processing.punctuation import PunctuationMerger
from processing.grouping import SentenceGrouper
from io_adapters.implementations import FileAudioWriter, JsonMetadataWriter
from pipeline.orchestrator import TTSPipeline
from rendering.video import create_video

if TYPE_CHECKING:
    from engine.scene import Scene


def generate_video_from_text(
    text: str,
    output_dir: Path,
    tts_config: Optional[TTSConfig] = None,
    video_config: Optional[VideoConfig] = None,
    subtitle_config: Optional[SubtitleConfig] = None,
    scene: Optional['Scene'] = None,
) -> Path:
    """
    Generate a narrated video from text.
    
    This is the main library entry point for generating videos from text input.
    It orchestrates the complete pipeline: TTS generation → text processing →
    video rendering with subtitles.
    
    All configuration is optional and will use sensible defaults if not provided.
    The function creates all necessary output files in the specified output
    directory.
    
    Args:
        text: Input text to narrate
        output_dir: Directory for output files (will be created if it doesn't exist)
        tts_config: TTS configuration (uses defaults if None: American English,
                   af_heart voice, 1.0 speed)
        video_config: Video configuration (uses defaults if None: 1920x1080,
                     30fps, black background)
        subtitle_config: Subtitle configuration (uses defaults if None:
                        sentence_with_word_highlight mode, white/yellow colors)
        scene: Optional Scene with image clips and motion effects. If provided,
               generates video with image sequences. If None, uses solid background.
        
    Returns:
        Path to the generated video file
        
    Raises:
        Exception: If TTS generation, processing, or rendering fails
        
    Example:
        >>> from pathlib import Path
        >>> from api.library import generate_video_from_text
        >>> 
        >>> text = "Hello world! This is a test."
        >>> output_dir = Path("output/my_video")
        >>> video_path = generate_video_from_text(text, output_dir)
        >>> print(f"Video created at: {video_path}")
        
        >>> # With Scene for image sequence
        >>> from engine import Scene, ImageClip, MotionPreset
        >>> scene = Scene(
        ...     clips=[
        ...         ImageClip("image1.jpg", duration=3.0, motion=MotionPreset.KEN_BURNS_ZOOM_IN),
        ...         ImageClip("image2.jpg", duration=3.0, motion=MotionPreset.PAN_LEFT),
        ...     ]
        ... )
        >>> video_path = generate_video_from_text(text, output_dir, scene=scene)
    """
    # Use defaults if not provided
    tts_config = tts_config or TTSConfig()
    video_config = video_config or VideoConfig()
    subtitle_config = subtitle_config or SubtitleConfig()
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define output file paths (using legacy naming for backward compatibility)
    audio_file = output_dir / "output_moviepy.wav"
    json_file = output_dir / "output_moviepy.json"
    video_file = output_dir / "output_video.mp4"
    
    # Instantiate pipeline components with dependency injection
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
    
    print("Generating TTS audio and processing text...")
    pipeline.process(text)
    
    # Build config dict for renderer (maintains backward compatibility)
    # Use scene resolution/fps if provided, otherwise use video_config
    if scene is not None:
        width = scene.resolution[0]
        height = scene.resolution[1]
        fps = scene.fps
    else:
        width = video_config.width
        height = video_config.height
        fps = video_config.fps
    
    renderer_config: Dict[str, Any] = {
        "json_file": str(json_file),
        "audio_file": str(audio_file),
        "output_video": str(video_file),
        "width": width,
        "height": height,
        "fps": fps,
        "bg_color": video_config.bg_color,
        # FIX: Properly pass subtitle configuration
        "subtitle": subtitle_config.to_dict(),
    }
    
    # Render video with subtitles
    print("Rendering video with subtitles...")
    create_video(
        renderer_config,
        subtitle_source=None,  # Will use JsonSubtitleSource from json_file
        layout=None,  # Will be chosen based on subtitle_config.mode
        renderer=None,  # Will use PillowSubtitleRenderer
        scene=scene,  # Pass scene through to enable engine rendering
    )
    
    return video_file


def generate_video_from_file(
    input_file: Path,
    output_dir: Path,
    tts_config: Optional[TTSConfig] = None,
    video_config: Optional[VideoConfig] = None,
    subtitle_config: Optional[SubtitleConfig] = None,
    scene: Optional['Scene'] = None,
) -> Path:
    """
    Generate a narrated video from a text file.
    
    This is a convenience wrapper around generate_video_from_text() that reads
    the input text from a file. It's useful for CLI applications and batch
    processing workflows.
    
    Args:
        input_file: Path to input text file (UTF-8 encoded)
        output_dir: Directory for output files (will be created if it doesn't exist)
        tts_config: TTS configuration (uses defaults if None)
        video_config: Video configuration (uses defaults if None)
        subtitle_config: Subtitle configuration (uses defaults if None)
        scene: Optional Scene with image clips and motion effects
        
    Returns:
        Path to the generated video file
        
    Raises:
        FileNotFoundError: If input_file doesn't exist
        Exception: If TTS generation, processing, or rendering fails
        
    Example:
        >>> from pathlib import Path
        >>> from api.library import generate_video_from_file
        >>> 
        >>> input_file = Path("files/input.txt")
        >>> output_dir = Path("output/my_video")
        >>> video_path = generate_video_from_file(input_file, output_dir)
        >>> print(f"Video created at: {video_path}")
    """
    input_file = Path(input_file)
    
    # Read text from file
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Delegate to generate_video_from_text
    return generate_video_from_text(
        text=text,
        output_dir=output_dir,
        tts_config=tts_config,
        video_config=video_config,
        subtitle_config=subtitle_config,
        scene=scene,
    )
