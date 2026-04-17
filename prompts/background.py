"""Background placement and inpainting prompts."""


PLACEMENT_PROMPT = (
    "Side-by-side input: LEFT = full-body person in outfit, "
    "RIGHT = empty scene/location.\n\n"
    "Place the person naturally into the scene. The person must look "
    "physically present: feet on the floor, correct scale (70-85%% of frame "
    "height), lighting and color temperature matched to the scene. Add a "
    "natural contact shadow under the feet.\n\n"
    "Preserve the person identically: same face, expression, hair, pose, "
    "every garment detail, shoes. The person must look real and alive, "
    "not smoothed, not re-rendered, not 3D-looking.\n\n"
    "Output: single 3:4 portrait image. NOT side-by-side. The entire "
    "canvas filled with the final scene edge-to-edge, no borders."
)


def build_inpainting_prompt(location_desc: str, deep_focus: bool = False) -> str:
    """Replace background behind an already-dressed person."""
    focus = (
        "Depth of field: everything in focus, person and background both sharp "
        "(f/8-f/11, like a real on-location photo)."
        if deep_focus else
        "Depth of field: shallow — person sharp, background with natural "
        "photographic bokeh (~f/2.8)."
    )
    return (
        "Background-only replacement. The person (face, hair, skin, pose, "
        "clothing, shoes) is frozen — do not repaint any part of the person. "
        "Only replace the background pixels.\n\n"
        f"New scene: {location_desc}\n\n"
        f"{focus}\n\n"
        "Match scene lighting onto the person's edges: subtle rim light, "
        "contact shadow under feet, ambient color cast. The person must look "
        "physically present in the location.\n\n"
        "Output: single image, same framing."
    )
