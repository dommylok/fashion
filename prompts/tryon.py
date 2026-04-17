"""Try-on промт — длина в самом начале, ДО слова 'trench'."""
from catalog import build_smart_description, get_length_hard_instruction


def _build_item_description(item: dict) -> tuple[str, str, str]:
    """Вернуть (ru, en, length_id) для одной вещи."""
    ru, en = build_smart_description(
        item["type_id"],
        length_id=item.get("length_id"),
        fit_id=item.get("fit_id"),
    )
    return ru, en, item.get("length_id") or ""


def build_tryon_prompt(
    items_chosen: list[dict],
    scene: str | None = None,
    outfit_style: str | None = None,
    photo_type: str = "hanger",
) -> str:
    """Промт с жёсткой инструкцией длины в начале."""

    # Собираем описания и инструкции длины
    descs_ru, descs_en = [], []
    hard_instructions = []
    for item in items_chosen:
        ru, en, lid = _build_item_description(item)
        descs_ru.append(ru)
        descs_en.append(en)
        instr = get_length_hard_instruction(lid)
        if instr:
            hard_instructions.append(instr)

    if len(items_chosen) == 1:
        desc = f"«{descs_ru[0]} ({descs_en[0]})»"
    else:
        desc = f"«верх + низ: {', '.join(descs_ru)} ({', '.join(descs_en)})»"

    # Блок про вешалку — только если фото на вешалке/flat_lay
    hanger_warning = ""
    if photo_type in ("hanger", "flat_lay"):
        hanger_warning = (
            "ВНИМАНИЕ: одежда на референс-фото висит на вешалке (скомкана, складки, "
            "висит криво). Визуально точную длину по фото ОПРЕДЕЛИТЬ НЕВОЗМОЖНО. "
            "ИГНОРИРУЙ попытки угадать длину по фото — следуй ТОЛЬКО текстовому "
            "описанию длины ниже.\n\n"
        )

    # Блок жёстких инструкций по длине
    length_block = ""
    if hard_instructions:
        length_block = (
            "ДЛИНА (критически важно, read first):\n"
            + "\n".join(f"• {h}" for h in hard_instructions)
            + "\n\nНЕ используй свои стандартные знания о типичной длине "
            "тренчей, курток, пальто. Следуй ТОЛЬКО инструкции длины выше.\n\n"
        )

    style_block = ""
    if outfit_style:
        style_block = f"\n\nДополни образ: {outfit_style}."

    scene_block = ""
    if scene:
        scene_block = f"\n\nФон: {scene}. Реальное фото, всё в фокусе."

    return (
        f"{hanger_warning}"
        f"{length_block}"

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

        # Повтор инструкции длины в конце
        + (f"Напоминание: {hard_instructions[0]}\n\n" if hard_instructions else "") +

        "AVOID: wrong length, altered hem, classic long trench, elongated jacket, "
        "changed silhouette, deformed clothing, store tags, hangers.\n\n"

        "Фотореализм, полный рост, 3:4."
    )
