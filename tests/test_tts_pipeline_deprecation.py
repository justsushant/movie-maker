"""
Tests for tts_pipeline.py deprecation warnings.

This test file verifies that the deprecated MoviePySubtitleExtractor class
properly emits deprecation warnings when used.
"""

from __future__ import annotations

import warnings
import pytest


def test_moviepy_subtitle_extractor_deprecation_warning():
    """Test that MoviePySubtitleExtractor emits a deprecation warning on instantiation."""
    from tts_pipeline import MoviePySubtitleExtractor
    
    # Verify that instantiating the class raises a DeprecationWarning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        extractor = MoviePySubtitleExtractor(
            text="Hello world.",
            lang_code='a',
            voice='af_heart',
            speed=1.0
        )
        
        # Filter for DeprecationWarnings only
        deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
        
        # Check that our deprecation warning was raised
        assert len(deprecation_warnings) >= 1
        found_our_warning = False
        for warning in deprecation_warnings:
            if "MoviePySubtitleExtractor is deprecated" in str(warning.message):
                found_our_warning = True
                assert "api.library.generate_video_from_text()" in str(warning.message)
                break
        
        assert found_our_warning, "Expected deprecation warning not found"


def test_export_moviepy_json_deprecation_warning():
    """Test that export_moviepy_json() emits a deprecation warning."""
    from tts_pipeline import MoviePySubtitleExtractor
    import tempfile
    from pathlib import Path
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Create extractor (this will emit one warning)
        extractor = MoviePySubtitleExtractor(
            text="Hello world.",
            lang_code='a',
            voice='af_heart',
            speed=1.0
        )
        
        # Clear warnings from __init__
        w.clear()
        
        # Call export_moviepy_json
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "test.json"
            extractor.export_moviepy_json(str(json_file))
        
        # Check that a warning was raised
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "export_moviepy_json() is deprecated" in str(w[0].message)


def test_get_audio_deprecation_warning():
    """Test that get_audio() emits a deprecation warning."""
    from tts_pipeline import MoviePySubtitleExtractor
    import tempfile
    from pathlib import Path
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Create extractor (this will emit one warning)
        extractor = MoviePySubtitleExtractor(
            text="Hello world.",
            lang_code='a',
            voice='af_heart',
            speed=1.0
        )
        
        # Clear warnings from __init__
        w.clear()
        
        # Call get_audio
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_file = Path(tmpdir) / "test.wav"
            extractor.get_audio(str(audio_file))
        
        # Check that a warning was raised
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "get_audio() is deprecated" in str(w[0].message)


def test_module_docstring_contains_migration_guide():
    """Test that the module docstring contains a migration guide."""
    import tts_pipeline
    
    docstring = tts_pipeline.__doc__
    assert docstring is not None
    assert "DEPRECATED MODULE" in docstring
    assert "MIGRATION GUIDE" in docstring
    assert "OLD CODE (DEPRECATED)" in docstring
    assert "NEW CODE (RECOMMENDED)" in docstring
    assert "generate_video_from_text" in docstring  # Check without parentheses


def test_class_docstring_contains_deprecation_notice():
    """Test that the class docstring contains a deprecation notice."""
    from tts_pipeline import MoviePySubtitleExtractor
    
    docstring = MoviePySubtitleExtractor.__doc__
    assert docstring is not None
    assert "DEPRECATED" in docstring
    assert "api.library.generate_video_from_text()" in docstring
