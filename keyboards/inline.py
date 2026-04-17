"""Все inline-клавиатуры бота."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# --- Загрузка одежды ---

def analyze_kb() -> InlineKeyboardMarkup:
    """Кнопка 'Анализировать' после загрузки фото."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Анализировать", callback_data="garment:analyze"),
    )
    return builder.as_markup()


# --- Выбор типа одежды ---

def type_suggestions_kb(suggestions: list[dict]) -> InlineKeyboardMarkup:
    """Кнопки: 3 AI-предложения + 'Другое' + 'Свой промт'."""
    from catalog import GARMENT_TYPES
    builder = InlineKeyboardBuilder()
    for i, s in enumerate(suggestions):
        type_id = s.get("type_id", "")
        t = GARMENT_TYPES.get(type_id)
        label = t["name_ru"] if t else type_id
        builder.button(text=f"{i + 1}. {label}", callback_data=f"type:{type_id}")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="Другое →", callback_data="type:other"))
    builder.row(InlineKeyboardButton(text="✍️ Свой промт", callback_data="type:custom_prompt"))
    return builder.as_markup()


def type_groups_kb() -> InlineKeyboardMarkup:
    """Группы типов одежды (если AI не угадал)."""
    from catalog import GROUPS
    builder = InlineKeyboardBuilder()
    for group_id, label in GROUPS.items():
        builder.button(text=label, callback_data=f"group:{group_id}")
    builder.adjust(2)
    return builder.as_markup()


def type_list_kb(group: str) -> InlineKeyboardMarkup:
    """Список типов в группе."""
    from catalog import get_types_by_group
    builder = InlineKeyboardBuilder()
    for type_id, name_ru in get_types_by_group(group):
        builder.button(text=name_ru, callback_data=f"type:{type_id}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="type:other"))
    return builder.as_markup()


def length_kb() -> InlineKeyboardMarkup:
    """Выбор длины — опционально."""
    from catalog import LENGTHS
    builder = InlineKeyboardBuilder()
    for lid, l in LENGTHS.items():
        builder.button(text=l["label_ru"], callback_data=f"length:{lid}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="⏭ По фото", callback_data="length:auto"))
    return builder.as_markup()


def fit_kb() -> InlineKeyboardMarkup:
    """Выбор посадки — опционально."""
    from catalog import FITS
    builder = InlineKeyboardBuilder()
    for fid, f in FITS.items():
        builder.button(text=f["label_ru"], callback_data=f"fit:{fid}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="⏭ По фото", callback_data="fit:auto"))
    return builder.as_markup()


# --- Стиль образа (AI-рекомендации) ---

def styling_kb() -> InlineKeyboardMarkup:
    """Кнопки выбора стайлинга: 1, 2, 3 + свой вариант."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="1", callback_data="style:0"),
        InlineKeyboardButton(text="2", callback_data="style:1"),
        InlineKeyboardButton(text="3", callback_data="style:2"),
    )
    builder.row(
        InlineKeyboardButton(text="Свой вариант", callback_data="style:custom"),
    )
    return builder.as_markup()


# --- Выбор модели ---

def model_select_kb(model_names: list[str]) -> InlineKeyboardMarkup:
    """Нумерованные кнопки 1-10 + Ещё."""
    builder = InlineKeyboardBuilder()
    for i, name in enumerate(model_names):
        builder.button(text=str(i + 1), callback_data=f"model:{name}")
    builder.adjust(5, 5)
    builder.row(
        InlineKeyboardButton(text="Другие модели", callback_data="model:more"),
    )
    return builder.as_markup()


# --- Фон ---

# Все сцены с текстовыми промтами для Grok
# Промты написаны так чтобы фон был РЕАЛИСТИЧНЫЙ — как настоящее фото,
# без боке, без фокуса на модели, всё в фокусе (f/8-f/11)
SCENES = {
    # --- Магазины ---
    "boutique": {
        "label": "🛍 Бутик",
        "category": "retail",
        "prompt": (
            "inside a real luxury fashion boutique, clothes on racks, large mirrors, "
            "warm spotlights, marble floor, everything in focus like a real photo taken "
            "on a phone, f/8, no bokeh, no blur, photorealistic"
        ),
    },
    "luxury_store": {
        "label": "💎 Luxury магазин",
        "category": "retail",
        "prompt": (
            "inside a high-end luxury flagship store, polished marble floor, glass "
            "display cases, architectural lighting, gold and cream tones, everything "
            "sharp and in focus, real photo look, f/8, no bokeh"
        ),
    },
    "showroom": {
        "label": "🏛 Шоурум",
        "category": "retail",
        "prompt": (
            "inside a minimal concrete showroom, neutral walls, soft diffused daylight "
            "from tall windows, clean contemporary architecture, everything in focus, "
            "real photo, f/8, no bokeh"
        ),
    },
    "mall": {
        "label": "🛒 Торговый центр",
        "category": "retail",
        "prompt": (
            "inside a bright modern shopping mall atrium, large windows, clean floors, "
            "storefronts visible, natural daylight, everything in focus, real phone "
            "photo look, f/8, no bokeh"
        ),
    },
    # --- Город ---
    "city_day": {
        "label": "🏙 Улица днём",
        "category": "urban",
        "prompt": (
            "on a european city street during the day, historic facades, sidewalk, "
            "natural soft daylight, everything in focus like a real street photo, "
            "f/8, no bokeh, no blur, photorealistic"
        ),
    },
    "night_street": {
        "label": "🌃 Ночная улица",
        "category": "urban",
        "prompt": (
            "on a city street at night with glowing neon signs, reflections on wet "
            "asphalt, streetlights, urban atmosphere, everything in focus, real "
            "night photo, no artificial bokeh"
        ),
    },
    "rooftop": {
        "label": "🏢 Крыша с видом",
        "category": "urban",
        "prompt": (
            "on a rooftop terrace with panoramic city skyline, golden hour sunlight, "
            "wide view, everything in focus, real photo, f/8, no bokeh"
        ),
    },
    "subway": {
        "label": "🚇 Метро",
        "category": "urban",
        "prompt": (
            "inside a modern subway station platform, tiled walls, cold lighting, "
            "clean architecture, everything sharp and in focus, real photo, "
            "f/8, no bokeh"
        ),
    },
    "industrial": {
        "label": "🏭 Индастриал / парковка",
        "category": "urban",
        "prompt": (
            "inside a raw concrete parking garage, rough walls, moody cold overhead "
            "lamps, industrial atmosphere, everything in focus, real photo, "
            "f/8, no bokeh"
        ),
    },
    # --- Интерьеры ---
    "loft": {
        "label": "🏠 Лофт",
        "category": "interior",
        "prompt": (
            "inside a spacious modern loft apartment, large windows, concrete floor, "
            "designer furniture, soft daylight, warm neutral tones, everything in "
            "focus, real interior photo, f/8, no bokeh"
        ),
    },
    "bedroom": {
        "label": "🛏 Спальня",
        "category": "interior",
        "prompt": (
            "inside a minimalist bedroom, soft bedding, natural window light, cream "
            "and beige tones, everything in focus, real lifestyle photo, f/8, no bokeh"
        ),
    },
    "kitchen": {
        "label": "🍳 Кухня",
        "category": "interior",
        "prompt": (
            "inside a modern scandinavian kitchen, marble countertop, white cabinets, "
            "natural daylight through window, everything in focus, real photo, "
            "f/8, no bokeh"
        ),
    },
    "hotel_lobby": {
        "label": "🏨 Лобби отеля",
        "category": "interior",
        "prompt": (
            "inside a luxury hotel lobby, elegant chandeliers, marble floor, plush "
            "seating, warm ambient lighting, everything in focus, real photo, "
            "f/8, no bokeh"
        ),
    },
    "cafe": {
        "label": "☕ Кафе",
        "category": "interior",
        "prompt": (
            "inside a stylish cafe with warm ambient lighting, wooden tables, coffee "
            "bar, cozy atmosphere, everything in focus, real interior photo, "
            "f/8, no bokeh"
        ),
    },
    # --- Природа ---
    "beach": {
        "label": "🏖 Пляж",
        "category": "nature",
        "prompt": (
            "on a sandy beach with ocean waves, golden hour sunlight, warm tones, "
            "everything in focus, real beach photo, f/8, no bokeh, no blur"
        ),
    },
    "forest": {
        "label": "🌳 Парк / лес",
        "category": "nature",
        "prompt": (
            "in a forest park with tall trees, dappled sunlight through leaves, "
            "green foliage, natural daylight, everything in focus, real outdoor "
            "photo, f/8, no bokeh"
        ),
    },
    "desert": {
        "label": "🏜 Пустыня",
        "category": "nature",
        "prompt": (
            "in a desert landscape with sand dunes and distant mountains, warm "
            "sunset light, wide vista, everything in focus, real photo, f/8, no bokeh"
        ),
    },
    "garden": {
        "label": "🌸 Сад / цветы",
        "category": "nature",
        "prompt": (
            "in a blooming garden with colorful flowers and lush greenery, golden "
            "hour light, everything in focus, real garden photo, f/8, no bokeh"
        ),
    },
}

# Категории для группировки сцен
SCENE_CATEGORIES = {
    "retail": "🛍 Магазины",
    "urban": "🏙 Город",
    "interior": "🏠 Интерьеры",
    "nature": "🌿 Природа",
}


def bg_type_kb() -> InlineKeyboardMarkup:
    """Белый фон или сцена."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Белый фон", callback_data="bg_type:white"),
        InlineKeyboardButton(text="На фоне", callback_data="bg_type:scene"),
    )
    return builder.as_markup()


def bg_category_kb() -> InlineKeyboardMarkup:
    """Выбор категории фона."""
    builder = InlineKeyboardBuilder()
    for key, label in SCENE_CATEGORIES.items():
        builder.button(text=label, callback_data=f"bg_cat:{key}")
    builder.adjust(2, 2)
    return builder.as_markup()


def bg_scene_kb(category: str) -> InlineKeyboardMarkup:
    """Список сцен в категории."""
    builder = InlineKeyboardBuilder()
    for key, scene in SCENES.items():
        if scene["category"] == category:
            builder.button(text=scene["label"], callback_data=f"bg_scene:{key}")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="bg:back_categories"))
    return builder.as_markup()


# --- Пост-генерация ---

def post_result_kb() -> InlineKeyboardMarkup:
    """Действия после генерации."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ Изменить", callback_data="post:edit"),
        InlineKeyboardButton(text="✍️ Новый промт", callback_data="post:new_prompt"),
    )
    builder.row(
        InlineKeyboardButton(text="Спина + бок", callback_data="post:back_side"),
        InlineKeyboardButton(text="Позы", callback_data="post:poses"),
    )
    builder.row(
        InlineKeyboardButton(text="Видео", callback_data="post:video"),
        InlineKeyboardButton(text="Сменить фон", callback_data="post:change_bg"),
    )
    builder.row(
        InlineKeyboardButton(text="Новая вещь", callback_data="post:new"),
    )
    return builder.as_markup()


def video_style_kb() -> InlineKeyboardMarkup:
    """Стиль видео."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="С эмоциями", callback_data="video:emotion"),
        InlineKeyboardButton(text="Нейтральное", callback_data="video:neutral"),
    )
    return builder.as_markup()
