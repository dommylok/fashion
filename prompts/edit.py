"""Prompt for targeted image editing — change only what the user asks."""


def build_edit_prompt(user_request: str, garment_desc: str) -> str:
    """Build a targeted edit prompt.

    The user describes what to change (e.g. 'сделай штаны длиннее',
    'смени обувь на кроссовки', 'фон темнее'). Everything else stays identical.
    """
    return (
        f"The input image shows a person wearing: {garment_desc}.\n\n"
        f"EDIT REQUEST: {user_request}\n\n"
        "Change ONLY what is requested above. Keep everything else absolutely "
        "identical: same person, same face, same hair, same pose, same garments "
        "(except the ones being edited), same background (unless background "
        "change is requested).\n\n"
        "The result must look like the same photo with a minimal targeted edit, "
        "not a new generation. Real photo quality, everything in focus."
    )
