"""Random model photo picker from the model library."""
import logging
import random
from pathlib import Path

from config import MODELS_DIR

logger = logging.getLogger(__name__)

_all_models: list[Path] | None = None


def _load_models() -> list[Path]:
    """Scan MODELS_DIR for JPG files (lazy, cached)."""
    global _all_models
    if _all_models is None:
        _all_models = sorted(MODELS_DIR.glob("*.jpg"))
        logger.info("Loaded %d model photos from %s", len(_all_models), MODELS_DIR)
    return _all_models


def pick_random_models(count: int = 10, exclude: set[str] | None = None) -> list[Path]:
    """Pick `count` random model photos, excluding already-shown ones.

    Returns a list of Path objects to model JPG files.
    """
    all_models = _load_models()
    if exclude:
        available = [m for m in all_models if m.name not in exclude]
    else:
        available = list(all_models)

    if len(available) <= count:
        return available

    return random.sample(available, count)


def get_model_by_name(filename: str) -> Path | None:
    """Get a specific model photo by filename."""
    path = MODELS_DIR / filename
    return path if path.exists() else None
