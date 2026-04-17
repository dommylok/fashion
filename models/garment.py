from pydantic import BaseModel, Field
from typing import Optional
from catalog import GARMENT_TYPES


class GarmentSuggestion(BaseModel):
    """Один вариант типа для распознанной вещи."""
    type_id: str = Field(description="ID из каталога типов одежды")


class DetectedGarment(BaseModel):
    """Одна распознанная вещь на фото (верх ИЛИ низ ИЛИ платье)."""
    position: str = Field(
        description="Где вещь на фото: 'top' (верх), 'bottom' (низ), 'dress' (платье/комбинезон), 'full' (цельный образ)"
    )
    suggestions: list[GarmentSuggestion] = Field(
        description="Top 3 matching type IDs from the catalog for this garment"
    )


class OutfitSuggestion(BaseModel):
    """Рекомендация стилиста."""
    style_name: str = Field(description="Название стиля: 'Кэжуал', 'Элегант' и т.д.")
    bottom: Optional[str] = Field(default=None, description="Низ если нужен, на русском")
    shoes: str = Field(description="Обувь на русском")
    accessories: Optional[str] = Field(default=None, description="Аксессуары на русском")

    def to_card_text(self, index: int) -> str:
        parts = [f"<b>{index}. {self.style_name}</b>"]
        if self.bottom:
            parts.append(f"   Низ: {self.bottom}")
        parts.append(f"   Обувь: {self.shoes}")
        if self.accessories:
            parts.append(f"   Аксессуары: {self.accessories}")
        return "\n".join(parts)

    def to_prompt(self) -> str:
        parts = []
        if self.bottom:
            parts.append(self.bottom)
        parts.append(self.shoes)
        if self.accessories:
            parts.append(self.accessories)
        return f"{self.style_name}: " + ", ".join(parts)


class GarmentAnalysis(BaseModel):
    """Анализ фото: 1-2 вещи + стайлинг."""

    items: list[DetectedGarment] = Field(
        description="All distinct garments visible in the photo. "
        "A suit (jacket + pants) = 2 items (top + bottom). "
        "A single jacket = 1 item. A dress/jumpsuit = 1 item."
    )
    styling: list[OutfitSuggestion] = Field(
        description="Exactly 3 diverse outfit suggestions in Russian."
    )

    def items_summary(self) -> str:
        """Краткая сводка распознанных вещей."""
        if len(self.items) == 1:
            item = self.items[0]
            top_suggestion = item.suggestions[0].type_id if item.suggestions else "?"
            t = GARMENT_TYPES.get(top_suggestion, {})
            return f"Обнаружена 1 вещь: {t.get('name_ru', top_suggestion)}"

        parts = [f"Обнаружено {len(self.items)} вещей:"]
        for item in self.items:
            top = item.suggestions[0].type_id if item.suggestions else "?"
            t = GARMENT_TYPES.get(top, {})
            pos_ru = {"top": "Верх", "bottom": "Низ", "dress": "Платье", "full": "Образ"}
            parts.append(f"• {pos_ru.get(item.position, item.position)}: {t.get('name_ru', top)}")
        return "\n".join(parts)

    def styling_card_text(self) -> str:
        lines = ["<b>Рекомендации AI-стилиста:</b>"]
        for i, s in enumerate(self.styling):
            lines.append(s.to_card_text(i + 1))
        return "\n\n".join(lines)
