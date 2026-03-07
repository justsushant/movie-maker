#!/usr/bin/env python3
"""Profile video generation pipeline to identify bottlenecks.

This script uses cProfile to analyze where time is spent during video generation.

Usage:
    python tests/profile_performance.py
"""

from __future__ import annotations

import cProfile
import pstats
import sys
from pathlib import Path
from io import StringIO

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.library import generate_video_from_text
from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle_config import SubtitleConfig, SubtitleMode


def profile_video_generation():
    """Profile a single video generation run."""
    # Use short text for faster profiling
    text = "Hello world! This is a test."
    output_dir = project_root / 'output' / 'profile_test'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate video
    generate_video_from_text(
        text=text,
        output_dir=output_dir,
        tts_config=TTSConfig(),
        video_config=VideoConfig(width=1280, height=720, fps=30),
        subtitle_config=SubtitleConfig(mode=SubtitleMode.SENTENCE)
    )


def main():
    print("Profiling video generation pipeline...")
    print("=" * 70)
    
    # Create profiler
    profiler = cProfile.Profile()
    
    # Run with profiling
    profiler.enable()
    profile_video_generation()
    profiler.disable()
    
    # Analyze results
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    
    # Sort by cumulative time
    stats.sort_stats('cumulative')
    
    print("\nTop 30 functions by cumulative time:")
    print("=" * 70)
    stats.print_stats(30)
    
    # Sort by total time
    stats.sort_stats('tottime')
    
    print("\nTop 30 functions by total time:")
    print("=" * 70)
    stats.print_stats(30)
    
    # Save detailed profile
    output_file = project_root / 'output' / 'profile_stats.txt'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        stats = pstats.Stats(profiler, stream=f)
        stats.sort_stats('cumulative')
        stats.print_stats()
    
    print(f"\n✓ Detailed profile saved to: {output_file}")
    print("\nProfile complete!")


if __name__ == '__main__':
    main()
