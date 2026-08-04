# Effect and Transition Validity for an Image

## Problem

Users do not know which effects and transitions are **valid** for a given image. The engine accepts any effect and any transition on any clip; there is no guidance, validation, or recommendation tied to the image.

## Current Behavior

- **Scene / ImageClip**: No validation of which effects or transitions are “allowed” for a clip. Any `EffectFunction` can be in `ImageClip.effects`; any `TransitionType` can be in `Scene.transitions`.
- **Planner**: Validates only transition **count** and **duration** (positive, and ≤ min of adjacent clip durations). It loads each image to get dimensions for the camera path but does not attach image metadata (aspect ratio, resolution, etc.) to clips or use it for effect/transition validity.
- **Renderer**: When applying effects, validates only that each effect preserves **frame shape** and **dtype** (H×W×3 uint8). When blending a transition, validates that both frames have the same shape (always true at output resolution). No check that an effect or transition is “valid for this image.”

So today, **technically** every effect and every transition is valid for every image in the sense: “it will run.” There is no notion of “valid for this image” in the codebase.

## What “Valid” Could Mean

| Sense | Meaning | Example |
|-------|--------|--------|
| **Technical** | The pipeline runs without error and output is correct. | Effect preserves shape/dtype; transition gets two frames of same size. |
| **Constraint-based** | The effect/transition has documented preconditions (e.g. minimum resolution, aspect ratio). | “Motion blur looks correct only if image width ≥ 320px.” |
| **Semantic / best-for** | Guidance on what works well for an image type or use case. | “Letterbox is best for non-16:9 source”; “Vignette works well for portraits.” |

The problem users face is a mix of (2) and (3): they don’t know constraints (if any) or what is recommended for a given image.

## Possible Directions

### A. Documentation only (no code change)

- Add a **guide** (e.g. in `docs/`) that describes:
  - **Effects**: any technical constraints (min resolution, aspect, etc.) and “best for” hints (e.g. portrait, landscape, photo vs illustration).
  - **Transitions**: any constraints and “best for” hints (e.g. similar vs contrasting adjacent images).
- **Pros**: No API or runtime change; fast to add.  
- **Cons**: Not machine-readable; no runtime validation or recommendations.

### B. Optional runtime validation

- Define a small set of **technical** rules (e.g. minimum size for certain blurs, or “letterbox only when aspect ≠ output aspect”).
- At **plan** or **render** time, optionally check each clip’s image (dimensions, aspect) against the chosen effect list and warn or raise if a constraint is violated.
- **Pros**: Catches clear mismatches before render.  
- **Cons**: Requires defining and maintaining constraints in code; risk of false positives if rules are too strict.

### C. Recommendation API (read-only)

- Attach to each clip (at plan time) **image metadata**: dimensions, aspect ratio, perhaps simple “orientation” (portrait/landscape/square).
- Provide a **recommendation** helper (e.g. “suggested effects for this clip” / “suggested transitions between clip A and B”) that returns lists of effect/transition names or enums based on metadata and optional policy (e.g. “cinematic,” “minimal,” “stylized”).
- **Pros**: Users and UIs can show “valid” or “recommended” options without hard validation.  
- **Cons**: Requires defining and maintaining the recommendation rules (e.g. in data or code).

### D. Combination

- **Docs** for humans (constraints + “best for”).
- **Optional validation** for technical constraints only.
- **Optional recommendation** API for “what works well” without blocking any choice.

## Requirements (if we implement validity)

- The system SHALL NOT prevent users from applying any effect or transition that is technically valid (shape/dtype preserved); any “validity” feature SHALL be advisory or opt-in validation, not a hard block.
- If we add constraint-based validation, the system SHALL document each effect’s and transition’s technical constraints (e.g. min resolution, aspect) in a single place (docs or code comments).
- If we add a recommendation API, the system SHALL expose “suggested” effects/transitions based on image metadata (e.g. dimensions, aspect) and SHALL allow the user to ignore suggestions.

## Non-goals (for this spec)

- Defining the exact list of “best for” recommendations (that can be a follow-up task or data file).
- Enforcing validity in the core render path by default (no mandatory blocking).

## Summary

| Item | Status |
|------|--------|
| Current validity model | None; any effect/transition runs on any clip. |
| “Valid” definition | Can be technical (runs), constraint-based (meets preconditions), or semantic (recommended). |
| Recommended next step | Add documentation (A) so users know constraints and “best for”; then consider (B) or (C) if needed. |
