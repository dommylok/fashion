"""Промт анализа — тип фото + распознавание 1-2 вещей + стайлинг."""
from catalog import GARMENT_TYPES

SYSTEM = "You are a fashion expert. Classify garments from photos."

_CATALOG_LIST = ", ".join(sorted(GARMENT_TYPES.keys()))

USER = (
    "Analyze this garment photo.\n\n"

    "STEP 0: DETECT photo_type (how the garment is photographed):\n"
    "- 'hanger' — clothing hangs on a hanger/тремпель, often wrinkled, length hard to see\n"
    "- 'mannequin' — clothing displayed on a mannequin (headless figure)\n"
    "- 'person' — clothing worn by a real person (full figure visible)\n"
    "- 'flat_lay' — clothing laid flat on a surface from above\n\n"

    "STEP 1: COUNT DISTINCT GARMENTS:\n"
    "- Single jacket alone = 1 garment\n"
    "- Single pants alone = 1 garment\n"
    "- Dress or jumpsuit = 1 garment\n"
    "- A suit / tracksuit with TOP + BOTTOM visible together = 2 garments\n\n"

    "STEP 2: For EACH garment, set 'position':\n"
    "- 'top' — upper body (jacket, shirt, sweater, etc.)\n"
    "- 'bottom' — lower body (pants, jeans, shorts, skirt)\n"
    "- 'dress' — dress or jumpsuit\n"
    "- 'full' — whole outfit as one concept\n\n"

    "STEP 3: For EACH garment, pick TOP 3 matching type IDs from this list:\n"
    f"{_CATALOG_LIST}\n\n"

    "STEP 4: In 'styling' — 3 diverse outfit suggestions in Russian "
    "(style_name, bottom, shoes, accessories).\n\n"

    "IMPORTANT: The number of items in 'items' MUST match the number of "
    "DISTINCT garments you see. Don't duplicate the same garment."
)
