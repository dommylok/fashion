"""Промт анализа — распознавание 1-2 вещей на фото + стайлинг."""
from catalog import GARMENT_TYPES

SYSTEM = "You are a fashion expert. Classify garments from photos."

_CATALOG_LIST = ", ".join(sorted(GARMENT_TYPES.keys()))

USER = (
    "Look at this garment photo carefully.\n\n"
    "STEP 1: COUNT DISTINCT GARMENTS visible on the photo.\n"
    "- Single jacket alone = 1 garment\n"
    "- Single pants alone = 1 garment\n"
    "- Dress or jumpsuit = 1 garment\n"
    "- A suit / tracksuit / outfit with TOP + BOTTOM visible together = 2 garments\n"
    "- If only upper body clothing visible = 1 garment\n"
    "- If only lower body clothing visible = 1 garment\n\n"
    "STEP 2: For EACH garment, set 'position':\n"
    "- 'top' — upper body (jacket, shirt, sweater, t-shirt, etc.)\n"
    "- 'bottom' — lower body (pants, jeans, shorts, skirt)\n"
    "- 'dress' — dress or jumpsuit (full body single piece)\n"
    "- 'full' — whole outfit as one concept\n\n"
    "STEP 3: For EACH garment, pick TOP 3 matching type IDs from this list:\n"
    f"{_CATALOG_LIST}\n\n"
    "STEP 4: In 'styling' — 3 diverse outfit suggestions in Russian "
    "(style_name, bottom, shoes, accessories).\n\n"
    "IMPORTANT: The number of items in 'items' MUST match the number of "
    "DISTINCT garments you see. Don't duplicate the same garment as multiple items."
)
