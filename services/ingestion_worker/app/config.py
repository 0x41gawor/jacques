import os
from dataclasses import dataclass

READWISE_BASE_URL = "https://readwise.io/api/v2/highlights/"
PROV_API_BASE_URL = "http://192.46.236.119:32317/api/v1/flashcards/generate"


@dataclass(frozen=True)
class Config:
    readwise_url: str
    prov_api_url: str
    poll_interval_seconds: int
    batch_size: int


def load_config() -> Config:
    from dotenv import load_dotenv
    load_dotenv()

    return Config(
        readwise_url=READWISE_BASE_URL,
        prov_api_url=PROV_API_BASE_URL,
        poll_interval_seconds=int(os.getenv("INGESTION_POLL_INTERVAL_SECONDS", "3600")),
        batch_size=int(os.getenv("INGESTION_BATCH_SIZE", "10")),
    )