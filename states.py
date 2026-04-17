from aiogram.fsm.state import State, StatesGroup


class FashinFlow(StatesGroup):
    # Phase 1: Garment upload
    waiting_garments = State()

    # Phase 2: Type → length → fit → styling
    confirming_analysis = State()    # AI предложил тип
    choosing_length = State()        # Выбор длины (опционально)
    choosing_fit = State()           # Выбор посадки (опционально)
    choosing_style = State()         # Свой стиль текстом
    waiting_custom_prompt = State()  # Свой промт

    # Phase 3: Model selection
    browsing_models = State()

    # Phase 4: Background choice
    choosing_bg_type = State()
    choosing_bg_category = State()
    choosing_bg_photo = State()

    # Phase 5: Generation
    generating = State()

    # Phase 6: Post-result
    post_result = State()
    waiting_edit_text = State()
    waiting_new_prompt = State()  # Новый промт для той же одежды+модели+фона
