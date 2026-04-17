"""Grok Imagine API calls — try-on, placement, views, video."""
import asyncio
import logging
import time
from PIL import Image
import io

from config import GROK_IMAGINE, GROK_IMAGINE_PRO, GROK_VIDEO
from services.xai_client import get_client
from services.image_utils import (
    make_side_by_side, crop_right_half, to_data_uri, download,
)
from prompts.tryon import build_tryon_prompt
from prompts.background import PLACEMENT_PROMPT, build_inpainting_prompt
from prompts.views import build_back_side_prompt, build_poses_prompt
from prompts.video import build_video_prompt
from prompts.edit import build_edit_prompt

logger = logging.getLogger(__name__)


def _model_name(pro: bool) -> str:
    return GROK_IMAGINE_PRO if pro else GROK_IMAGINE


async def _imagine(prompt: str, image_uri: str = None,
                   image_uris: list[str] = None,
                   aspect: str = "3:2",
                   pro: bool = False, timeout: int = 300) -> tuple[bytes, dict]:
    """Core Grok Imagine call. Returns (image_bytes, usage_info).
    Supports single image_uri OR multiple image_uris."""
    model = _model_name(pro)
    client = get_client()
    t0 = time.time()
    logger.info("==> GROK START: model=%s, images=%d\n==> PROMPT:\n%s",
                model, len(image_uris) if image_uris else (1 if image_uri else 0), prompt)

    kwargs = {
        "prompt": prompt,
        "model": model,
        "aspect_ratio": aspect,
        "resolution": "2k",
        "image_format": "base64",
    }
    if image_uris:
        kwargs["image_urls"] = image_uris
    elif image_uri:
        kwargs["image_url"] = image_uri

    try:
        response = await asyncio.wait_for(
            client.image.sample(**kwargs),
            timeout=timeout,
        )
        elapsed = time.time() - t0
        # Extract usage info from response
        usage = {}
        try:
            u = response.usage
            usage = {
                "model": model,
                "prompt_tokens": u.prompt_tokens,
                "completion_tokens": u.completion_tokens,
                "total_tokens": u.total_tokens,
                "elapsed_s": round(elapsed, 1),
            }
        except Exception:
            usage = {"model": model, "elapsed_s": round(elapsed, 1)}
        logger.info("<== GROK DONE in %.1fs, usage=%s", elapsed, usage)
    except asyncio.TimeoutError:
        logger.error("<== GROK TIMEOUT after %.1fs", time.time() - t0)
        raise RuntimeError("Grok timeout — попробуйте через несколько минут")
    except Exception as e:
        logger.error("<== GROK FAILED in %.1fs: %r", time.time() - t0, e)
        raise

    try:
        img_bytes = response._decode_base64()
    except Exception:
        if hasattr(response, "url") and response.url:
            img_bytes = await download(response.url)
        else:
            raise
    return img_bytes, usage


# --- Public API ---
# All functions return (image_bytes, usage_dict)

async def tryon(garment_bytes: bytes, model_bytes: bytes,
                items_chosen: list[dict] | None = None,
                scene: str | None = None,
                outfit_style: str | None = None,
                photo_type: str = "hanger",
                custom_prompt: str | None = None,
                pro: bool = False) -> tuple[bytes, dict]:
    """Try-on using two separate images.
    photo_type: тип фото одежды для условной инструкции длины."""
    garment_uri = to_data_uri(garment_bytes)
    model_uri = to_data_uri(model_bytes)
    if custom_prompt:
        prompt = custom_prompt
    else:
        prompt = build_tryon_prompt(items_chosen or [],
                                    scene=scene, outfit_style=outfit_style,
                                    photo_type=photo_type)
    return await _imagine(prompt, image_uris=[garment_uri, model_uri],
                          aspect="3:4", pro=pro)


async def place_on_background(person_bytes: bytes, bg_bytes: bytes,
                              pro: bool = False) -> tuple[bytes, dict]:
    """Place dressed person onto a scene background."""
    composite = make_side_by_side(person_bytes, bg_bytes)
    return await _imagine(PLACEMENT_PROMPT, to_data_uri(composite),
                          aspect="3:4", pro=pro)


async def inpaint_background(person_bytes: bytes, location_desc: str,
                             deep_focus: bool = False,
                             pro: bool = False) -> tuple[bytes, dict]:
    """Replace background using text description."""
    prompt = build_inpainting_prompt(location_desc, deep_focus)
    uri = to_data_uri(person_bytes)
    return await _imagine(prompt, uri, aspect="3:4", pro=pro)


async def generate_back_side(reference_bytes: bytes,
                             garment_desc: str, pro: bool = False) -> tuple[bytes, dict]:
    """Generate 2-panel: over-shoulder + 3/4 back view.
    reference_bytes: the full-body result from first generation (ground truth)."""
    prompt = build_back_side_prompt(garment_desc)
    return await _imagine(prompt, to_data_uri(reference_bytes), aspect="3:2", pro=pro)


async def generate_poses(reference_bytes: bytes,
                         garment_desc: str, variant: int = 0,
                         pro: bool = False) -> tuple[bytes, dict]:
    """Generate 2-panel pose variations.
    reference_bytes: the full-body result from first generation (ground truth)."""
    prompt = build_poses_prompt(garment_desc, variant)
    return await _imagine(prompt, to_data_uri(reference_bytes), aspect="3:2", pro=pro)


async def edit_image(image_bytes: bytes, user_request: str,
                     garment_desc: str, pro: bool = False) -> tuple[bytes, dict]:
    """Edit existing result image based on user's text request."""
    prompt = build_edit_prompt(user_request, garment_desc)
    return await _imagine(prompt, to_data_uri(image_bytes), aspect="3:2", pro=pro)


async def generate_video(person_bytes: bytes, with_emotions: bool = True,
                         variant: int = 0) -> bytes:
    """Generate 5-sec rotation video from full-body image. Cost: $0.07 flat (720p)."""
    from config import VIDEO_DURATION
    img = Image.open(io.BytesIO(person_bytes)).convert("RGB")
    if img.height > 1280:
        ratio = 1280 / img.height
        img = img.resize((int(img.width * ratio), 1280), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    uri = to_data_uri(buf.getvalue())

    prompt = build_video_prompt(with_emotions, variant)
    client = get_client()
    t0 = time.time()
    logger.info("==> GROK VIDEO START: duration=%ds", VIDEO_DURATION)

    try:
        response = await client.video.generate(
            prompt=prompt,
            model=GROK_VIDEO,
            image_url=uri,
            duration=VIDEO_DURATION,
            resolution="720p",
            aspect_ratio="3:4",
        )
        logger.info("<== GROK VIDEO DONE in %.1fs", time.time() - t0)
    except Exception as e:
        logger.error("<== GROK VIDEO FAILED: %r", e)
        raise

    if hasattr(response, "url") and response.url:
        return await download(response.url, timeout_sec=300)
    raise RuntimeError("Grok video returned no URL")
