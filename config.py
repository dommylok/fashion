from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Paths to assets
PROJECT_ROOT = Path(__file__).parent
FASHIN_ROOT = PROJECT_ROOT.parent

LOCATIONS_DIR = FASHIN_ROOT / "fashionbot" / "assets" / "locations"
MODELS_DIR = FASHIN_ROOT / "model_sorter" / "input" / "image"

# Grok model names and pricing
GROK_VISION_MODEL = "grok-4-1-fast-reasoning"
GROK_IMAGINE = "grok-imagine-image"
GROK_IMAGINE_PRO = "grok-imagine-image-pro"
GROK_VIDEO = "grok-imagine-video"

# Pricing
PRICE_IMAGINE = 0.02          # per image
PRICE_IMAGINE_PRO = 0.07      # per image
PRICE_VIDEO_720P = 0.07       # per video (flat, any duration)
PRICE_VIDEO_480P = 0.05       # per video (flat)
VIDEO_DURATION = 5            # always 5 seconds

# Vision model token pricing (per 1M tokens)
VISION_INPUT_PRICE_PER_M = 0.20   # $0.20 per 1M input tokens
VISION_OUTPUT_PRICE_PER_M = 0.50  # $0.50 per 1M output tokens

USD_TO_RUB = 93

