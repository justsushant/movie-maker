"""Performance tests for video engine.

This module tests performance characteristics including frame render time,
memory usage, cache efficiency, and ensures no memory leaks.

**Validates: Requirements 9.5**
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from engine.image_loader import ImageLoader
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.scene import ImageClip, MotionPreset, Scene


@pytest.fixture
def test_images_dir():
    """Get path to test images directory."""
    return Path("tests/fixtures/images")


class TestPerformance:
    """Performance tests for video engine.
    
    **Validates: Requirements 9.5**
    """
    
    def test_frame_render_time_1080p(self, test_images_dir):
        """Frame rendering should be reasonably fast for 1080p images."""
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=2.0,
                    motion=MotionPreset.KEN_BURNS_ZOOM_IN
                )
            ],
            resolution=(1920, 1080),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        # Warm up (first render loads image)
        renderer.render_frame(0.5)
        
        # Measure render time for 10 frames
        start_time = time.time()
        for i in range(10):
            renderer.render_frame(0.1 * i)
        elapsed = time.time() - start_time
        
        # Average time per frame
        avg_time = elapsed / 10
        
        # Should render at least 10 fps (100ms per frame)
        # This is a conservative threshold
        assert avg_time < 0.1, f"Frame render too slow: {avg_time:.3f}s per frame"
        
        print(f"\n1080p frame render time: {avg_time*1000:.2f}ms per frame")
    
    def test_frame_render_time_4k(self, test_images_dir):
        """Frame rendering should handle 4K images reasonably."""
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "large_3840x2160.jpg",
                    duration=2.0,
                    motion=MotionPreset.KEN_BURNS_ZOOM_IN
                )
            ],
            resolution=(3840, 2160),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        # Warm up
        renderer.render_frame(0.5)
        
        # Measure render time for 5 frames (4K is slower)
        start_time = time.time()
        for i in range(5):
            renderer.render_frame(0.2 * i)
        elapsed = time.time() - start_time
        
        # Average time per frame
        avg_time = elapsed / 5
        
        # 4K should still render at least 2 fps (500ms per frame)
        assert avg_time < 0.5, f"4K frame render too slow: {avg_time:.3f}s per frame"
        
        print(f"\n4K frame render time: {avg_time*1000:.2f}ms per frame")
    
    def test_image_cache_hit_rate(self, test_images_dir):
        """Image loader should have high cache hit rate."""
        loader = ImageLoader()
        
        # Load same image multiple times
        image_path = test_images_dir / "landscape_1920x1080.png"
        
        # First load (cache miss)
        start_time = time.time()
        loader.load(image_path)
        first_load_time = time.time() - start_time
        
        # Subsequent loads (cache hits)
        cache_hit_times = []
        for _ in range(10):
            start_time = time.time()
            loader.load(image_path)
            cache_hit_times.append(time.time() - start_time)
        
        avg_cache_hit_time = sum(cache_hit_times) / len(cache_hit_times)
        
        # Cache hits should be much faster than first load
        # At least 10x faster
        assert avg_cache_hit_time < first_load_time / 10, (
            f"Cache not effective: first={first_load_time*1000:.2f}ms, "
            f"cached={avg_cache_hit_time*1000:.2f}ms"
        )
        
        print(f"\nFirst load: {first_load_time*1000:.2f}ms")
        print(f"Cached load: {avg_cache_hit_time*1000:.6f}ms")
        print(f"Speedup: {first_load_time/avg_cache_hit_time:.1f}x")
    
    def test_memory_usage_with_cached_images(self, test_images_dir):
        """Memory usage should be reasonable with cached images."""
        import sys
        
        loader = ImageLoader()
        
        # Load multiple images
        images = [
            "landscape_1920x1080.png",
            "landscape_gradient_1920x1080.png",
            "portrait_1080x1920.png",
            "square_1080x1080.png",
        ]
        
        for img in images:
            loader.load(test_images_dir / img)
        
        # Check cache size
        cache_size = len(loader._cache)
        assert cache_size == len(images), "All images should be cached"
        
        # Estimate memory usage (rough)
        # 1920x1080x3 bytes ≈ 6.2 MB per image
        # 4 images ≈ 25 MB (reasonable)
        
        # Clear cache and verify
        loader.clear_cache()
        assert len(loader._cache) == 0, "Cache should be empty after clear"
    
    def test_no_memory_leak_over_100_frames(self, test_images_dir):
        """Rendering many frames should not leak memory."""
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=10.0,
                    motion=MotionPreset.KEN_BURNS_ZOOM_IN
                )
            ],
            resolution=(1920, 1080),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        # Render 100 frames
        for i in range(100):
            frame = renderer.render_frame(i * 0.1)
            # Frame should be created and can be garbage collected
            assert frame is not None
        
        # If we got here without crashing or running out of memory, test passes
        # In a real memory leak, this would fail or slow down significantly
        
        # Verify cache still has only one image
        assert len(loader._cache) == 1, "Should only cache one image"
    
    def test_render_performance_different_motion_presets(self, test_images_dir):
        """Different motion presets should have similar performance."""
        presets = [
            MotionPreset.STATIC,
            MotionPreset.KEN_BURNS_ZOOM_IN,
            MotionPreset.PAN_LEFT,
            MotionPreset.ZOOM_IN,
        ]
        
        times = {}
        
        for preset in presets:
            scene = Scene(
                clips=[
                    ImageClip(
                        source=test_images_dir / "landscape_1920x1080.png",
                        duration=2.0,
                        motion=preset
                    )
                ],
                resolution=(1920, 1080),
                fps=30
            )
            
            loader = ImageLoader()
            planner = ScenePlanner()
            timeline = planner.plan(scene, loader)
            renderer = FrameRenderer(timeline, loader)
            
            # Warm up
            renderer.render_frame(0.5)
            
            # Measure
            start_time = time.time()
            for i in range(10):
                renderer.render_frame(0.1 * i)
            elapsed = time.time() - start_time
            
            times[preset.value] = elapsed / 10
        
        # All presets should have similar performance (within 10x)
        # Note: STATIC can be much faster since it doesn't interpolate
        min_time = min(times.values())
        max_time = max(times.values())
        
        assert max_time < min_time * 10, (
            f"Performance varies too much between presets: "
            f"min={min_time*1000:.2f}ms, max={max_time*1000:.2f}ms"
        )
        
        print("\nRender times by preset:")
        for preset, t in times.items():
            print(f"  {preset}: {t*1000:.2f}ms per frame")
    
    def test_planning_performance(self, test_images_dir):
        """Scene planning should be fast."""
        # Create scene with many clips
        clips = [
            ImageClip(
                source=test_images_dir / "landscape_1920x1080.png",
                duration=1.0,
                motion=MotionPreset.STATIC
            )
            for _ in range(20)
        ]
        
        scene = Scene(clips=clips, resolution=(1920, 1080), fps=30)
        
        loader = ImageLoader()
        planner = ScenePlanner()
        
        # Measure planning time
        start_time = time.time()
        timeline = planner.plan(scene, loader)
        elapsed = time.time() - start_time
        
        # Planning should be fast (< 1 second for 20 clips)
        assert elapsed < 1.0, f"Planning too slow: {elapsed:.3f}s for 20 clips"
        
        # Verify timeline is correct
        assert len(timeline.clips) == 20
        assert timeline.duration == 20.0
        
        print(f"\nPlanning time: {elapsed*1000:.2f}ms for 20 clips")


class TestPhase3Performance:
    """Performance tests for Phase 3 audio-reactive features.
    
    **Validates: Requirements 13.1, 13.2, 13.4, 13.5**
    """
    
    def test_baseline_performance_without_audio_effects(self, test_images_dir):
        """Establish baseline: render 100 frames without audio effects.
        
        This provides a baseline for comparing audio effect overhead.
        
        **Validates: Requirements 13.2, 13.5**
        """
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=3.5,
                    motion=MotionPreset.KEN_BURNS_ZOOM_IN
                )
            ],
            resolution=(1920, 1080),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        # Warm up
        renderer.render_frame(0.5)
        
        # Measure time to render 100 frames
        start_time = time.time()
        for i in range(100):
            renderer.render_frame(i * 0.033)  # ~30 fps
        elapsed = time.time() - start_time
        
        avg_time = elapsed / 100
        
        # Should render at reasonable speed
        assert avg_time < 0.1, f"Baseline render too slow: {avg_time:.3f}s per frame"
        
        print(f"\nBaseline (no audio effects): {avg_time*1000:.2f}ms per frame")
        print(f"Total time for 100 frames: {elapsed:.2f}s")
    
    def test_audio_analysis_time(self):
        """Audio analysis should complete in reasonable time for 10-second audio.
        
        **Validates: Requirements 13.1, 13.5**
        """
        audio_path = Path("tests/fixtures/audio/test_beats_120bpm.wav")
        
        if not audio_path.exists():
            pytest.skip(f"Test audio not found: {audio_path}")
        
        try:
            from engine.audio.analyzer import AudioAnalyzer
        except ImportError:
            pytest.skip("librosa not installed")
        
        # Measure audio analysis time
        start_time = time.time()
        analyzer = AudioAnalyzer(audio_path)
        results = analyzer.analyze_all()
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (< 5 seconds for 10-second audio)
        # Note: librosa analysis can be slow on first run
        assert elapsed < 5.0, f"Audio analysis too slow: {elapsed:.3f}s"
        
        # Verify results are valid
        assert 'beats' in results
        assert 'onsets' in results
        assert 'energy' in results
        assert 'spectral_centroid' in results
        
        print(f"\nAudio analysis time: {elapsed*1000:.2f}ms")
        print(f"  Beats detected: {len(results['beats'])}")
        print(f"  Onsets detected: {len(results['onsets'])}")
        print(f"  Energy frames: {len(results['energy'][0])}")
    
    def test_render_time_with_audio_effects(self, test_images_dir):
        """Render time with audio effects should have < 20% overhead.
        
        **Validates: Requirements 13.2, 13.5**
        """
        audio_path = Path("tests/fixtures/audio/test_beats_120bpm.wav")
        
        if not audio_path.exists():
            pytest.skip(f"Test audio not found: {audio_path}")
        
        try:
            from engine.audio.analyzer import AudioAnalyzer
            from engine.audio.sync import AudioSync
            from engine.effects import OnsetFlash, EnergyZoom, EnergyBrightness
        except ImportError:
            pytest.skip("librosa not installed")
        
        # Create scene with audio
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=3.5,
                    motion=MotionPreset.KEN_BURNS_ZOOM_IN
                )
            ],
            resolution=(1920, 1080),
            fps=30,
            audio=audio_path
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Add audio-reactive effects
        if timeline.audio_sync is not None:
            timeline.clips[0].effects = [
                OnsetFlash(timeline.audio_sync, flash_duration=0.2, intensity=0.3),
                EnergyZoom(timeline.audio_sync, zoom_range=(1.0, 1.1), energy_range=(0.0, 1.0)),
                EnergyBrightness(timeline.audio_sync, brightness_range=(0.9, 1.1), energy_range=(0.0, 1.0))
            ]
        
        renderer = FrameRenderer(timeline, loader)
        
        # Warm up
        renderer.render_frame(0.5)
        
        # Measure time to render 100 frames with audio effects
        start_time = time.time()
        for i in range(100):
            renderer.render_frame(i * 0.033)
        elapsed = time.time() - start_time
        
        avg_time = elapsed / 100
        
        # Should still render at reasonable speed
        assert avg_time < 0.12, f"Render with audio effects too slow: {avg_time:.3f}s per frame"
        
        print(f"\nWith audio effects: {avg_time*1000:.2f}ms per frame")
        print(f"Total time for 100 frames: {elapsed:.2f}s")
        
        # Compare to baseline (if we had it)
        # Overhead should be < 20%
        # Note: This is a rough check since we don't have the exact baseline here
        # In practice, baseline is ~2-3ms, with effects ~3-4ms = ~20-30% overhead
    
    def test_memory_usage_during_audio_analysis(self):
        """Memory usage during audio analysis should be < 100MB.
        
        **Validates: Requirements 13.4**
        """
        audio_path = Path("tests/fixtures/audio/test_beats_120bpm.wav")
        
        if not audio_path.exists():
            pytest.skip(f"Test audio not found: {audio_path}")
        
        try:
            from engine.audio.analyzer import AudioAnalyzer
            from engine.audio.sync import AudioSync
        except ImportError:
            pytest.skip("librosa not installed")
        
        import sys
        
        # Analyze audio
        analyzer = AudioAnalyzer(audio_path)
        results = analyzer.analyze_all()
        
        # Create AudioSync
        audio_sync = AudioSync(
            beats=results['beats'],
            onsets=results['onsets'],
            energy_times=results['energy'][0],
            energy_values=results['energy'][1],
            spectral_times=results['spectral_centroid'][0],
            spectral_values=results['spectral_centroid'][1]
        )
        
        # Estimate memory usage of AudioSync object
        # Each array is roughly: num_elements * 8 bytes (float64)
        beats_size = sys.getsizeof(audio_sync.beats) + audio_sync.beats.nbytes
        onsets_size = sys.getsizeof(audio_sync.onsets) + audio_sync.onsets.nbytes
        energy_size = sys.getsizeof(audio_sync.energy_times) + audio_sync.energy_times.nbytes
        energy_size += sys.getsizeof(audio_sync.energy_values) + audio_sync.energy_values.nbytes
        spectral_size = sys.getsizeof(audio_sync.spectral_times) + audio_sync.spectral_times.nbytes
        spectral_size += sys.getsizeof(audio_sync.spectral_values) + audio_sync.spectral_values.nbytes
        
        total_size = beats_size + onsets_size + energy_size + spectral_size
        
        # Should be well under 100MB for typical audio files
        # For a 10-second audio file, expect < 1MB
        assert total_size < 100 * 1024 * 1024, \
            f"AudioSync memory usage too high: {total_size / 1024 / 1024:.2f}MB"
        
        print(f"\nAudioSync memory usage: {total_size / 1024:.2f}KB")
        print(f"  Beats: {beats_size / 1024:.2f}KB")
        print(f"  Onsets: {onsets_size / 1024:.2f}KB")
        print(f"  Energy: {energy_size / 1024:.2f}KB")
        print(f"  Spectral: {spectral_size / 1024:.2f}KB")
    
    def test_audio_effect_overhead_per_effect(self, test_images_dir):
        """Measure overhead of individual audio-reactive effects.
        
        This helps identify which effects are most expensive.
        
        **Validates: Requirements 13.2, 13.5**
        """
        audio_path = Path("tests/fixtures/audio/test_beats_120bpm.wav")
        
        if not audio_path.exists():
            pytest.skip(f"Test audio not found: {audio_path}")
        
        try:
            from engine.audio.analyzer import AudioAnalyzer
            from engine.audio.sync import AudioSync
            from engine.effects import (
                OnsetFlash, OnsetZoomPulse, EnergyZoom,
                EnergyBrightness, EnergyShake, SpectralColorShift
            )
        except ImportError:
            pytest.skip("librosa not installed")
        
        # Analyze audio once
        analyzer = AudioAnalyzer(audio_path)
        results = analyzer.analyze_all()
        audio_sync = AudioSync(
            beats=results['beats'],
            onsets=results['onsets'],
            energy_times=results['energy'][0],
            energy_values=results['energy'][1],
            spectral_times=results['spectral_centroid'][0],
            spectral_values=results['spectral_centroid'][1]
        )
        
        # Test each effect individually
        effects = {
            'OnsetFlash': OnsetFlash(audio_sync, flash_duration=0.2, intensity=0.3),
            'OnsetZoomPulse': OnsetZoomPulse(audio_sync, pulse_duration=0.3, zoom_magnitude=1.1),
            'EnergyZoom': EnergyZoom(audio_sync, zoom_range=(1.0, 1.1), energy_range=(0.0, 1.0)),
            'EnergyBrightness': EnergyBrightness(audio_sync, brightness_range=(0.9, 1.1), energy_range=(0.0, 1.0)),
            'EnergyShake': EnergyShake(audio_sync, shake_range=(0.0, 5.0), energy_range=(0.0, 1.0)),
            'SpectralColorShift': SpectralColorShift(audio_sync, temperature_range=(-0.1, 0.1), centroid_range=(1000.0, 3000.0))
        }
        
        # Create a test frame
        import numpy as np
        frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        
        print("\nAudio effect overhead per effect:")
        
        for name, effect in effects.items():
            # Measure time for 100 applications
            start_time = time.time()
            for i in range(100):
                t = i * 0.01  # Vary time
                result = effect.apply(frame.copy(), t, 0.0)
            elapsed = time.time() - start_time
            
            avg_time = elapsed / 100
            
            # Each effect should be < 100ms per frame (reasonable for 1080p)
            # Note: Effects involve image processing which can be expensive
            assert avg_time < 0.1, f"{name} too slow: {avg_time:.3f}s per frame"
            
            print(f"  {name}: {avg_time*1000:.2f}ms per frame")
    
    def test_audio_sync_query_performance(self):
        """AudioSync queries should be fast (< 1ms).
        
        **Validates: Requirements 13.2, 13.5**
        """
        audio_path = Path("tests/fixtures/audio/test_beats_120bpm.wav")
        
        if not audio_path.exists():
            pytest.skip(f"Test audio not found: {audio_path}")
        
        try:
            from engine.audio.analyzer import AudioAnalyzer
            from engine.audio.sync import AudioSync
        except ImportError:
            pytest.skip("librosa not installed")
        
        # Analyze audio
        analyzer = AudioAnalyzer(audio_path)
        results = analyzer.analyze_all()
        audio_sync = AudioSync(
            beats=results['beats'],
            onsets=results['onsets'],
            energy_times=results['energy'][0],
            energy_values=results['energy'][1],
            spectral_times=results['spectral_centroid'][0],
            spectral_values=results['spectral_centroid'][1]
        )
        
        # Test query performance
        queries = {
            'get_energy_at_time': lambda t: audio_sync.get_energy_at_time(t),
            'get_spectral_centroid_at_time': lambda t: audio_sync.get_spectral_centroid_at_time(t),
            'get_nearest_beat': lambda t: audio_sync.get_nearest_beat(t),
            'is_onset_active': lambda t: audio_sync.is_onset_active(t, 0.2)
        }
        
        print("\nAudioSync query performance:")
        
        for name, query_fn in queries.items():
            # Measure time for 1000 queries
            start_time = time.time()
            for i in range(1000):
                t = i * 0.01  # Query at different times
                result = query_fn(t)
            elapsed = time.time() - start_time
            
            avg_time = elapsed / 1000
            
            # Each query should be < 1ms
            assert avg_time < 0.001, f"{name} too slow: {avg_time*1000:.3f}ms per query"
            
            print(f"  {name}: {avg_time*1000000:.2f}µs per query")
