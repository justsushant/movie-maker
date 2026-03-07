"""Tests for ImageLoader with caching."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from PIL import Image

from engine.image_loader import ImageLoader


# ============================================================================
# Property-Based Tests
# ============================================================================


# Feature: video-engine-phase-1, Property 11: Image Loader Caching
@given(
    width=st.integers(min_value=10, max_value=1000),
    height=st.integers(min_value=10, max_value=1000),
)
@settings(max_examples=100)
def test_property_image_loader_caching(width: int, height: int):
    """
    Property 11: Image Loader Caching
    
    For any image path, loading the same image twice should result in only
    one disk read (the second load should return the cached value).
    
    Validates: Requirements 9.5
    """
    # Create a test image in a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        image_path = Path(tmp_dir) / "test_image.png"
        img = Image.new('RGB', (width, height), color='red')
        img.save(image_path)
        
        loader = ImageLoader()
        
        # Mock PIL.Image.open to track calls
        with patch('engine.image_loader.Image.open', wraps=Image.open) as mock_open:
            # First load - should read from disk
            result1 = loader.load(image_path)
            assert mock_open.call_count == 1
            
            # Second load - should use cache (no additional disk read)
            result2 = loader.load(image_path)
            assert mock_open.call_count == 1  # Still 1, not 2
            
            # Results should be identical (same cached array)
            assert np.array_equal(result1, result2)
            assert result1 is result2  # Same object reference


# Feature: video-engine-phase-1, Property 12: Image Loader RGB Conversion
@given(
    width=st.integers(min_value=10, max_value=1000),
    height=st.integers(min_value=10, max_value=1000),
    mode=st.sampled_from(['RGB', 'RGBA', 'L', 'P']),
)
@settings(max_examples=100)
def test_property_rgb_conversion(width: int, height: int, mode: str):
    """
    Property 12: Image Loader RGB Conversion
    
    For any valid image file, loading it should produce a numpy array with
    shape (height, width, 3) where the third dimension represents RGB channels.
    
    Validates: Requirements 9.4
    """
    # Create test image in various modes using temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        image_path = Path(tmp_dir) / f"test_{mode}.png"
        
        if mode == 'RGB':
            img = Image.new('RGB', (width, height), color='blue')
        elif mode == 'RGBA':
            img = Image.new('RGBA', (width, height), color=(0, 255, 0, 128))
        elif mode == 'L':
            img = Image.new('L', (width, height), color=128)
        elif mode == 'P':
            img = Image.new('P', (width, height))
            img.putpalette([i % 256 for i in range(768)])
        
        img.save(image_path)
        
        loader = ImageLoader()
        result = loader.load(image_path)
        
        # Should always be HxWx3 numpy array (RGB)
        assert isinstance(result, np.ndarray)
        assert result.shape == (height, width, 3)
        assert result.dtype == np.uint8


# ============================================================================
# Unit Tests
# ============================================================================


class TestImageLoaderBasics:
    """Test basic ImageLoader functionality."""
    
    def test_load_png_image(self, tmp_path: Path):
        """Test loading a PNG image successfully."""
        # Create a test PNG
        image_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image_path)
        
        loader = ImageLoader()
        result = loader.load(image_path)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (100, 100, 3)
        assert result.dtype == np.uint8
        # Check it's red (approximately, due to compression)
        assert result[0, 0, 0] > 200  # Red channel
    
    def test_load_jpeg_image(self, tmp_path: Path):
        """Test loading a JPEG image successfully."""
        # Create a test JPEG
        image_path = tmp_path / "test.jpg"
        img = Image.new('RGB', (100, 100), color='green')
        img.save(image_path, 'JPEG')
        
        loader = ImageLoader()
        result = loader.load(image_path)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (100, 100, 3)
        assert result.dtype == np.uint8
        # Check it's green (approximately, due to JPEG compression)
        # JPEG compression can significantly alter colors, so use looser check
        assert result[0, 0, 1] > 100  # Green channel should be dominant
    
    def test_load_webp_image(self, tmp_path: Path):
        """Test loading a WebP image successfully."""
        # Create a test WebP
        image_path = tmp_path / "test.webp"
        img = Image.new('RGB', (100, 100), color='blue')
        try:
            img.save(image_path, 'WEBP')
            
            loader = ImageLoader()
            result = loader.load(image_path)
            
            assert isinstance(result, np.ndarray)
            assert result.shape == (100, 100, 3)
            assert result.dtype == np.uint8
        except (OSError, ValueError):
            # WebP support might not be available
            pytest.skip("WebP support not available")


class TestImageLoaderConversions:
    """Test image format conversions."""
    
    def test_load_rgba_converts_to_rgb(self, tmp_path: Path):
        """Test loading image with alpha channel converts to RGB."""
        # Create RGBA image
        image_path = tmp_path / "test_rgba.png"
        img = Image.new('RGBA', (50, 50), color=(255, 0, 0, 128))
        img.save(image_path)
        
        loader = ImageLoader()
        result = loader.load(image_path)
        
        # Should be RGB (no alpha channel)
        assert result.shape == (50, 50, 3)
        assert result.dtype == np.uint8
    
    def test_load_grayscale_converts_to_rgb(self, tmp_path: Path):
        """Test loading grayscale image converts to RGB."""
        # Create grayscale image
        image_path = tmp_path / "test_gray.png"
        img = Image.new('L', (50, 50), color=128)
        img.save(image_path)
        
        loader = ImageLoader()
        result = loader.load(image_path)
        
        # Should be RGB (3 channels)
        assert result.shape == (50, 50, 3)
        assert result.dtype == np.uint8
        # All channels should be equal (grayscale)
        assert np.allclose(result[:, :, 0], result[:, :, 1])
        assert np.allclose(result[:, :, 1], result[:, :, 2])


class TestImageLoaderCaching:
    """Test image caching behavior."""
    
    def test_caching_behavior_with_mock(self, tmp_path: Path):
        """Test caching behavior by mocking file I/O."""
        # Create test image
        image_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image_path)
        
        loader = ImageLoader()
        
        # Mock Image.open to track calls
        with patch('engine.image_loader.Image.open', wraps=Image.open) as mock_open:
            # First load
            result1 = loader.load(image_path)
            assert mock_open.call_count == 1
            
            # Second load - should use cache
            result2 = loader.load(image_path)
            assert mock_open.call_count == 1  # No additional call
            
            # Third load - still cached
            result3 = loader.load(image_path)
            assert mock_open.call_count == 1
            
            # All results should be the same cached array
            assert result1 is result2
            assert result2 is result3
    
    def test_cache_with_string_and_path(self, tmp_path: Path):
        """Test that string and Path to same file use same cache entry."""
        # Create test image
        image_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(image_path)
        
        loader = ImageLoader()
        
        # Load with Path
        result1 = loader.load(image_path)
        
        # Load with string - should use same cache
        result2 = loader.load(str(image_path))
        
        # Should be same cached object
        assert result1 is result2
    
    def test_clear_cache(self, tmp_path: Path):
        """Test clear_cache removes cached images."""
        # Create test images
        image1_path = tmp_path / "test1.png"
        image2_path = tmp_path / "test2.png"
        Image.new('RGB', (100, 100), color='red').save(image1_path)
        Image.new('RGB', (100, 100), color='blue').save(image2_path)
        
        loader = ImageLoader()
        
        # Load images
        loader.load(image1_path)
        loader.load(image2_path)
        
        # Cache should have 2 entries
        assert len(loader._cache) == 2
        
        # Clear cache
        loader.clear_cache()
        
        # Cache should be empty
        assert len(loader._cache) == 0
        
        # Loading again should work (reload from disk)
        result = loader.load(image1_path)
        assert isinstance(result, np.ndarray)
        assert len(loader._cache) == 1


class TestImageLoaderErrors:
    """Test error handling."""
    
    def test_file_not_found_error(self, tmp_path: Path):
        """Test FileNotFoundError for missing file."""
        loader = ImageLoader()
        non_existent = tmp_path / "does_not_exist.png"
        
        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load(non_existent)
        
        assert "Image file not found" in str(exc_info.value)
        assert str(non_existent) in str(exc_info.value)
    
    def test_corrupted_file_exception(self, tmp_path: Path):
        """Test exception for corrupted file."""
        # Create a corrupted image file (just write garbage)
        corrupted_path = tmp_path / "corrupted.png"
        corrupted_path.write_bytes(b"This is not a valid image file")
        
        loader = ImageLoader()
        
        with pytest.raises(Exception) as exc_info:
            loader.load(corrupted_path)
        
        assert "Failed to load image" in str(exc_info.value)
        assert str(corrupted_path) in str(exc_info.value)
    
    def test_empty_file_exception(self, tmp_path: Path):
        """Test exception for empty file."""
        # Create an empty file
        empty_path = tmp_path / "empty.png"
        empty_path.write_bytes(b"")
        
        loader = ImageLoader()
        
        with pytest.raises(Exception) as exc_info:
            loader.load(empty_path)
        
        assert "Failed to load image" in str(exc_info.value)


class TestImageLoaderOutputFormat:
    """Test output format specifications."""
    
    def test_output_is_numpy_array(self, tmp_path: Path):
        """Test output is numpy array with correct shape and dtype."""
        image_path = tmp_path / "test.png"
        Image.new('RGB', (200, 150), color='red').save(image_path)
        
        loader = ImageLoader()
        result = loader.load(image_path)
        
        # Check type
        assert isinstance(result, np.ndarray)
        
        # Check shape (H, W, 3)
        assert result.shape == (150, 200, 3)
        
        # Check dtype
        assert result.dtype == np.uint8
    
    def test_various_image_sizes(self, tmp_path: Path):
        """Test loading images of various sizes."""
        sizes = [(100, 100), (1920, 1080), (50, 200), (300, 100)]
        
        loader = ImageLoader()
        
        for width, height in sizes:
            image_path = tmp_path / f"test_{width}x{height}.png"
            Image.new('RGB', (width, height), color='green').save(image_path)
            
            result = loader.load(image_path)
            
            assert result.shape == (height, width, 3)
            assert result.dtype == np.uint8


class TestImageLoaderEdgeCases:
    """Test edge cases and unusual scenarios."""
    
    def test_very_small_image(self, tmp_path: Path):
        """Test loading a very small image (1x1 pixel)."""
        image_path = tmp_path / "tiny.png"
        Image.new('RGB', (1, 1), color='red').save(image_path)
        
        loader = ImageLoader()
        result = loader.load(image_path)
        
        assert result.shape == (1, 1, 3)
        assert result.dtype == np.uint8
    
    def test_large_image(self, tmp_path: Path):
        """Test loading a large image."""
        # Create a 4K image
        image_path = tmp_path / "large.png"
        Image.new('RGB', (3840, 2160), color='blue').save(image_path)
        
        loader = ImageLoader()
        result = loader.load(image_path)
        
        assert result.shape == (2160, 3840, 3)
        assert result.dtype == np.uint8
    
    def test_unusual_aspect_ratio(self, tmp_path: Path):
        """Test loading image with unusual aspect ratio."""
        # Very wide image
        image_path = tmp_path / "wide.png"
        Image.new('RGB', (1000, 100), color='yellow').save(image_path)
        
        loader = ImageLoader()
        result = loader.load(image_path)
        
        assert result.shape == (100, 1000, 3)
        assert result.dtype == np.uint8
    
    def test_multiple_loaders_independent_caches(self, tmp_path: Path):
        """Test that multiple ImageLoader instances have independent caches."""
        image_path = tmp_path / "test.png"
        Image.new('RGB', (100, 100), color='red').save(image_path)
        
        loader1 = ImageLoader()
        loader2 = ImageLoader()
        
        # Load with first loader
        result1 = loader1.load(image_path)
        
        # Second loader should have empty cache
        assert len(loader2._cache) == 0
        
        # Load with second loader
        result2 = loader2.load(image_path)
        
        # Both should have loaded the image
        assert np.array_equal(result1, result2)
        
        # But they should be different objects (different caches)
        assert result1 is not result2
        
        # Each loader should have 1 cache entry
        assert len(loader1._cache) == 1
        assert len(loader2._cache) == 1
