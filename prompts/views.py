"""Back/side view and pose prompts.

Key principle: input is the FIRST GENERATION RESULT (the person already dressed).
This is the ground truth. All subsequent views must match it exactly.
"""

OUTFIT_LOCK = (
    "OUTFIT LOCK: The input image is the GROUND TRUTH. Every garment on the "
    "person must appear IDENTICAL in the output: same color, same fabric, same "
    "length, same fit, same every detail (buttons, zippers, belt, pockets, "
    "logos, stitching, shoes). Do NOT change the length — if the jacket ends "
    "at the hips, it must end at the hips in every panel. Do NOT add, remove, "
    "or restyle any piece of clothing."
)


def build_back_side_prompt(garment_desc: str) -> str:
    """Generate 2 panels: over-shoulder + 3/4 back view.
    Input: the full-body result from the first generation (single image)."""
    return (
        f"The person in the input image is wearing: {garment_desc}.\n\n"
        f"{OUTFIT_LOCK}\n\n"
        "Preserve the person's identity: same face, hair, body, skin tone.\n\n"
        "Output: two side-by-side panels, 3:2 aspect ratio.\n"
        "LEFT panel: same person turned ~135 degrees away, looking back over "
        "shoulder at camera with a natural smile. Full body head-to-toe.\n"
        "RIGHT panel: same person in 3/4 back view (~100 degrees), slight "
        "contrapposto, hand on hip. Profile visible. Full body head-to-toe.\n"
        "Both panels: same person, same outfit (every detail identical to input), "
        "same background."
    )


POSE_VARIANTS = [
    (
        "LEFT panel: confident contrapposto, ~20 degrees from camera, "
        "weight on one hip, hand in pocket or on hip, soft smile.\n"
        "RIGHT panel: walking toward camera, mid-stride, natural arm "
        "swing, relaxed confident expression."
    ),
    (
        "LEFT panel: casual weight shift to one side, arms loosely "
        "crossed, warm relaxed expression.\n"
        "RIGHT panel: looking down at outfit appreciatively, one hand "
        "adjusting collar or hem, candid fashion moment."
    ),
    (
        "LEFT panel: facing camera straight, one hand on waist, chin "
        "slightly up, editorial confidence.\n"
        "RIGHT panel: body turned ~60 degrees away, head turned back "
        "looking at camera over shoulder, playful smile."
    ),
]


def build_poses_prompt(garment_desc: str, variant: int = 0) -> str:
    """Generate 2 panels with fashion poses.
    Input: the full-body result from the first generation (single image)."""
    poses = POSE_VARIANTS[variant % len(POSE_VARIANTS)]
    return (
        f"The person in the input image is wearing: {garment_desc}.\n\n"
        f"{OUTFIT_LOCK}\n\n"
        "Preserve the person's identity: same face, hair, body, skin tone.\n\n"
        "Output: two side-by-side panels, full body head-to-toe, 3:2.\n"
        f"{poses}\n"
        "Both panels: same person, outfit IDENTICAL to input image "
        "(every color, length, detail, shoes unchanged)."
    )
