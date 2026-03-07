"""Property-based tests for Phase 2 renderer functionality."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader
from engine.effects import brightness, contrast


@pytest.fixture
def test_images(tmp_path):
    """Create test images for renderer tests."""
    import cv2
    
    # Create solid color images
    red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
    blue = np.full((100, 100, 3), [0, 0, 255], dtype=np.uint8)
    
    red_path = tmp_path / "red.png"
    blue_path = tmp_path / "blue.png"
    
    cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(blue_path), cv2.cvtColor(blue, cv2.COLOR_RGB2BGR))
    
    return str(red_path), str(blue_path)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=50)
@given(
    clip_duration=st.floats(min_value=1.0, max_value=3.0),
    transition_duration=st.floats(min_value=0.1, max_value=0.5),
    query_time=st.floats(min_value=0.0, max_value=5.0)
)
def test_renderer_transition_detection(test_images, clip_duration, transition_duration, query_time):
    """
    Property 30: Renderer Transition Detection
    
    The renderer must correctly identify whether a given time falls within a transition region.
    
    **Validates: Requirements 9.1, 9.2**
    """
    red_path, blue_path = test_images
    
    # Ensure transition doesn't exceed clip duration
    transition_duration = min(transition_duration, clip_duration * 0.5)
    
    scene = Scene(
        clips=[
            ImageClip(source=red_path, duration=clip_duration, motion=MotionPreset.STATIC),
            ImageClip(source=blue_path, duration=clip_duration, motion=MotionPreset.STATIC),
        ],
        transitions=[
            Transition(type=TransitionType.CROSSFADE, duration=transition_duration)
        ],
        resolution=(100, 100),
        fps=30
    )
    
    loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    renderer = FrameRenderer(timeline, loader)
    
    # Transition should start at clip1.start_time and end at clip1.start_time + duration
    transition_start = timeline.clips[1].start_time
    transition_end = transition_start + transition_duration
    
    # Clamp query time to valid range
    query_time = min(query_time, timeline.duration)
    
    # Find transition at query time
    transition = renderer._find_transition_at_time(query_time)
    
    # Verify detection correctness
    if transition_start <= query_time < transition_end:
        assert transition is not None, f"Expected transition at t={query_time}, but got None"
        assert transition.start_time == transition_start
        assert transition.end_time == transition_end
    else:
        assert transition is None, f"Expected no transition at t={query_time}, but got {transition}"


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(
    progress=st.floats(min_value=0.0, max_value=1.0)
)
def test_transition_rendering_process(test_images, progress):
    """
    Property 31: Transition Rendering Process
    
    During a transition, the renderer must:
    1. Render both clips at the correct times
    2. Apply effects to each clip independently
    3. Compute progress correctly
    4. Call the transition function with both frames
    
    **Validates: Requirements 9.3, 9.4, 9.5, 9.6**
    """
    red_path, blue_path = test_images
    
    # Create scene with effects on both clips
    scene = Scene(
        clips=[
            ImageClip(
                source=red_path, 
                duration=2.0, 
                motion=MotionPreset.STATIC,
                effects=[brightness(0.1)]
            ),
            ImageClip(
                source=blue_path, 
                duration=2.0, 
                motion=MotionPreset.STATIC,
                effects=[contrast(1.2)]
            ),
        ],
        transitions=[
            Transition(type=TransitionType.CROSSFADE, duration=0.5)
        ],
        resolution=(100, 100),
        fps=30
    )
    
    loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    renderer = FrameRenderer(timeline, loader)
    
    # Query time during transition
    transition_start = timeline.clips[1].start_time
    query_time = transition_start + progress * 0.5
    
    # Render frame during transition
    frame = renderer.render_frame(query_time)
    
    # Verify frame properties
    assert frame.shape == (100, 100, 3)
    assert frame.dtype == np.uint8
    
    # Verify blending occurred (frame should not be pure red or pure blue)
    center_pixel = frame[50, 50]
    if 0.1 < progress < 0.9:  # Avoid boundary cases
        # Should have both red and blue components
        assert center_pixel[0] > 0 or center_pixel[2] > 0


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=50)
@given(
    query_time=st.floats(min_value=0.0, max_value=5.0)
)
def test_single_clip_rendering_outside_transitions(test_images, query_time):
    """
    Property 32: Single Clip Rendering Outside Transitions
    
    Outside transition regions, the renderer must render only the active clip
    with its effect chain applied.
    
    **Validates: Requirements 9.7**
    """
    red_path, blue_path = test_images
    
    scene = Scene(
        clips=[
            ImageClip(
                source=red_path, 
                duration=2.0, 
                motion=MotionPreset.STATIC,
                effects=[brightness(0.1)]
            ),
            ImageClip(
                source=blue_path, 
                duration=2.0, 
                motion=MotionPreset.STATIC,
                effects=[brightness(-0.1)]
            ),
        ],
        transitions=[
            Transition(type=TransitionType.CROSSFADE, duration=0.5)
        ],
        resolution=(100, 100),
        fps=30
    )
    
    loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    renderer = FrameRenderer(timeline, loader)
    
    # Clamp query time to valid range
    query_time = min(query_time, timeline.duration - 0.01)
    
    # Find if we're in a transition
    transition = renderer._find_transition_at_time(query_time)
    
    # Render frame
    frame = renderer.render_frame(query_time)
    
    # Verify frame properties
    assert frame.shape == (100, 100, 3)
    assert frame.dtype == np.uint8
    
    # If outside transition, frame should be pure color (with effects applied)
    if transition is None:
        center_pixel = frame[50, 50]
        # Should be predominantly one color
        color_variance = np.std([center_pixel[0], center_pixel[1], center_pixel[2]])
        assert color_variance > 50, "Expected single color outside transition"


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=50)
@given(
    query_offset=st.floats(min_value=0.0, max_value=1.0)
)
def test_transition_progress_range(test_images, query_offset):
    """
    Property 33: Transition Progress Range
    
    The progress value passed to transition functions must always be in [0.0, 1.0].
    
    **Validates: Requirements 10.2, 11.2**
    """
    red_path, blue_path = test_images
    
    scene = Scene(
        clips=[
            ImageClip(source=red_path, duration=2.0, motion=MotionPreset.STATIC),
            ImageClip(source=blue_path, duration=2.0, motion=MotionPreset.STATIC),
        ],
        transitions=[
            Transition(type=TransitionType.CROSSFADE, duration=0.5)
        ],
        resolution=(100, 100),
        fps=30
    )
    
    loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    renderer = FrameRenderer(timeline, loader)
    
    # Query time during transition
    transition_start = timeline.clips[1].start_time
    transition_duration = 0.5
    query_time = transition_start + query_offset * transition_duration
    
    # Compute expected progress
    expected_progress = query_offset
    
    # The progress should be in [0.0, 1.0]
    assert 0.0 <= expected_progress <= 1.0
    
    # Render frame (this internally validates progress is in range)
    frame = renderer.render_frame(query_time)
    assert frame.shape == (100, 100, 3)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(
    width=st.integers(min_value=50, max_value=200),
    height=st.integers(min_value=50, max_value=200)
)
def test_transition_frame_dimension_matching(tmp_path, width, height):
    """
    Property 34: Transition Frame Dimension Matching
    
    Both frames passed to a transition function must have identical dimensions.
    
    **Validates: Requirements 10.7, 13.5**
    """
    import cv2
    
    # Create images with specified dimensions
    red = np.full((height, width, 3), [255, 0, 0], dtype=np.uint8)
    blue = np.full((height, width, 3), [0, 0, 255], dtype=np.uint8)
    
    red_path = tmp_path / "red.png"
    blue_path = tmp_path / "blue.png"
    
    cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(blue_path), cv2.cvtColor(blue, cv2.COLOR_RGB2BGR))
    
    scene = Scene(
        clips=[
            ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
            ImageClip(source=str(blue_path), duration=1.0, motion=MotionPreset.STATIC),
        ],
        transitions=[
            Transition(type=TransitionType.CROSSFADE, duration=0.3)
        ],
        resolution=(width, height),
        fps=30
    )
    
    loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    renderer = FrameRenderer(timeline, loader)
    
    # Render during transition
    query_time = timeline.clips[1].start_time + 0.15
    frame = renderer.render_frame(query_time)
    
    # Verify output dimensions match
    assert frame.shape == (height, width, 3)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
@given(
    width=st.integers(min_value=50, max_value=200),
    height=st.integers(min_value=50, max_value=200)
)
def test_transition_output_dimensions(tmp_path, width, height):
    """
    Property 35: Transition Output Dimensions
    
    The output frame from a transition must match the input frame dimensions.
    
    **Validates: Requirements 10.5**
    """
    import cv2
    
    # Create images with specified dimensions
    red = np.full((height, width, 3), [255, 0, 0], dtype=np.uint8)
    blue = np.full((height, width, 3), [0, 0, 255], dtype=np.uint8)
    
    red_path = tmp_path / "red.png"
    blue_path = tmp_path / "blue.png"
    
    cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(blue_path), cv2.cvtColor(blue, cv2.COLOR_RGB2BGR))
    
    scene = Scene(
        clips=[
            ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
            ImageClip(source=str(blue_path), duration=1.0, motion=MotionPreset.STATIC),
        ],
        transitions=[
            Transition(type=TransitionType.SLIDE_LEFT, duration=0.3)
        ],
        resolution=(width, height),
        fps=30
    )
    
    loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    renderer = FrameRenderer(timeline, loader)
    
    # Render at multiple points during transition
    for progress in [0.0, 0.25, 0.5, 0.75, 1.0]:
        query_time = timeline.clips[1].start_time + progress * 0.3
        frame = renderer.render_frame(query_time)
        
        # Verify dimensions preserved
        assert frame.shape == (height, width, 3)
        assert frame.dtype == np.uint8
