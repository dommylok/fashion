"""Try-on промт — короткий и чёткий (рабочий формат)."""
from catalog import build_smart_description


def _build_item_description(item: dict) -> tuple[str, str]:
    return build_smart_description(
        item["type_id"],
        length_id=item.get("length_id"),
        fit_id=item.get("fit_id"),
    )


def build_tryon_prompt(
    items_chosen: list[dict],
    scene: str | None = None,
    outfit_style: str | None = None,
) -> str:
    """Короткий рабочий промт. Всё усиление — внутри описания в кавычках."""

    if len(items_chosen) == 1:
        ru, en = _build_item_description(items_chosen[0])
        desc = f"«{ru} ({en})»"
    else:
        parts_ru, parts_en = [], []
        for item in items_chosen:
            ru, en = _build_item_description(item)
            parts_ru.append(ru)
            parts_en.append(en)
        desc = f"«верх + низ: {', '.join(parts_ru)} ({', '.join(parts_en)})»"

    style_block = ""
    if outfit_style:
        style_block = f"\n\nДополни образ: {outfit_style}."

    scene_block = ""
    if scene:
        scene_block = f"\n\nФон: {scene}. Реальное фото, всё в фокусе."

    return (
        "Используй ТОЧНУЮ одежду с ПЕРВОЙ загруженной фотографии (reference clothing photo). "
        f"Это {desc}.\n\n"

        "Перенеси на модель ВСЕ детали одежды 1:1: цвет, фактуру, надписи, "
        "логотипы, пуговицы, молнии, пряжки, карманы, швы, воротник, манжеты, "
        "пояса, вышивку, принты, фурнитуру. Pixel-perfect.\n\n"

        "Убери вешалки, бирки, ценники, наклейки, упаковку. "
        "Пришивные лейблы оставь.\n\n"

        "Одень эту одежду на модель со ВТОРОЙ фотографии. "
        "Лицо, причёска, поза, тело модели — 1:1."
        f"{style_block}{scene_block}\n\n"
        "Фотореализм, полный рост, 3:4."
    )
