from pydantic import BaseModel, Field
from typing import Optional
from catalog import GARMENT_TYPES, build_ai_name


class GarmentSuggestion(BaseModel):
    """AI предлагает 1 вариант типа из каталога."""
    type_id: str = Field(description="ID из каталога типов одежды")
    confidence: str = Field(description="high / medium / low")


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
    """Анализ фото — AI предлагает 3 варианта типа из каталога + стайлинг."""

    suggestions: list[GarmentSuggestion] = Field(
        description="Top 3 matching garment types from the catalog, ordered by confidence."
    )
    styling: list[OutfitSuggestion] = Field(
        description="Exactly 3 diverse outfit suggestions. All text in Russian."
    )

    def suggestions_card_text(self) -> str:
        """Карточка с вариантами для пользователя."""
        lines = ["<b>Что на фото?</b>"]
        for i, s in enumerate(self.suggestions):
            t = GARMENT_TYPES.get(s.type_id)
            if t:
                lines.append(f"{i + 1}. {t['name_ru']}")
            else:
                lines.append(f"{i + 1}. {s.type_id}")
        return "\n".join(lines)

    def styling_card_text(self) -> str:
        lines = ["<b>Рекомендации AI-стилиста:</b>"]
        for i, s in enumerate(self.styling):
            lines.append(s.to_card_text(i + 1))
        return "\n\n".join(lines)

    def garment_name_en(self, chosen_type_id: str | None = None) -> str:
        """AI-friendly английское название для промта."""
        type_id = chosen_type_id or (self.suggestions[0].type_id if self.suggestions else "jacket")
        return build_ai_name(type_id)
