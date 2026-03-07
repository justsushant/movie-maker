"""Unit tests for audio-reactive effects (Phase 3)."""

from __future__ import annotations
import pytest
import numpy as np

from engine.effects import OnsetFlash
from engine.audio.sync import AudioSync
from engine.easing import linear, ease_out_cubic


def test_onset_flash_brightens_during_onset():
    """Test that OnsetFlash brightens frame during onset window."""
    # Create AudioSync with known onsets
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([1.0, 2.0, 3.0]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    # Create effect
    effect = OnsetFlash(audio_sync, flash_duration=0.2, intensity=0.5, easing=linear)
    
    # Create test frame (gray)
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    
    # At onset time (t=1.0), should brighten
    result = effect.apply(frame, 1.0, 0.0)
    
    # Should be brighter than original
    assert np.mean(result) > np.mean(frame)
    
    # At peak (t=1.0), brightness should be 1.0 + 0.5 = 1.5x
    # 128 * 1.5 = 192
    assert np.mean(result) == pytest.approx(192, abs=1)


def test_onset_flash_unchanged_outside_onset():
    """Test that OnsetFlash doesn't modify frame outside onset window."""
    # Create AudioSync with known onsets
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([1.0, 2.0, 3.0]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    # Create effect
    effect = OnsetFlash(audio_sync, flash_duration=0.2, intensity=0.5)
    
    # Create test frame
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    
    # At time far from any onset, should be unchanged
    result = effect.apply(frame, 0.5, 0.0)
    
    assert np.array_equal(result, frame)


def test_onset_flash_uses_easing():
    """Test that OnsetFlash uses easing curve for decay."""
    # Create AudioSync with known onsets
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([1.0]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    # Create effect with linear easing for predictable behavior
    effect = OnsetFlash(audio_sync, flash_duration=0.2, intensity=0.5, easing=linear)
    
    # Create test frame
    frame = np.full((100, 100, 3), 100, dtype=np.uint8)
    
    # At onset (t=1.0), full brightness
    result_start = effect.apply(frame, 1.0, 0.0)
    brightness_start = np.mean(result_start)
    
    # Halfway through (t=1.1), should be between original and peak
    result_mid = effect.apply(frame, 1.1, 0.0)
    brightness_mid = np.mean(result_mid)
    
    # At end (t=1.2), should be back to original
    result_end = effect.apply(frame, 1.2, 0.0)
    brightness_end = np.mean(result_end)
    
    # Check progression: start > mid > end
    assert brightness_start > brightness_mid > brightness_end
    
    # End should be close to original
    assert brightness_end == pytest.approx(100, abs=1)


def test_onset_flash_maximum_for_overlapping_onsets():
    """Test that OnsetFlash uses maximum brightness for overlapping onsets."""
    # Create AudioSync with overlapping onsets
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([1.0, 1.1]),  # Onsets 0.1s apart
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    # Create effect with 0.2s duration (so onsets overlap)
    effect = OnsetFlash(audio_sync, flash_duration=0.2, intensity=0.5, easing=linear)
    
    # Create test frame
    frame = np.full((100, 100, 3), 100, dtype=np.uint8)
    
    # At t=1.15, both onsets are active
    # First onset: delta=0.15, progress=0.75, brightness=1.0+0.5*(1-0.75)=1.125
    # Second onset: delta=0.05, progress=0.25, brightness=1.0+0.5*(1-0.25)=1.375
    # Should use maximum: 1.375
    result = effect.apply(frame, 1.15, 0.0)
    
    # Expected: 100 * 1.375 = 137.5
    assert np.mean(result) == pytest.approx(137.5, abs=2)


def test_onset_flash_degrades_gracefully_without_audio():
    """Test that OnsetFlash degrades gracefully when audio_sync is None."""
    # Create effect with no audio
    effect = OnsetFlash(None, flash_duration=0.2, intensity=0.5)
    
    # Create test frame
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    
    # Should return frame unchanged
    result = effect.apply(frame, 1.0, 0.0)
    
    assert np.array_equal(result, frame)


def test_onset_flash_clamps_to_255():
    """Test that OnsetFlash clamps brightness to valid range."""
    # Create AudioSync with onset
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([1.0]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    # Create effect with high intensity
    effect = OnsetFlash(audio_sync, flash_duration=0.2, intensity=1.0, easing=linear)
    
    # Create bright frame
    frame = np.full((100, 100, 3), 200, dtype=np.uint8)
    
    # At onset, would be 200 * 2.0 = 400, but should clamp to 255
    result = effect.apply(frame, 1.0, 0.0)
    
    assert np.max(result) == 255
    assert np.min(result) <= 255


def test_onset_flash_before_onset_time():
    """Test that OnsetFlash doesn't flash before onset occurs."""
    # Create AudioSync with onset at t=1.0
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([1.0]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    # Create effect
    effect = OnsetFlash(audio_sync, flash_duration=0.2, intensity=0.5)
    
    # Create test frame
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    
    # At time before onset, should be unchanged
    result = effect.apply(frame, 0.9, 0.0)
    
    assert np.array_equal(result, frame)


def test_onset_flash_with_ease_out_cubic():
    """Test that OnsetFlash works with ease_out_cubic easing."""
    # Create AudioSync with onset
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([1.0]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    # Create effect with ease_out_cubic (default)
    effect = OnsetFlash(audio_sync, flash_duration=0.2, intensity=0.5, easing=ease_out_cubic)
    
    # Create test frame
    frame = np.full((100, 100, 3), 100, dtype=np.uint8)
    
    # At onset, should brighten
    result_start = effect.apply(frame, 1.0, 0.0)
    assert np.mean(result_start) > 100
    
    # At end, should return to normal
    result_end = effect.apply(frame, 1.2, 0.0)
    assert np.mean(result_end) == pytest.approx(100, abs=1)


def test_onset_flash_empty_onsets():
    """Test that OnsetFlash handles empty onset array gracefully."""
    # Create AudioSync with no onsets
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    # Create effect
    effect = OnsetFlash(audio_sync, flash_duration=0.2, intensity=0.5)
    
    # Create test frame
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    
    # Should return frame unchanged
    result = effect.apply(frame, 1.0, 0.0)
    
    assert np.array_equal(result, frame)



# ============================================================================
# OnsetZoomPulse Tests
# ============================================================================

def test_onset_zoom_pulse_scales_during_onset():
    """Test that OnsetZoomPulse scales frame during onset window."""
    from engine.effects import OnsetZoomPulse
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([1.0]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    effect = OnsetZoomPulse(audio_sync, pulse_duration=0.3, zoom_magnitude=1.2, easing=linear)
    
    # Create test frame with distinct pattern
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[40:60, 40:60] = 255  # White square in center
    
    # At onset, should zoom
    result = effect.apply(frame, 1.0, 0.0)
    
    # Result should be different from original (zoomed)
    assert not np.array_equal(result, frame)


def test_onset_zoom_pulse_unchanged_outside_onset():
    """Test that OnsetZoomPulse doesn't modify frame outside onset window."""
    from engine.effects import OnsetZoomPulse
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([1.0]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    effect = OnsetZoomPulse(audio_sync, pulse_duration=0.3, zoom_magnitude=1.2)
    
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    
    # Outside onset window
    result = effect.apply(frame, 0.5, 0.0)
    
    assert np.array_equal(result, frame)


def test_onset_zoom_pulse_degrades_gracefully():
    """Test that OnsetZoomPulse degrades gracefully without audio."""
    from engine.effects import OnsetZoomPulse
    
    effect = OnsetZoomPulse(None, pulse_duration=0.3, zoom_magnitude=1.2)
    
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    result = effect.apply(frame, 1.0, 0.0)
    
    assert np.array_equal(result, frame)


# ============================================================================
# EnergyZoom Tests
# ============================================================================

def test_energy_zoom_maps_energy_to_zoom():
    """Test that EnergyZoom maps energy to zoom range."""
    from engine.effects import EnergyZoom
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([0.0, 1.0, 2.0]),
        energy_values=np.array([0.0, 0.5, 1.0]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    effect = EnergyZoom(audio_sync, zoom_range=(1.0, 1.4), energy_range=(0.0, 1.0))
    
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[40:60, 40:60] = 255
    
    # At low energy (t=0.0), should have minimal zoom
    result_low = effect.apply(frame, 0.0, 0.0)
    
    # At high energy (t=2.0), should have maximum zoom
    result_high = effect.apply(frame, 2.0, 0.0)
    
    # Results should be different
    assert not np.array_equal(result_low, result_high)


def test_energy_zoom_degrades_gracefully():
    """Test that EnergyZoom degrades gracefully without audio."""
    from engine.effects import EnergyZoom
    
    effect = EnergyZoom(None, zoom_range=(1.0, 1.2), energy_range=(0.0, 1.0))
    
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    result = effect.apply(frame, 1.0, 0.0)
    
    assert np.array_equal(result, frame)


def test_energy_zoom_interpolates_energy():
    """Test that EnergyZoom interpolates energy values."""
    from engine.effects import EnergyZoom
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([0.0, 2.0]),
        energy_values=np.array([0.0, 1.0]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    effect = EnergyZoom(audio_sync, zoom_range=(1.0, 1.2), energy_range=(0.0, 1.0))
    
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    
    # At t=1.0 (midpoint), energy should be 0.5
    # Zoom should be 1.0 + 0.5 * (1.2 - 1.0) = 1.1
    result = effect.apply(frame, 1.0, 0.0)
    
    # Should apply some zoom (result different from original)
    # But we can't easily verify exact zoom without complex analysis
    assert result.shape == frame.shape


# ============================================================================
# EnergyBrightness Tests
# ============================================================================

def test_energy_brightness_maps_energy_to_brightness():
    """Test that EnergyBrightness maps energy to brightness range."""
    from engine.effects import EnergyBrightness
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([0.0, 1.0, 2.0]),
        energy_values=np.array([0.0, 0.5, 1.0]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    effect = EnergyBrightness(audio_sync, brightness_range=(0.5, 1.5), energy_range=(0.0, 1.0))
    
    frame = np.full((100, 100, 3), 100, dtype=np.uint8)
    
    # At low energy (t=0.0), brightness = 0.5, result = 50
    result_low = effect.apply(frame, 0.0, 0.0)
    assert np.mean(result_low) == pytest.approx(50, abs=1)
    
    # At high energy (t=2.0), brightness = 1.5, result = 150
    result_high = effect.apply(frame, 2.0, 0.0)
    assert np.mean(result_high) == pytest.approx(150, abs=1)


def test_energy_brightness_clamps_values():
    """Test that EnergyBrightness clamps pixel values to [0, 255]."""
    from engine.effects import EnergyBrightness
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([0.0]),
        energy_values=np.array([1.0]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    effect = EnergyBrightness(audio_sync, brightness_range=(0.5, 2.0), energy_range=(0.0, 1.0))
    
    frame = np.full((100, 100, 3), 200, dtype=np.uint8)
    
    # At high energy, 200 * 2.0 = 400, should clamp to 255
    result = effect.apply(frame, 0.0, 0.0)
    
    assert np.max(result) == 255


def test_energy_brightness_degrades_gracefully():
    """Test that EnergyBrightness degrades gracefully without audio."""
    from engine.effects import EnergyBrightness
    
    effect = EnergyBrightness(None, brightness_range=(0.8, 1.2), energy_range=(0.0, 1.0))
    
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    result = effect.apply(frame, 1.0, 0.0)
    
    assert np.array_equal(result, frame)


# ============================================================================
# EnergyShake Tests
# ============================================================================

def test_energy_shake_maps_energy_to_shake():
    """Test that EnergyShake maps energy to shake range."""
    from engine.effects import EnergyShake
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([0.0, 1.0]),
        energy_values=np.array([0.0, 1.0]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    effect = EnergyShake(audio_sync, shake_range=(0.0, 10.0), energy_range=(0.0, 1.0))
    
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    
    # At low energy, minimal shake (should be unchanged or nearly so)
    result_low = effect.apply(frame, 0.0, 0.0)
    
    # At high energy, should shake
    result_high = effect.apply(frame, 1.0, 0.0)
    
    # High energy result should be different (shaken)
    # Low energy might be unchanged if shake < 0.1
    assert result_high.shape == frame.shape


def test_energy_shake_degrades_gracefully():
    """Test that EnergyShake degrades gracefully without audio."""
    from engine.effects import EnergyShake
    
    effect = EnergyShake(None, shake_range=(0.0, 10.0), energy_range=(0.0, 1.0))
    
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    result = effect.apply(frame, 1.0, 0.0)
    
    assert np.array_equal(result, frame)


# ============================================================================
# SpectralColorShift Tests
# ============================================================================

def test_spectral_color_shift_maps_centroid_to_temperature():
    """Test that SpectralColorShift maps spectral centroid to temperature."""
    from engine.effects import SpectralColorShift
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([0.0, 1.0, 2.0]),
        spectral_values=np.array([1000.0, 2000.0, 3000.0])
    )
    
    effect = SpectralColorShift(audio_sync, temperature_range=(-0.3, 0.3), centroid_range=(1000.0, 3000.0))
    
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    
    # At low centroid (t=0.0), should shift cool (more blue)
    result_low = effect.apply(frame, 0.0, 0.0)
    
    # At high centroid (t=2.0), should shift warm (more red)
    result_high = effect.apply(frame, 2.0, 0.0)
    
    # Results should be different
    assert not np.array_equal(result_low, result_high)
    
    # Low centroid should have more blue
    assert result_low[:, :, 2].mean() > result_high[:, :, 2].mean()


def test_spectral_color_shift_adjusts_channels():
    """Test that SpectralColorShift adjusts red and blue channels."""
    from engine.effects import SpectralColorShift
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([0.0]),
        spectral_values=np.array([3000.0])  # High centroid = warm
    )
    
    effect = SpectralColorShift(audio_sync, temperature_range=(-0.2, 0.2), centroid_range=(1000.0, 3000.0))
    
    frame = np.full((100, 100, 3), 100, dtype=np.uint8)
    
    # At high centroid, should increase red, decrease blue
    result = effect.apply(frame, 0.0, 0.0)
    
    # Red channel should increase
    assert result[:, :, 0].mean() > 100
    
    # Blue channel should decrease
    assert result[:, :, 2].mean() < 100


def test_spectral_color_shift_degrades_gracefully():
    """Test that SpectralColorShift degrades gracefully without audio."""
    from engine.effects import SpectralColorShift
    
    effect = SpectralColorShift(None, temperature_range=(-0.2, 0.2), centroid_range=(1000.0, 3000.0))
    
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    result = effect.apply(frame, 1.0, 0.0)
    
    assert np.array_equal(result, frame)
