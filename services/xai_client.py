"""Shared xAI SDK client singleton."""
from xai_sdk.aio.client import Client as AsyncClient
from config import XAI_API_KEY

_client: AsyncClient | None = None


def get_client() -> AsyncClient:
    global _client
    if _client is None:
        _client = AsyncClient(api_key=XAI_API_KEY)
    return _client
