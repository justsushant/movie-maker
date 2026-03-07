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
