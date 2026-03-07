#!/usr/bin/env python3
"""Profile the video generation pipeline to identify bottlenecks.

This script uses cProfile to analyze the performance characteristics of the
refactored codebase and identify any bottlenecks or optimization opportunities.

Usage:
    python tests/profile_pipeline.py [--text-file FILE] [--output-dir DIR]
"""

from __future__ import annotations

import argparse
import cProfile
import pstats
import sys
from io import StringIO
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.library import generate_video_from_text
from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle_config import SubtitleConfig, SubtitleMode


def profile_video_generation(
    text: str,
    output_dir: Path,
    profile_output: Path | None = None
) -> pstats.Stats:
    """Profile a single video generation run.
    
    Args:
        text: Input text to generate video from
        output_dir: Directory for output files
        profile_output: Optional file to write profile data
        
    Returns:
        pstats.Stats object with profiling results
    """
    # Create profiler
    profiler = cProfile.Profile()
    
    # Profile the video generation
    profiler.enable()
    
    video_path = generate_video_from_text(
        text=text,
        output_dir=output_dir,
        tts_config=TTSConfig(),
        video_config=VideoConfig(width=1280, height=720, fps=30),
        subtitle_config=SubtitleConfig(mode=SubtitleMode.SENTENCE)
    )
    
    profiler.disable()
    
    # Create stats object
    stats = pstats.Stats(profiler)
    
    # Save raw profile data if requested
    if profile_output:
        profiler.dump_stats(str(profile_output))
        print(f"\n✓ Raw profile data saved to: {profile_output}")
    
    return stats


def print_profile_report(stats: pstats.Stats, top_n: int = 30):
    """Print formatted profile report.
    
    Args:
        stats: Profile statistics
        top_n: Number of top functions to display
    """
    print(f"\n{'='*80}")
    print(f"Profile Report - Top {top_n} Functions by Cumulative Time")
    print(f"{'='*80}\n")
    
    # Sort by cumulative time and print top functions
    stats.sort_stats('cumulative')
    stats.print_stats(top_n)
    
    print(f"\n{'='*80}")
    print(f"Profile Report - Top {top_n} Functions by Total Time")
    print(f"{'='*80}\n")
    
    # Sort by total time and print top functions
    stats.sort_stats('tottime')
    stats.print_stats(top_n)


def analyze_bottlenecks(stats: pstats.Stats) -> dict:
    """Analyze profile data to identify bottlenecks.
    
    Args:
        stats: Profile statistics
        
    Returns:
        Dictionary with bottleneck analysis
    """
    # Get stats as string for parsing
    stream = StringIO()
    ps = pstats.Stats(stats.stats, stream=stream)
    ps.sort_stats('cumulative')
    
    # Analyze key components
    analysis = {
        'tts_time': 0.0,
        'processing_time': 0.0,
        'rendering_time': 0.0,
        'io_time': 0.0,
        'other_time': 0.0
    }
    
    for func, (cc, nc, tt, ct, callers) in stats.stats.items():
        filename, line, func_name = func
        
        # Categorize by component
        if 'kokoro' in filename.lower() or 'tts' in filename.lower():
            analysis['tts_time'] += ct
        elif 'punctuation' in filename.lower() or 'grouping' in filename.lower() or 'processing' in filename.lower():
            analysis['processing_time'] += ct
        elif 'render' in filename.lower() or 'moviepy' in filename.lower() or 'subtitle' in filename.lower():
            analysis['rendering_time'] += ct
        elif 'soundfile' in filename.lower() or any(io_op in func_name for io_op in ['write', 'read', 'open', 'dump']):
            analysis['io_time'] += ct
        else:
            analysis['other_time'] += ct
    
    return analysis


def print_bottleneck_analysis(analysis: dict):
    """Print bottleneck analysis report.
    
    Args:
        analysis: Bottleneck analysis dictionary
    """
    print(f"\n{'='*80}")
    print(f"Bottleneck Analysis - Time by Component")
    print(f"{'='*80}\n")
    
    total_time = sum(analysis.values())
    
    # Sort by time descending
    sorted_components = sorted(analysis.items(), key=lambda x: x[1], reverse=True)
    
    for component, time_spent in sorted_components:
        percentage = (time_spent / total_time * 100) if total_time > 0 else 0
        print(f"  {component:20s}: {time_spent:8.3f}s ({percentage:5.1f}%)")
    
    print(f"\n  {'Total':20s}: {total_time:8.3f}s (100.0%)")
    
    # Identify primary bottleneck
    if sorted_components:
        primary_bottleneck = sorted_components[0]
        print(f"\n  Primary bottleneck: {primary_bottleneck[0]} ({primary_bottleneck[1]:.3f}s)")


def main():
    parser = argparse.ArgumentParser(
        description="Profile video generation pipeline for bottlenecks"
    )
    parser.add_argument(
        '--text-file',
        type=Path,
        default=Path('tests/fixtures/text/long_paragraph.txt'),
        help='Input text file to profile (default: long_paragraph.txt)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('output/profile'),
        help='Output directory for generated video (default: output/profile)'
    )
    parser.add_argument(
        '--profile-output',
        type=Path,
        default=None,
        help='File to save raw profile data (optional)'
    )
    parser.add_argument(
        '--top-n',
        type=int,
        default=30,
        help='Number of top functions to display (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Read input text
    if not args.text_file.exists():
        print(f"✗ Error: Text file not found: {args.text_file}")
        sys.exit(1)
    
    with open(args.text_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"\n{'='*80}")
    print(f"Profiling Video Generation Pipeline")
    print(f"{'='*80}")
    print(f"\nInput file: {args.text_file}")
    print(f"Text length: {len(text)} characters")
    print(f"Output directory: {args.output_dir}")
    print(f"\nRunning profiler...")
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Profile the pipeline
    stats = profile_video_generation(
        text=text,
        output_dir=args.output_dir,
        profile_output=args.profile_output
    )
    
    # Print detailed profile report
    print_profile_report(stats, top_n=args.top_n)
    
    # Analyze and print bottlenecks
    analysis = analyze_bottlenecks(stats)
    print_bottleneck_analysis(analysis)
    
    print(f"\n{'='*80}")
    print(f"Profiling Complete")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
