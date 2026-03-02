import os
from dataclasses import dataclass

READWISE_BASE_URL = "https://readwise.io/api/v2/highlights/"
PROV_API_BASE_URL = "http://192.46.236.119:32317/api/v1/flashcards/generate"

@dataclass(frozen=True)
class Config:
    readwise_url: str
    readwise_token: str
    prov_api_url: str

def load_config() -> Config:
    from dotenv import load_dotenv
    load_dotenv()
    return Config(
        readwise_url=READWISE_BASE_URL,
        readwise_token=os.getenv("READWISE_TOKEN", ""),
        prov_api_url=PROV_API_BASE_URL
        )
