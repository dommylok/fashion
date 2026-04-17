"""Rotation video prompts."""

EMOTION_VARIANTS = [
    # Lookbook rotation with expressions
    (
        "Same person, same outfit. Natural fashion lookbook sequence: "
        "starts facing camera with a confident smile, makes subtle expression "
        "changes, then slowly rotates 360 degrees (front, side, back, side, "
        "front). Occasional hair adjustment and natural weight shifts. "
        "Alive, warm, cinematic. Stable camera. "
        "Every garment and shoe stays identical throughout."
    ),
    # Over-shoulder glance
    (
        "Same person, same outfit. Starts facing camera with warm smile, "
        "slowly turns to 3/4 back, pauses, looks back over shoulder with "
        "a playful look, then completes the 360 degree turn back to front. "
        "Hand on hip during the pause. Fashion editorial vibe. Stable camera. "
        "Every garment and shoe stays identical throughout."
    ),
    # Runway walk
    (
        "Same person, same outfit. Takes 3-4 confident slow steps toward "
        "camera like a runway walk, stops, shifts weight to one hip, gives "
        "a confident look, then slowly turns 180 degrees and walks away "
        "showing the back. Stable camera follows subtly. "
        "Every garment and shoe stays identical throughout."
    ),
]

NEUTRAL_VARIANTS = [
    # Clean rotation
    (
        "Same person, same outfit. Calm neutral professional expression. "
        "Slowly rotates 360 degrees in place: front, side, back, side, front. "
        "Hands relaxed at sides. Clean professional catalog rotation. "
        "Stable camera. Every garment and shoe stays identical throughout."
    ),
    # Runway serious
    (
        "Same person, same outfit. Serious neutral expression. Takes 3-4 "
        "slow confident steps toward camera, stops, pauses 2 seconds showing "
        "the front, then turns 180 degrees and walks away showing the back. "
        "Stable camera follows. Every garment and shoe stays identical."
    ),
]


def build_video_prompt(with_emotions: bool = True, variant: int = 0) -> str:
    """Build video rotation prompt."""
    pool = EMOTION_VARIANTS if with_emotions else NEUTRAL_VARIANTS
    return pool[variant % len(pool)]
