"""Try-on промт — рабочая формула с кавычками, без семантических якорей."""
from catalog import build_smart_description


def build_tryon_prompt(
    type_id: str,
    length_id: str | None = None,
    fit_id: str | None = None,
    scene: str | None = None,
    outfit_style: str | None = None,
) -> str:
    """Универсальный промт по рабочей формуле Grok."""

    ru_desc, en_desc = build_smart_description(type_id, length_id, fit_id)

    style_block = ""
    if outfit_style:
        style_block = f"\n\nДополни образ: {outfit_style}."

    scene_block = ""
    if scene:
        scene_block = (
            f"\n\nФон: {scene}. Реальное фото на 35mm f/8, всё в фокусе, "
            "street photography."
        )

    return (
        "Используй ТОЧНУЮ одежду с ПЕРВОЙ загруженной фотографии (reference clothing photo). "
        f"Это «{ru_desc} ({en_desc})».\n\n"
        "Одень эту одежду на модель со ВТОРОЙ загруженной фотографии. "
        "Сохрани лицо, причёску, позу, тело, макияж и пропорции модели 1:1. "
        "Одежда должна сидеть естественно поверх нижних слоёв или заменять верх, "
        "как логично для этого типа одежды."
        f"{style_block}{scene_block}\n\n"
        "Фотографический реализм, высокое качество, естественное освещение, "
        "точное соответствие референсу, полный рост 3:4."
    )
