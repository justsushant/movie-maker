#!/usr/bin/env python3
"""Performance benchmark for video generation pipeline.

This script measures execution time and memory usage for the video generation
pipeline to ensure the refactored code performs comparably to the original.

Usage:
    python tests/benchmark_performance.py [--runs N] [--output FILE]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.library import generate_video_from_text
from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle_config import SubtitleConfig, SubtitleMode


def measure_performance(
    text: str,
    output_dir: Path,
    run_name: str
) -> Dict[str, Any]:
    """Measure time and memory for a single video generation run.
    
    Args:
        text: Input text to generate video from
        output_dir: Directory for output files
        run_name: Name for this benchmark run
        
    Returns:
        Dictionary with timing and memory metrics
    """
    # Start memory tracking
    tracemalloc.start()
    
    # Record start time
    start_time = time.perf_counter()
    
    try:
        # Generate video
        video_path = generate_video_from_text(
            text=text,
            output_dir=output_dir,
            tts_config=TTSConfig(),
            video_config=VideoConfig(width=1280, height=720, fps=30),
            subtitle_config=SubtitleConfig(mode=SubtitleMode.SENTENCE)
        )
        
        # Record end time
        end_time = time.perf_counter()
        
        # Get memory statistics
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Calculate metrics
        elapsed_time = end_time - start_time
        
        return {
            'run_name': run_name,
            'success': True,
            'elapsed_time_seconds': elapsed_time,
            'peak_memory_mb': peak / (1024 * 1024),
            'current_memory_mb': current / (1024 * 1024),
            'video_path': str(video_path),
            'error': None
        }
        
    except Exception as e:
        tracemalloc.stop()
        return {
            'run_name': run_name,
            'success': False,
            'elapsed_time_seconds': None,
            'peak_memory_mb': None,
            'current_memory_mb': None,
            'video_path': None,
            'error': str(e)
        }


def run_benchmark_suite(
    num_runs: int = 3,
    output_file: Path | None = None
) -> Dict[str, Any]:
    """Run complete benchmark suite with multiple test cases.
    
    Args:
        num_runs: Number of times to run each test case
        output_file: Optional file to write JSON results
        
    Returns:
        Dictionary with all benchmark results
    """
    # Test cases with different text lengths
    test_cases = [
        {
            'name': 'short_sentence',
            'file': 'tests/fixtures/text/short_single_sentence.txt',
            'description': 'Single short sentence'
        },
        {
            'name': 'long_paragraph',
            'file': 'tests/fixtures/text/long_paragraph.txt',
            'description': 'Long paragraph with multiple sentences'
        },
        {
            'name': 'multi_paragraph',
            'file': 'tests/fixtures/text/multi_paragraph.txt',
            'description': 'Multiple paragraphs'
        }
    ]
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'num_runs': num_runs,
        'test_cases': []
    }
    
    print(f"\n{'='*70}")
    print(f"Video Generation Performance Benchmark")
    print(f"{'='*70}")
    print(f"\nRunning {len(test_cases)} test case(s), {num_runs} run(s) each...\n")
    
    for test_case in test_cases:
        print(f"\nTest Case: {test_case['name']}")
        print(f"Description: {test_case['description']}")
        print(f"{'─'*70}")
        
        # Read test text
        text_file = Path(test_case['file'])
        if not text_file.exists():
            print(f"  ✗ Test file not found: {text_file}")
            continue
            
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"  Text length: {len(text)} characters")
        
        # Run multiple times
        run_results = []
        for i in range(num_runs):
            print(f"  Run {i+1}/{num_runs}...", end=' ', flush=True)
            
            # Create unique output directory
            output_dir = project_root / 'output' / 'benchmark' / f"{test_case['name']}_run{i+1}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Measure performance
            result = measure_performance(
                text=text,
                output_dir=output_dir,
                run_name=f"{test_case['name']}_run{i+1}"
            )
            
            run_results.append(result)
            
            if result['success']:
                print(f"✓ {result['elapsed_time_seconds']:.2f}s, {result['peak_memory_mb']:.1f}MB peak")
            else:
                print(f"✗ Error: {result['error']}")
        
        # Calculate statistics
        successful_runs = [r for r in run_results if r['success']]
        
        if successful_runs:
            times = [r['elapsed_time_seconds'] for r in successful_runs]
            memories = [r['peak_memory_mb'] for r in successful_runs]
            
            stats = {
                'avg_time_seconds': sum(times) / len(times),
                'min_time_seconds': min(times),
                'max_time_seconds': max(times),
                'avg_memory_mb': sum(memories) / len(memories),
                'min_memory_mb': min(memories),
                'max_memory_mb': max(memories),
                'success_rate': len(successful_runs) / len(run_results)
            }
            
            print(f"\n  Statistics:")
            print(f"    Time:   avg={stats['avg_time_seconds']:.2f}s, "
                  f"min={stats['min_time_seconds']:.2f}s, "
                  f"max={stats['max_time_seconds']:.2f}s")
            print(f"    Memory: avg={stats['avg_memory_mb']:.1f}MB, "
                  f"min={stats['min_memory_mb']:.1f}MB, "
                  f"max={stats['max_memory_mb']:.1f}MB")
        else:
            stats = None
            print(f"\n  ✗ All runs failed")
        
        results['test_cases'].append({
            'name': test_case['name'],
            'description': test_case['description'],
            'text_length': len(text),
            'runs': run_results,
            'statistics': stats
        })
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"Summary")
    print(f"{'='*70}\n")
    
    for test_case in results['test_cases']:
        if test_case['statistics']:
            stats = test_case['statistics']
            print(f"{test_case['name']:20s} | "
                  f"Time: {stats['avg_time_seconds']:6.2f}s | "
                  f"Memory: {stats['avg_memory_mb']:6.1f}MB")
    
    # Write results to file if requested
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results written to: {output_file}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark video generation performance"
    )
    parser.add_argument(
        '--runs',
        type=int,
        default=3,
        help='Number of runs per test case (default: 3)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help='Output file for JSON results (optional)'
    )
    
    args = parser.parse_args()
    
    # Run benchmark suite
    results = run_benchmark_suite(
        num_runs=args.runs,
        output_file=args.output
    )
    
    # Check if all tests succeeded
    all_success = all(
        tc['statistics'] is not None and tc['statistics']['success_rate'] == 1.0
        for tc in results['test_cases']
    )
    
    if all_success:
        print(f"\n✓ All benchmarks completed successfully")
        sys.exit(0)
    else:
        print(f"\n✗ Some benchmarks failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
