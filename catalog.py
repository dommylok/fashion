"""Каталог типов одежды с AI-friendly английскими названиями.

Каждый тип имеет:
- id: уникальный ключ
- name_ru: русское название (для пользователя)
- name_en: английское название (для промта Grok Imagine)
- category: upper_body / lower_body / dresses / full_body
- group: группа для UI-кнопок
- default_length: длина по умолчанию
- default_fit: посадка по умолчанию
"""

# ============================================================
# ТИПЫ ОДЕЖДЫ
# ============================================================

GARMENT_TYPES: dict[str, dict] = {
    # --- ВЕРХНЯЯ ОДЕЖДА: Куртки ---
    "bomber":           {"name_ru": "Бомбер",                "name_en": "bomber jacket",              "category": "upper_body", "group": "jackets", "default_length": "short", "default_fit": "regular"},
    "denim_jacket":     {"name_ru": "Джинсовая куртка",      "name_en": "denim jacket",               "category": "upper_body", "group": "jackets", "default_length": "short", "default_fit": "regular"},
    "leather_jacket":   {"name_ru": "Кожаная куртка",        "name_en": "leather jacket",             "category": "upper_body", "group": "jackets", "default_length": "short", "default_fit": "fitted"},
    "biker_jacket":     {"name_ru": "Косуха",                "name_en": "leather biker jacket",       "category": "upper_body", "group": "jackets", "default_length": "short", "default_fit": "fitted"},
    "puffer_jacket":    {"name_ru": "Пуховик короткий",      "name_en": "puffer jacket",              "category": "upper_body", "group": "jackets", "default_length": "short", "default_fit": "oversized"},
    "puffer_coat":      {"name_ru": "Пуховик длинный",       "name_en": "long puffer coat",           "category": "upper_body", "group": "jackets", "default_length": "long", "default_fit": "oversized"},
    "windbreaker":      {"name_ru": "Ветровка",              "name_en": "windbreaker jacket",         "category": "upper_body", "group": "jackets", "default_length": "short", "default_fit": "regular"},
    "utility_jacket":   {"name_ru": "Утилитарная куртка",    "name_en": "utility jacket",             "category": "upper_body", "group": "jackets", "default_length": "short", "default_fit": "regular"},
    "cropped_jacket":   {"name_ru": "Укороченная куртка",    "name_en": "cropped jacket",             "category": "upper_body", "group": "jackets", "default_length": "cropped", "default_fit": "regular"},
    "puffer_vest":      {"name_ru": "Жилет утеплённый",      "name_en": "puffer vest",                "category": "upper_body", "group": "jackets", "default_length": "short", "default_fit": "regular"},
    "rain_jacket":      {"name_ru": "Дождевик",              "name_en": "rain jacket",                "category": "upper_body", "group": "jackets", "default_length": "regular", "default_fit": "regular"},

    # --- ВЕРХНЯЯ ОДЕЖДА: Пальто ---
    # base_type используется когда длина != дефолта (убирает семантический якорь)
    "trench_coat":      {"name_ru": "Тренч",                 "name_en": "trench coat",                "base_type": "trench-style jacket",  "category": "upper_body", "group": "coats", "default_length": "long", "default_fit": "fitted"},
    "wool_coat":        {"name_ru": "Пальто классическое",   "name_en": "wool coat",                  "base_type": "tailored jacket",      "category": "upper_body", "group": "coats", "default_length": "long", "default_fit": "fitted"},
    "short_coat":       {"name_ru": "Полупальто",            "name_en": "short coat",                                                      "category": "upper_body", "group": "coats", "default_length": "regular", "default_fit": "regular"},
    "overcoat":         {"name_ru": "Пальто оверсайз",       "name_en": "oversized wool coat",        "base_type": "tailored jacket",      "category": "upper_body", "group": "coats", "default_length": "long", "default_fit": "oversized"},
    "maxi_coat":        {"name_ru": "Пальто макси",          "name_en": "maxi coat",                  "base_type": "tailored coat",        "category": "upper_body", "group": "coats", "default_length": "maxi", "default_fit": "regular"},
    "teddy_coat":       {"name_ru": "Тедди / шуба эко",      "name_en": "teddy coat",                 "base_type": "teddy jacket",         "category": "upper_body", "group": "coats", "default_length": "regular", "default_fit": "oversized"},
    "fur_coat":         {"name_ru": "Шуба",                  "name_en": "fur coat",                   "base_type": "fur jacket",           "category": "upper_body", "group": "coats", "default_length": "long", "default_fit": "oversized"},
    "short_fur":        {"name_ru": "Шуба короткая",         "name_en": "short fur coat",                                                  "category": "upper_body", "group": "coats", "default_length": "short", "default_fit": "oversized"},
    "shearling":        {"name_ru": "Дублёнка",              "name_en": "shearling coat",             "base_type": "shearling jacket",     "category": "upper_body", "group": "coats", "default_length": "regular", "default_fit": "regular"},
    "cape":             {"name_ru": "Кейп / пончо",          "name_en": "cape",                                                            "category": "upper_body", "group": "coats", "default_length": "regular", "default_fit": "oversized"},
    "parka":            {"name_ru": "Парка",                 "name_en": "parka",                      "base_type": "parka jacket",         "category": "upper_body", "group": "coats", "default_length": "regular", "default_fit": "regular"},

    # --- ПИДЖАКИ ---
    "blazer":           {"name_ru": "Пиджак",                "name_en": "blazer",                     "category": "upper_body", "group": "blazers", "default_length": "regular", "default_fit": "fitted"},
    "oversized_blazer": {"name_ru": "Пиджак оверсайз",      "name_en": "oversized blazer",           "category": "upper_body", "group": "blazers", "default_length": "regular", "default_fit": "oversized"},
    "cropped_blazer":   {"name_ru": "Пиджак укороченный",   "name_en": "cropped blazer",             "category": "upper_body", "group": "blazers", "default_length": "cropped", "default_fit": "fitted"},
    "longline_blazer":  {"name_ru": "Пиджак удлинённый",    "name_en": "longline blazer",            "category": "upper_body", "group": "blazers", "default_length": "long", "default_fit": "regular"},
    "tweed_jacket":     {"name_ru": "Жакет твидовый",        "name_en": "tweed jacket",               "category": "upper_body", "group": "blazers", "default_length": "short", "default_fit": "fitted"},
    "vest_formal":      {"name_ru": "Жилет костюмный",       "name_en": "formal vest",                "category": "upper_body", "group": "blazers", "default_length": "short", "default_fit": "fitted"},

    # --- ТОПЫ И ФУТБОЛКИ ---
    "tshirt":           {"name_ru": "Футболка",              "name_en": "t-shirt",                    "category": "upper_body", "group": "tops", "default_length": "regular", "default_fit": "regular"},
    "oversized_tshirt": {"name_ru": "Футболка оверсайз",    "name_en": "oversized t-shirt",          "category": "upper_body", "group": "tops", "default_length": "regular", "default_fit": "oversized"},
    "crop_top":         {"name_ru": "Кроп-топ",              "name_en": "crop top",                   "category": "upper_body", "group": "tops", "default_length": "cropped", "default_fit": "fitted"},
    "tank_top":         {"name_ru": "Майка",                 "name_en": "tank top",                   "category": "upper_body", "group": "tops", "default_length": "regular", "default_fit": "fitted"},
    "polo":             {"name_ru": "Поло",                  "name_en": "polo shirt",                 "category": "upper_body", "group": "tops", "default_length": "regular", "default_fit": "regular"},
    "bodysuit":         {"name_ru": "Боди",                  "name_en": "bodysuit",                   "category": "upper_body", "group": "tops", "default_length": "regular", "default_fit": "fitted"},
    "corset_top":       {"name_ru": "Корсет",                "name_en": "corset top",                 "category": "upper_body", "group": "tops", "default_length": "cropped", "default_fit": "fitted"},
    "tube_top":         {"name_ru": "Топ-бандо",             "name_en": "tube top",                   "category": "upper_body", "group": "tops", "default_length": "cropped", "default_fit": "fitted"},
    "camisole":         {"name_ru": "Топ на бретелях",       "name_en": "camisole top",               "category": "upper_body", "group": "tops", "default_length": "regular", "default_fit": "fitted"},

    # --- РУБАШКИ И БЛУЗЫ ---
    "shirt":            {"name_ru": "Рубашка",               "name_en": "button-down shirt",          "category": "upper_body", "group": "shirts", "default_length": "regular", "default_fit": "regular"},
    "oversized_shirt":  {"name_ru": "Рубашка оверсайз",     "name_en": "oversized shirt",            "category": "upper_body", "group": "shirts", "default_length": "long", "default_fit": "oversized"},
    "cropped_shirt":    {"name_ru": "Рубашка укороченная",  "name_en": "cropped button-down shirt",  "category": "upper_body", "group": "shirts", "default_length": "cropped", "default_fit": "regular"},
    "blouse":           {"name_ru": "Блуза",                 "name_en": "blouse",                     "category": "upper_body", "group": "shirts", "default_length": "regular", "default_fit": "relaxed"},

    # --- ТРИКОТАЖ ---
    "sweater":          {"name_ru": "Свитер",                "name_en": "sweater",                    "category": "upper_body", "group": "knitwear", "default_length": "regular", "default_fit": "regular"},
    "oversized_sweater":{"name_ru": "Свитер оверсайз",      "name_en": "oversized sweater",          "category": "upper_body", "group": "knitwear", "default_length": "long", "default_fit": "oversized"},
    "turtleneck":       {"name_ru": "Водолазка",             "name_en": "turtleneck sweater",         "category": "upper_body", "group": "knitwear", "default_length": "regular", "default_fit": "fitted"},
    "cardigan":         {"name_ru": "Кардиган",              "name_en": "cardigan",                   "category": "upper_body", "group": "knitwear", "default_length": "regular", "default_fit": "relaxed"},
    "long_cardigan":    {"name_ru": "Кардиган длинный",      "name_en": "long duster cardigan",       "category": "upper_body", "group": "knitwear", "default_length": "long", "default_fit": "relaxed"},
    "cropped_cardigan": {"name_ru": "Кардиган укороченный", "name_en": "cropped cardigan",           "category": "upper_body", "group": "knitwear", "default_length": "cropped", "default_fit": "relaxed"},
    "knit_vest":        {"name_ru": "Жилет вязаный",         "name_en": "knit vest",                  "category": "upper_body", "group": "knitwear", "default_length": "regular", "default_fit": "regular"},

    # --- СВИТШОТЫ И ХУДИ ---
    "sweatshirt":       {"name_ru": "Свитшот",               "name_en": "sweatshirt",                 "category": "upper_body", "group": "hoodies", "default_length": "regular", "default_fit": "relaxed"},
    "hoodie":           {"name_ru": "Худи",                  "name_en": "hoodie",                     "category": "upper_body", "group": "hoodies", "default_length": "regular", "default_fit": "relaxed"},
    "cropped_hoodie":   {"name_ru": "Худи укороченное",      "name_en": "cropped hoodie",             "category": "upper_body", "group": "hoodies", "default_length": "cropped", "default_fit": "relaxed"},
    "zip_hoodie":       {"name_ru": "Худи на молнии",        "name_en": "zip-up hoodie",              "category": "upper_body", "group": "hoodies", "default_length": "regular", "default_fit": "relaxed"},

    # --- БРЮКИ ---
    "trousers":         {"name_ru": "Брюки классические",    "name_en": "tailored trousers",          "category": "lower_body", "group": "pants", "default_length": "regular", "default_fit": "regular"},
    "wide_trousers":    {"name_ru": "Брюки широкие",         "name_en": "wide-leg trousers",          "category": "lower_body", "group": "pants", "default_length": "regular", "default_fit": "relaxed"},
    "slim_trousers":    {"name_ru": "Брюки зауженные",      "name_en": "slim tapered trousers",      "category": "lower_body", "group": "pants", "default_length": "regular", "default_fit": "fitted"},
    "cargo":            {"name_ru": "Карго",                 "name_en": "cargo pants",                "category": "lower_body", "group": "pants", "default_length": "regular", "default_fit": "relaxed"},
    "joggers":          {"name_ru": "Джоггеры",              "name_en": "jogger pants",               "category": "lower_body", "group": "pants", "default_length": "regular", "default_fit": "relaxed"},
    "culottes":         {"name_ru": "Кюлоты",                "name_en": "wide cropped trousers",      "category": "lower_body", "group": "pants", "default_length": "cropped", "default_fit": "relaxed"},
    "leggings":         {"name_ru": "Леггинсы",              "name_en": "leggings",                   "category": "lower_body", "group": "pants", "default_length": "regular", "default_fit": "fitted"},
    "palazzo":          {"name_ru": "Палаццо",               "name_en": "palazzo pants",              "category": "lower_body", "group": "pants", "default_length": "regular", "default_fit": "relaxed"},
    "sweatpants":       {"name_ru": "Спортивные штаны",      "name_en": "sweatpants",                 "category": "lower_body", "group": "pants", "default_length": "regular", "default_fit": "relaxed"},

    # --- ДЖИНСЫ ---
    "skinny_jeans":     {"name_ru": "Джинсы скинни",         "name_en": "skinny jeans",               "category": "lower_body", "group": "jeans", "default_length": "regular", "default_fit": "fitted"},
    "slim_jeans":       {"name_ru": "Джинсы слим",           "name_en": "slim jeans",                 "category": "lower_body", "group": "jeans", "default_length": "regular", "default_fit": "fitted"},
    "straight_jeans":   {"name_ru": "Джинсы прямые",         "name_en": "straight jeans",             "category": "lower_body", "group": "jeans", "default_length": "regular", "default_fit": "regular"},
    "wide_jeans":       {"name_ru": "Джинсы широкие",        "name_en": "wide-leg jeans",             "category": "lower_body", "group": "jeans", "default_length": "regular", "default_fit": "relaxed"},
    "flared_jeans":     {"name_ru": "Джинсы клёш",           "name_en": "flared jeans",               "category": "lower_body", "group": "jeans", "default_length": "regular", "default_fit": "regular"},
    "mom_jeans":        {"name_ru": "Мом джинсы",            "name_en": "mom jeans",                  "category": "lower_body", "group": "jeans", "default_length": "regular", "default_fit": "relaxed"},
    "boyfriend_jeans":  {"name_ru": "Бойфренды",             "name_en": "boyfriend jeans",            "category": "lower_body", "group": "jeans", "default_length": "regular", "default_fit": "relaxed"},
    "baggy_jeans":      {"name_ru": "Бэгги джинсы",          "name_en": "baggy jeans",                "category": "lower_body", "group": "jeans", "default_length": "regular", "default_fit": "oversized"},

    # --- ШОРТЫ ---
    "denim_shorts":     {"name_ru": "Шорты джинсовые",       "name_en": "denim shorts",               "category": "lower_body", "group": "shorts", "default_length": "short", "default_fit": "regular"},
    "chino_shorts":     {"name_ru": "Шорты классические",    "name_en": "chino shorts",               "category": "lower_body", "group": "shorts", "default_length": "short", "default_fit": "regular"},
    "bermuda":          {"name_ru": "Бермуды",               "name_en": "bermuda shorts",             "category": "lower_body", "group": "shorts", "default_length": "regular", "default_fit": "relaxed"},
    "sport_shorts":     {"name_ru": "Шорты спортивные",      "name_en": "athletic shorts",            "category": "lower_body", "group": "shorts", "default_length": "short", "default_fit": "relaxed"},
    "biker_shorts":     {"name_ru": "Велосипедки",           "name_en": "biker shorts",               "category": "lower_body", "group": "shorts", "default_length": "short", "default_fit": "fitted"},

    # --- ЮБКИ ---
    "mini_skirt":       {"name_ru": "Мини-юбка",             "name_en": "mini skirt",                 "category": "lower_body", "group": "skirts", "default_length": "short", "default_fit": "regular"},
    "midi_skirt":       {"name_ru": "Миди-юбка",             "name_en": "midi skirt",                 "category": "lower_body", "group": "skirts", "default_length": "regular", "default_fit": "regular"},
    "maxi_skirt":       {"name_ru": "Макси-юбка",            "name_en": "maxi skirt",                 "category": "lower_body", "group": "skirts", "default_length": "maxi", "default_fit": "regular"},
    "pencil_skirt":     {"name_ru": "Юбка-карандаш",         "name_en": "pencil skirt",               "category": "lower_body", "group": "skirts", "default_length": "regular", "default_fit": "fitted"},
    "pleated_skirt":    {"name_ru": "Юбка-плиссе",           "name_en": "pleated skirt",              "category": "lower_body", "group": "skirts", "default_length": "regular", "default_fit": "regular"},
    "aline_skirt":      {"name_ru": "Юбка А-силуэта",        "name_en": "A-line skirt",               "category": "lower_body", "group": "skirts", "default_length": "regular", "default_fit": "regular"},

    # --- ПЛАТЬЯ ---
    "mini_dress":       {"name_ru": "Мини-платье",           "name_en": "mini dress",                 "category": "dresses", "group": "dresses", "default_length": "short", "default_fit": "regular"},
    "midi_dress":       {"name_ru": "Миди-платье",           "name_en": "midi dress",                 "category": "dresses", "group": "dresses", "default_length": "regular", "default_fit": "regular"},
    "maxi_dress":       {"name_ru": "Макси-платье",          "name_en": "maxi dress",                 "category": "dresses", "group": "dresses", "default_length": "maxi", "default_fit": "regular"},
    "bodycon_dress":    {"name_ru": "Платье бодикон",        "name_en": "bodycon dress",              "category": "dresses", "group": "dresses", "default_length": "regular", "default_fit": "fitted"},
    "wrap_dress":       {"name_ru": "Платье с запахом",      "name_en": "wrap dress",                 "category": "dresses", "group": "dresses", "default_length": "regular", "default_fit": "fitted"},
    "shirt_dress":      {"name_ru": "Платье-рубашка",        "name_en": "shirt dress",                "category": "dresses", "group": "dresses", "default_length": "regular", "default_fit": "regular"},
    "slip_dress":       {"name_ru": "Платье-комбинация",     "name_en": "slip dress",                 "category": "dresses", "group": "dresses", "default_length": "regular", "default_fit": "fitted"},
    "blazer_dress":     {"name_ru": "Платье-пиджак",         "name_en": "blazer dress",               "category": "dresses", "group": "dresses", "default_length": "short", "default_fit": "fitted"},
    "sweater_dress":    {"name_ru": "Платье-свитер",         "name_en": "sweater dress",              "category": "dresses", "group": "dresses", "default_length": "regular", "default_fit": "regular"},
    "sundress":         {"name_ru": "Сарафан",               "name_en": "sundress",                   "category": "dresses", "group": "dresses", "default_length": "regular", "default_fit": "relaxed"},
    "aline_dress":      {"name_ru": "Платье А-силуэта",      "name_en": "A-line dress",               "category": "dresses", "group": "dresses", "default_length": "regular", "default_fit": "regular"},

    # --- КОМБИНЕЗОНЫ ---
    "jumpsuit":         {"name_ru": "Комбинезон",            "name_en": "jumpsuit",                   "category": "full_body", "group": "jumpsuits", "default_length": "regular", "default_fit": "regular"},
    "romper":           {"name_ru": "Комбинезон короткий",   "name_en": "romper",                     "category": "full_body", "group": "jumpsuits", "default_length": "short", "default_fit": "regular"},
    "overalls":         {"name_ru": "Комбинезон джинсовый", "name_en": "denim overalls",             "category": "full_body", "group": "jumpsuits", "default_length": "regular", "default_fit": "relaxed"},

    # --- СПОРТИВНЫЕ КОМПЛЕКТЫ ---
    "tracksuit":        {"name_ru": "Спортивный костюм",     "name_en": "tracksuit",                  "category": "full_body", "group": "sets", "default_length": "regular", "default_fit": "relaxed"},
    "coord_set":        {"name_ru": "Костюм-комплект",       "name_en": "matching coord set",         "category": "full_body", "group": "sets", "default_length": "regular", "default_fit": "regular"},
    "suit":             {"name_ru": "Деловой костюм",        "name_en": "formal suit",                "category": "full_body", "group": "sets", "default_length": "regular", "default_fit": "fitted"},
}

# ============================================================
# ДЛИНЫ И ПОСАДКИ (для кнопок переопределения)
# ============================================================

LENGTHS: dict[str, dict] = {
    "cropped":    {"label_ru": "Короткая (до талии)",      "name_ru": "короткая",     "name_en": "cropped waist-length"},
    "short":      {"label_ru": "Средняя (до бёдер)",        "name_ru": "средняя",      "name_en": "hip-length"},
    "regular":    {"label_ru": "Стандартная",               "name_ru": "стандартная",  "name_en": "regular length"},
    "long":       {"label_ru": "Длинная (до колен)",        "name_ru": "длинная",      "name_en": "knee-length"},
    "midi":       {"label_ru": "Миди (до середины икры)",   "name_ru": "миди",         "name_en": "midi-length"},
    "maxi":       {"label_ru": "Макси (в пол)",             "name_ru": "макси",        "name_en": "full-length maxi"},
}

FITS: dict[str, dict] = {
    "fitted":     {"label_ru": "Облегающая",  "name_ru": "облегающая",  "name_en": "fitted slim fit"},
    "regular":    {"label_ru": "Стандартная", "name_ru": "стандартная", "name_en": "regular fit"},
    "relaxed":    {"label_ru": "Свободная",   "name_ru": "свободная",   "name_en": "relaxed fit"},
    "oversized":  {"label_ru": "Оверсайз",    "name_ru": "оверсайз",    "name_en": "oversized"},
    "boxy":       {"label_ru": "Boxy",        "name_ru": "boxy",        "name_en": "boxy"},
}


# ============================================================
# ГРУППЫ ДЛЯ UI-КНОПОК
# ============================================================

GROUPS: dict[str, str] = {
    "jackets":   "🧥 Куртки",
    "coats":     "🧥 Пальто и шубы",
    "blazers":   "🤵 Пиджаки и жакеты",
    "tops":      "👕 Топы и футболки",
    "shirts":    "👔 Рубашки и блузы",
    "knitwear":  "🧶 Трикотаж",
    "hoodies":   "🏋️ Худи и свитшоты",
    "pants":     "👖 Брюки",
    "jeans":     "👖 Джинсы",
    "shorts":    "🩳 Шорты",
    "skirts":    "👗 Юбки",
    "dresses":   "👗 Платья",
    "jumpsuits": "🦺 Комбинезоны",
    "sets":      "👔 Костюмы и комплекты",
}


def get_types_by_group(group: str) -> list[tuple[str, str]]:
    """Получить все типы в группе: [(id, name_ru), ...]"""
    return [
        (tid, t["name_ru"])
        for tid, t in GARMENT_TYPES.items()
        if t["group"] == group
    ]


def get_type(type_id: str) -> dict | None:
    """Получить тип по ID."""
    return GARMENT_TYPES.get(type_id)


def build_ai_name(type_id: str) -> str:
    """Получить AI-friendly английское название для промта."""
    t = GARMENT_TYPES.get(type_id)
    if not t:
        return type_id
    return t["name_en"]


def build_smart_description(
    type_id: str,
    length_id: str | None = None,
    fit_id: str | None = None,
) -> tuple[str, str]:
    """Умное описание одежды. Возвращает (ru_desc, en_desc).

    Если длина != дефолта и у типа есть base_type — используем нейтральный термин.
    Пример: trench_coat + cropped = 'cropped trench-style jacket' (не 'cropped trench coat')
    """
    t = GARMENT_TYPES.get(type_id, {})
    type_ru = t.get("name_ru", type_id)
    type_en = t.get("name_en", type_id)
    base_type = t.get("base_type")
    default_length = t.get("default_length", "regular")
    default_fit = t.get("default_fit", "regular")

    # Проверяем: изменена ли длина относительно дефолта
    length_changed = length_id is not None and length_id != default_length
    fit_changed = fit_id is not None and fit_id != default_fit

    # Выбираем английский базовый термин
    if length_changed and base_type:
        # Используем base_type чтобы убрать семантический якорь
        en_base = base_type
    else:
        en_base = type_en

    # Собираем английское описание
    en_parts = []
    if length_id and length_id in LENGTHS:
        en_parts.append(LENGTHS[length_id]["name_en"])
    en_parts.append(en_base)
    if fit_id and fit_id in FITS:
        en_parts.append(FITS[fit_id]["name_en"])
    en_desc = " ".join(en_parts)

    # Русское описание
    ru_parts = []
    if length_id and length_id in LENGTHS:
        ru_parts.append(LENGTHS[length_id]["name_ru"])
    ru_parts.append(type_ru.lower())
    if fit_id and fit_id in FITS:
        ru_parts.append(FITS[fit_id]["name_ru"] + " посадки")
    ru_desc = " ".join(ru_parts)

    return ru_desc, en_desc
