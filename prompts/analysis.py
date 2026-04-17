"""Промт анализа — AI выбирает из каталога типов одежды."""
from catalog import GARMENT_TYPES

SYSTEM = "You are a fashion expert. Classify garments from photos."

# Генерируем список ID каталога для промта
_CATALOG_LIST = ", ".join(sorted(GARMENT_TYPES.keys()))

USER = (
    "Look at this garment photo and classify it.\n\n"
    "AVAILABLE TYPE IDs (pick from this list ONLY):\n"
    f"{_CATALOG_LIST}\n\n"
    "TASKS:\n"
    "1. In 'suggestions': pick the TOP 3 most matching type IDs from the list above. "
    "Order by confidence (best match first). Use ONLY IDs from the list.\n"
    "2. In 'styling': suggest 3 outfit ideas (in Russian) — "
    "style_name, bottom (if needed), shoes, accessories."
)
