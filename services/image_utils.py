"""Image processing utilities. Core functions copied from fashionbot."""
import base64
import io
import logging

import aiohttp
from PIL import Image

logger = logging.getLogger(__name__)

# --- Background removal (rembg, local) ---

_rembg_session = None


def _get_rembg_session():
    global _rembg_session
    if _rembg_session is None:
        from rembg import new_session
        _rembg_session = new_session("birefnet-general")
        logger.info("rembg session initialized (birefnet-general)")
    return _rembg_session


def remove_bg_local(image_bytes: bytes) -> bytes:
    """Remove background locally via rembg. Returns PNG with transparency."""
    from rembg import remove
    session = _get_rembg_session()
    return remove(image_bytes, session=session)


# --- Image compositing ---

def composite_on_white(png_bytes: bytes) -> Image.Image:
    """Overlay PNG with alpha on white background."""
    img = Image.open(io.BytesIO(png_bytes))
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    white_bg = Image.new("RGB", img.size, (255, 255, 255))
    white_bg.paste(img, mask=img.split()[3])
    return white_bg


def crop_to_content(img: Image.Image, padding: int = 50) -> Image.Image:
    """Crop image to content bounding box, removing excess white."""
    if img.mode == "RGBA":
        bbox = img.split()[3].getbbox()
    else:
        from PIL import ImageChops
        bg = Image.new("RGB", img.size, (255, 255, 255))
        diff = ImageChops.difference(img, bg)
        bbox = diff.getbbox()
    if not bbox:
        return img
    left = max(0, bbox[0] - padding)
    top = max(0, bbox[1] - padding)
    right = min(img.width, bbox[2] + padding)
    bottom = min(img.height, bbox[3] + padding)
    return img.crop((left, top, right, bottom))


def preprocess_garment(png_bytes: bytes) -> bytes:
    """Full garment preprocessing: bg removal result → clean JPEG on white.

    Crops to content, composites on white, preserves natural proportions.
    Returns JPEG bytes.
    """
    img = Image.open(io.BytesIO(png_bytes))
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    # Crop to content
    bbox = img.split()[3].getbbox()
    if bbox:
        padding = 40
        left = max(0, bbox[0] - padding)
        top = max(0, bbox[1] - padding)
        right = min(img.width, bbox[2] + padding)
        bottom = min(img.height, bbox[3] + padding)
        img = img.crop((left, top, right, bottom))

    # Composite on white
    white_bg = Image.new("RGB", img.size, (255, 255, 255))
    white_bg.paste(img, mask=img.split()[3])
    img_rgb = white_bg

    # Resize to max 2000px per side
    w, h = img_rgb.size
    max_side = 2000
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        img_rgb = img_rgb.resize(
            (int(w * scale), int(h * scale)), Image.Resampling.LANCZOS
        )

    out = io.BytesIO()
    img_rgb.save(out, format="JPEG", quality=95, optimize=True)
    return out.getvalue()


def crop_garment_length(image_bytes: bytes, target_length: str) -> bytes:
    """Физически обрезать фото одежды по длине.
    Grok игнорирует текстовые инструкции о длине — единственный способ
    контролировать длину это обрезать фото до нужного уровня.

    target_length: 'укороченная' -> 55%, 'стандартная' -> 75%, и т.д.
    """
    # Маппинг длины → процент от высоты одежды который оставляем
    length_crop = {
        "укороченная": 0.55,
        "cropped": 0.55,
        "стандартная": 0.75,
        "regular": 0.75,
        # удлинённая и длиннее — не обрезаем
    }

    ratio = length_crop.get(target_length)
    if not ratio:
        return image_bytes  # не обрезаем для длинных вещей

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Находим контент (не белый фон)
    from PIL import ImageChops
    bg = Image.new("RGB", img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()

    if not bbox:
        return image_bytes

    content_top = bbox[1]
    content_bottom = bbox[3]
    content_height = content_bottom - content_top

    # Обрезаем контент до нужного процента
    new_bottom = content_top + int(content_height * ratio)
    new_bottom = min(new_bottom, img.height)

    # Обрезаем картинку
    cropped = img.crop((0, 0, img.width, new_bottom + 40))  # +40 padding

    # Добавляем белый фон снизу чтобы был чистый край
    canvas = Image.new("RGB", (cropped.width, cropped.height + 20), (255, 255, 255))
    canvas.paste(cropped, (0, 0))

    out = io.BytesIO()
    canvas.save(out, format="JPEG", quality=95)
    logger.info("Cropped garment: %s -> %d%% height (%dx%d -> %dx%d)",
                target_length, int(ratio * 100),
                img.width, img.height, canvas.width, canvas.height)
    return out.getvalue()


# --- Side-by-side compositing ---

def make_side_by_side(left_bytes: bytes, right_bytes: bytes,
                      target_height: int = 1536) -> bytes:
    """Combine two images into a side-by-side composite (LEFT | RIGHT).
    Both rescaled to target_height with white separator."""
    left = Image.open(io.BytesIO(left_bytes)).convert("RGB")
    right = Image.open(io.BytesIO(right_bytes)).convert("RGB")

    def fit(img, h):
        ratio = h / img.height
        return img.resize((int(img.width * ratio), h), Image.Resampling.LANCZOS)

    left = fit(left, target_height)
    right = fit(right, target_height)
    sep = 20
    canvas = Image.new("RGB", (left.width + sep + right.width, target_height),
                        (255, 255, 255))
    canvas.paste(left, (0, 0))
    canvas.paste(right, (left.width + sep, 0))

    out = io.BytesIO()
    canvas.save(out, format="JPEG", quality=92)
    return out.getvalue()


def stack_images_vertical(images_bytes: list[bytes], target_width: int = 768) -> bytes:
    """Склеить несколько изображений вертикально (одно под другим).
    Для случая когда несколько вещей нужно показать в одной картинке."""
    imgs = [Image.open(io.BytesIO(b)).convert("RGB") for b in images_bytes]

    # Resize all to same width
    resized = []
    for img in imgs:
        ratio = target_width / img.width
        resized.append(img.resize(
            (target_width, int(img.height * ratio)), Image.Resampling.LANCZOS
        ))

    total_height = sum(img.height for img in resized)
    gap = 10
    total_height += gap * (len(resized) - 1)

    canvas = Image.new("RGB", (target_width, total_height), (255, 255, 255))
    y = 0
    for img in resized:
        canvas.paste(img, (0, y))
        y += img.height + gap

    out = io.BytesIO()
    canvas.save(out, format="JPEG", quality=95)
    return out.getvalue()


def crop_closeup(raw: bytes) -> bytes:
    """Вырезать крупный план (верхние 55% изображения) из full-body фото.
    Гарантирует что крупный план и полный рост — одна и та же картинка."""
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    # Берём верхние 55% — грудь + лицо
    crop_h = int(img.height * 0.55)
    closeup = img.crop((0, 0, img.width, crop_h))
    out = io.BytesIO()
    closeup.save(out, format="JPEG", quality=95)
    return out.getvalue()


def make_two_panel(fullbody_bytes: bytes) -> bytes:
    """Создать 2-панельное изображение из full-body: крупный план + полный рост.
    Оба из одного фото — гарантированная консистентность."""
    img = Image.open(io.BytesIO(fullbody_bytes)).convert("RGB")

    # Крупный план — верхние 55%
    crop_h = int(img.height * 0.55)
    closeup = img.crop((0, 0, img.width, crop_h))

    # Resize closeup до той же высоты что fullbody
    closeup_resized = closeup.resize(
        (int(closeup.width * img.height / closeup.height), img.height),
        Image.Resampling.LANCZOS,
    )

    sep = 20
    canvas = Image.new("RGB", (closeup_resized.width + sep + img.width, img.height),
                        (255, 255, 255))
    canvas.paste(closeup_resized, (0, 0))
    canvas.paste(img, (closeup_resized.width + sep, 0))

    out = io.BytesIO()
    canvas.save(out, format="JPEG", quality=92)
    return out.getvalue()


def crop_right_half(raw: bytes) -> bytes:
    """Extract the right half from a 2-panel result (the full-body panel).
    If the image isn't wide enough to be 2-panel, returns as-is."""
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    aspect = img.width / max(img.height, 1)
    if aspect >= 1.3:
        left = img.width // 2
        img = img.crop((left, 0, img.width, img.height))
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=95)
    return out.getvalue()


def split_two_panels(raw: bytes) -> tuple[bytes, bytes]:
    """Split a 2-panel image into left and right halves."""
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    mid = img.width // 2
    gap = 10  # skip separator

    left_img = img.crop((0, 0, mid - gap, img.height))
    right_img = img.crop((mid + gap, 0, img.width, img.height))

    def to_bytes(i):
        buf = io.BytesIO()
        i.save(buf, format="JPEG", quality=95)
        return buf.getvalue()

    return to_bytes(left_img), to_bytes(right_img)


# --- Download / data URI helpers ---

async def download(url: str, timeout_sec: int = 60) -> bytes:
    """Download file from URL."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url, timeout=aiohttp.ClientTimeout(total=timeout_sec)
        ) as resp:
            resp.raise_for_status()
            return await resp.read()


def compress_for_grok(raw: bytes, max_bytes: int = 2_800_000) -> bytes:
    """Сжать изображение чтобы влезло в лимит gRPC 4MB (с учётом base64 +33%).
    Grok Imagine не принимает больше 4MB в payload."""
    if len(raw) <= max_bytes:
        return raw
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    # Уменьшить до 1536px по длинной стороне
    max_dim = 1536
    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)),
                         Image.Resampling.LANCZOS)
    # Подбор quality
    for q in [85, 75, 65, 55]:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=q, optimize=True)
        if buf.tell() <= max_bytes:
            logger.info("Compressed image: %dKB -> %dKB (q=%d)",
                        len(raw) // 1024, buf.tell() // 1024, q)
            return buf.getvalue()
    return buf.getvalue()


def to_data_uri(raw: bytes, mime: str = "image/jpeg") -> str:
    raw = compress_for_grok(raw)
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"
