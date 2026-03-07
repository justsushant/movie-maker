"""Property-based tests for Phase 2 ScenePlanner."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st

from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.planner import ScenePlanner
from engine.image_loader import ImageLoader


@pytest.fixture
def image_loader_with_test_images(tmp_path):
    """Create image loader with test images."""
    loader = ImageLoader()
    
    # Create test images
    test_image = np.full((100, 100, 3), [128, 128, 128], dtype=np.uint8)
    
    image_paths = []
    for i in range(5):
        path = tmp_path / f"test_{i}.png"
        import cv2
        cv2.imwrite(str(path), cv2.cvtColor(test_image, cv2.COLOR_RGB2BGR))
        image_paths.append(str(path))
    
    return loader, image_paths


# Feature: video-engine-phase-2, Property 27: Timeline Overlap Computation
# Validates: Requirements 8.1, 8.2, 8.3
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    num_clips=st.integers(min_value=2, max_value=5),
    clip_duration=st.floats(min_value=1.0, max_value=5.0, allow_nan=False, allow_infinity=False),
    transition_duration=st.floats(min_value=0.1, max_value=0.9, allow_nan=False, allow_infinity=False),
)
def test_timeline_overlap_computation(
    image_loader_with_test_images,
    num_clips: int,
    clip_duration: float,
    transition_duration: float
) -> None:
    """
    Property: For any scene with transitions, the planner should create overlap
    regions where clip_n.end_time > clip_n+1.start_time, and the overlap duration
    should equal the transition duration.
    
    **Validates: Requirements 8.1, 8.2, 8.3**
    """
    loader, image_paths = image_loader_with_test_images
    
    # Ensure transition doesn't exceed clip duration
    assume(transition_duration < clip_duration)
    
    # Create scene with transitions
    clips = [
        ImageClip(source=image_paths[i % len(image_paths)], duration=clip_duration, motion=MotionPreset.STATIC)
        for i in range(num_clips)
    ]
    
    transitions = [
        Transition(type=TransitionType.CROSSFADE, duration=transition_duration)
        for _ in range(num_clips - 1)
    ]
    
    scene = Scene(clips=clips, transitions=transitions, resolution=(100, 100), fps=30)
    
    # Plan timeline
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    
    # Verify overlaps
    for i in range(len(timeline.clips) - 1):
        clip_a = timeline.clips[i]
        clip_b = timeline.clips[i + 1]
        
        # Verify overlap exists
        assert clip_a.end_time > clip_b.start_time, \
            f"No overlap between clips {i} and {i+1}"
        
        # Verify overlap duration matches transition duration
        overlap = clip_a.end_time - clip_b.start_time
        assert abs(overlap - transition_duration) < 0.001, \
            f"Overlap {overlap} doesn't match transition duration {transition_duration}"


# Feature: video-engine-phase-2, Property 28: Sequential Timing Without Transitions
# Validates: Requirements 8.4, 12.1, 12.2
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    num_clips=st.integers(min_value=2, max_value=5),
    clip_duration=st.floats(min_value=1.0, max_value=5.0, allow_nan=False, allow_infinity=False),
)
def test_sequential_timing_without_transitions(
    image_loader_with_test_images,
    num_clips: int,
    clip_duration: float
) -> None:
    """
    Property: For any scene with no transitions or empty transitions list, the
    planner should create clips with sequential timing where
    clip_n.end_time = clip_n+1.start_time.
    
    **Validates: Requirements 8.4, 12.1, 12.2**
    """
    loader, image_paths = image_loader_with_test_images
    
    # Create scene without transitions
    clips = [
        ImageClip(source=image_paths[i % len(image_paths)], duration=clip_duration, motion=MotionPreset.STATIC)
        for i in range(num_clips)
    ]
    
    scene = Scene(clips=clips, resolution=(100, 100), fps=30)
    
    # Plan timeline
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    
    # Verify sequential timing (no overlaps)
    for i in range(len(timeline.clips) - 1):
        clip_a = timeline.clips[i]
        clip_b = timeline.clips[i + 1]
        
        # Verify no overlap
        assert abs(clip_a.end_time - clip_b.start_time) < 0.001, \
            f"Unexpected overlap between clips {i} and {i+1}: {clip_a.end_time} vs {clip_b.start_time}"
    
    # Verify total duration is sum of clip durations
    expected_duration = num_clips * clip_duration
    assert abs(timeline.duration - expected_duration) < 0.001, \
        f"Total duration {timeline.duration} doesn't match expected {expected_duration}"


# Feature: video-engine-phase-2, Property 29: Transition Region Creation
# Validates: Requirements 8.5
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    num_clips=st.integers(min_value=2, max_value=5),
    clip_duration=st.floats(min_value=1.0, max_value=5.0, allow_nan=False, allow_infinity=False),
    transition_duration=st.floats(min_value=0.1, max_value=0.9, allow_nan=False, allow_infinity=False),
)
def test_transition_region_creation(
    image_loader_with_test_images,
    num_clips: int,
    clip_duration: float,
    transition_duration: float
) -> None:
    """
    Property: For any scene with T transitions, the resolved timeline should
    contain exactly T transition regions, each with correct clip indices and timing.
    
    **Validates: Requirements 8.5**
    """
    loader, image_paths = image_loader_with_test_images
    
    # Ensure transition doesn't exceed clip duration
    assume(transition_duration < clip_duration)
    
    # Create scene with transitions
    clips = [
        ImageClip(source=image_paths[i % len(image_paths)], duration=clip_duration, motion=MotionPreset.STATIC)
        for i in range(num_clips)
    ]
    
    num_transitions = num_clips - 1
    transitions = [
        Transition(type=TransitionType.CROSSFADE, duration=transition_duration)
        for _ in range(num_transitions)
    ]
    
    scene = Scene(clips=clips, transitions=transitions, resolution=(100, 100), fps=30)
    
    # Plan timeline
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    
    # Verify correct number of transition regions
    assert len(timeline.transitions) == num_transitions, \
        f"Expected {num_transitions} transition regions, got {len(timeline.transitions)}"
    
    # Verify each transition region
    for i, transition_region in enumerate(timeline.transitions):
        # Verify clip indices
        assert transition_region.clip_a_index == i, \
            f"Transition {i} has wrong clip_a_index: {transition_region.clip_a_index}"
        assert transition_region.clip_b_index == i + 1, \
            f"Transition {i} has wrong clip_b_index: {transition_region.clip_b_index}"
        
        # Verify timing
        expected_start = timeline.clips[i + 1].start_time
        expected_end = expected_start + transition_duration
        
        assert abs(transition_region.start_time - expected_start) < 0.001, \
            f"Transition {i} start time mismatch"
        assert abs(transition_region.end_time - expected_end) < 0.001, \
            f"Transition {i} end time mismatch"


# Feature: video-engine-phase-2, Property 1: Transition Duration Validation
# Validates: Requirements 1.3, 8.6, 13.1, 13.2
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    clip_duration=st.floats(min_value=0.5, max_value=2.0, allow_nan=False, allow_infinity=False),
)
def test_transition_duration_validation(
    image_loader_with_test_images,
    clip_duration: float
) -> None:
    """
    Property: For any transition with duration D, D must be positive, and when
    used between two clips with durations d1 and d2, D must not exceed min(d1, d2).
    
    **Validates: Requirements 1.3, 8.6, 13.1, 13.2**
    """
    loader, image_paths = image_loader_with_test_images
    
    # Test 1: Negative duration should raise ValueError
    with pytest.raises(ValueError, match="duration must be positive"):
        Transition(type=TransitionType.CROSSFADE, duration=-0.5)
    
    # Test 2: Zero duration should raise ValueError
    with pytest.raises(ValueError, match="duration must be positive"):
        Transition(type=TransitionType.CROSSFADE, duration=0.0)
    
    # Test 3: Transition exceeding clip duration should raise ValueError
    clips = [
        ImageClip(source=image_paths[0], duration=clip_duration, motion=MotionPreset.STATIC),
        ImageClip(source=image_paths[1], duration=clip_duration, motion=MotionPreset.STATIC),
    ]
    
    # Transition longer than clip duration
    transitions = [
        Transition(type=TransitionType.CROSSFADE, duration=clip_duration + 0.5)
    ]
    
    scene = Scene(clips=clips, transitions=transitions, resolution=(100, 100), fps=30)
    
    planner = ScenePlanner()
    with pytest.raises(ValueError, match="exceeds"):
        planner.plan(scene, loader)


# Feature: video-engine-phase-2, Property 2: Scene Transition Count Validation
# Validates: Requirements 1.6, 13.3
def test_scene_transition_count_validation(image_loader_with_test_images) -> None:
    """
    Property: For any scene with N clips and T transitions, T must be at most N-1,
    otherwise a ValueError should be raised.
    
    **Validates: Requirements 1.6, 13.3**
    """
    loader, image_paths = image_loader_with_test_images
    
    # Create scene with too many transitions
    clips = [
        ImageClip(source=image_paths[0], duration=2.0, motion=MotionPreset.STATIC),
        ImageClip(source=image_paths[1], duration=2.0, motion=MotionPreset.STATIC),
    ]
    
    # 3 transitions for 2 clips (should fail)
    transitions = [
        Transition(type=TransitionType.CROSSFADE, duration=0.5),
        Transition(type=TransitionType.CROSSFADE, duration=0.5),
        Transition(type=TransitionType.CROSSFADE, duration=0.5),
    ]
    
    with pytest.raises(ValueError, match="Maximum transitions"):
        Scene(clips=clips, transitions=transitions, resolution=(100, 100), fps=30)
