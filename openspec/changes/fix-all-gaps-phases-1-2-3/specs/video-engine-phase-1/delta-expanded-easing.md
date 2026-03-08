# Delta Spec: Expanded Easing Function Library

## Overview

This delta specification expands the existing video-engine-phase-1 capabilities by implementing the 19 missing easing functions from the original plan. Currently only 4 easing functions are implemented (linear, ease_in_cubic, ease_out_cubic, ease_in_out_cubic).

## Original Spec

The original Phase 1 specification is at `.kiro/specs/video-engine-phase-1/requirements.md`.

## MODIFIED Requirements

### Requirement: Easing Function Library

**Original Requirement 2**: Easing Functions

The System SHALL provide easing functions that control animation timing for smooth, natural-feeling motion.

**MODIFIED**:

The System SHALL implement additional easing functions beyond the current 4:

1. **Quadratic Variants**: The System SHALL provide ease_in_quadratic(t), ease_out_quadratic(t), and ease_in_out_quadratic(t) functions using t² formulas:
   - ease_in_quadratic: t²
   - ease_out_quadratic: 1 - (1-t)²
   - ease_in_out_quadratic: Piecewise quadratic with t<0.5 and t>=0.5

2. **Quartic Variants**: The System SHALL provide ease_in_quartic(t), ease_out_quartic(t), and ease_in_out_quartic(t) functions using t⁴ formulas

3. **Quintic Variants**: The System SHALL provide ease_in_quintic(t), ease_out_quintic(t), and ease_in_out_quintic(t) functions using t⁵ formulas

4. **Exponential Variants**: The System SHALL provide ease_in_exponential(t), ease_out_exponential(t), and ease_in_out_exponential(t) functions using power functions:
   - ease_in_exponential: 2^(10*(t-1))
   - ease_out_exponential: 1 - 2^(-10*t)
   - ease_in_out_exponential: Piecewise exponential with t<0.5 and t>=0.5

5. **Sine Variants**: The System SHALL provide ease_in_sine(t), ease_out_sine(t), and ease_in_out_sine(t) functions using sine-based formulas:
   - ease_in_sine: 1 - cos(t * π/2)
   - ease_out_sine: sin(t * π/2)
   - ease_in_out_sine: Piecewise sine with t<0.5 and t>=0.5

6. **Circular Variants**: The System SHALL provide ease_in_circular(t), ease_out_circular(t), and ease_in_out_circular(t) functions using circular arc formulas:
   - ease_in_circular: 1 - sqrt(1 - t²)
   - ease_out_circular: sqrt(1 - (1-t)²)
   - ease_in_out_circular: Piecewise circular with t<0.5 and t>=0.5

7. **Elastic Variants**: The System SHALL provide ease_in_elastic(t), ease_out_elastic(t), and ease_in_out_elastic(t) functions with sine-based oscillation that decays exponentially

8. **Back Variants**: The System SHALL provide ease_in_back(t), ease_out_back(t), and ease_in_out_back(t) functions with cubic overshoot and bounce effect using overshoot constant c=1.70158

9. **Spring Function**: The System SHALL provide a spring(t) function that simulates a damped spring oscillation using scipy.interpolate.interp1d and physics-based formula

10. **Bezier Curve**: The System SHALL provide a cubic_bezier(t) function that evaluates a cubic Bezier curve with control points for custom animation curves

11. **Step Function**: The System SHALL provide a step(t, num_steps) function that creates quantized, stepped progression

12. **Cubic Spline**: The System SHALL provide a cubic_spline(t, control_points) function that creates smooth interpolation through multiple control points using scipy.interpolate.CubicSpline

#### Scenario: Applying quadratic easing

- **WHEN** user applies ease_in_quadratic to an animation
- **THEN** the animation starts slow and accelerates quadratically (t²), creating a smooth acceleration effect

#### Scenario: Applying elastic easing

- **WHEN** user applies ease_in_elastic to an animation
- **THEN** the animation overshoots and oscillates with decreasing amplitude, creating a bouncy elastic effect

#### Scenario: Applying spring easing

- **WHEN** user applies spring easing to an animation
- **THEN** the animation oscillates with damped spring physics, creating a realistic springy motion

#### Scenario: Applying cubic spline

- **WHEN** user applies cubic_spline with multiple control points
- **THEN** the animation follows a smooth curve through all control points, enabling complex custom animation paths

### Requirement: Motion Presets Expansion

**Original Requirement 4**: Motion Presets

The System SHALL provide motion presets that define camera movement patterns.

**MODIFIED**:

The System SHALL add the SLOW_ZOOM_IN motion preset to the MotionPreset enum and implement it in compute_motion_path():

1. **SLOW_ZOOM_IN**: The System SHALL provide a slow zoom in preset where the camera gradually zooms in over the clip duration (0.75x to 1.0x scale, similar to KEN_BURNS_ZOOM_IN but slower)

#### Scenario: Using SLOW_ZOOM_IN motion preset

- **WHEN** user specifies MotionPreset.SLOW_ZOOM_IN in an ImageClip
- **THEN** the camera slowly zooms in from 75% to 100% scale over the clip duration with ease_in_out_cubic easing, creating a gentle, gradual zoom effect

## ADDED Requirements

### Requirement: Easing Function Exports

The System SHALL export all new easing functions in `engine/__init__.py` for public API access.

#### Scenario: Importing new easing functions

- **WHEN** user imports from engine (e.g., `from engine import ease_in_quadratic, spring, cubic_bezier`)
- **THEN** the functions are available and can be used in custom animations

## REMOVED Requirements

None - No requirements are removed, only expanded with new functionality.

## RENAMED Requirements

None - No requirement names are changed.
