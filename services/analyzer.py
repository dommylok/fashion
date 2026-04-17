"""Garment analysis via Grok Vision (grok-4-1-fast-reasoning)."""
import base64
import logging

from pydantic import ValidationError
from xai_sdk.chat import user, system, image

from config import GROK_VISION_MODEL, VISION_INPUT_PRICE_PER_M, VISION_OUTPUT_PRICE_PER_M
from models.garment import GarmentAnalysis
from prompts.analysis import SYSTEM, USER
from services.xai_client import get_client

logger = logging.getLogger(__name__)

MAX_RETRIES = 2


def _to_data_uri(raw: bytes, mime: str = "image/jpeg") -> str:
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


def _calc_vision_cost(usage) -> float:
    try:
        input_cost = usage.prompt_tokens * VISION_INPUT_PRICE_PER_M / 1_000_000
        output_cost = usage.completion_tokens * VISION_OUTPUT_PRICE_PER_M / 1_000_000
        return input_cost + output_cost
    except Exception:
        return 0.0


async def analyze_garment(image_bytes: bytes) -> tuple[GarmentAnalysis, float]:
    """Отправить фото одежды в Grok Vision для структурного анализа.

    Retry при обрезанном JSON (ValidationError).
    Returns: (GarmentAnalysis, cost_usd)
    """
    total_cost = 0.0
    data_uri = _to_data_uri(image_bytes)

    for attempt in range(MAX_RETRIES + 1):
        client = get_client()
        chat = client.chat.create(model=GROK_VISION_MODEL, max_tokens=16384)
        chat.append(system(SYSTEM))
        chat.append(user(USER, image(data_uri)))

        logger.info("Analyzing garment via %s (attempt %d)...", GROK_VISION_MODEL, attempt + 1)

        try:
            response, parsed = await chat.parse(GarmentAnalysis)
        except (ValidationError, Exception) as e:
            logger.warning("Analysis attempt %d failed: %s", attempt + 1, e)
            if attempt < MAX_RETRIES:
                continue
            raise

        cost = _calc_vision_cost(response.usage)
        total_cost += cost
        usage = response.usage
        logger.info(
            "Analysis done: %d suggestions, %d styling, input=%d, output=%d, cost=$%.4f",
            len(parsed.suggestions), len(parsed.styling),
            usage.prompt_tokens, usage.completion_tokens, cost,
        )
        return parsed, total_cost

    raise RuntimeError("Analysis failed after retries")
