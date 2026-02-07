import os
import argparse
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

from utils import normalize_word
from db import get_db_connection

load_dotenv()

TOKEN = os.getenv("READWISE_TOKEN")
if not TOKEN:
    raise RuntimeError("Brak READWISE_TOKEN w .env")

BASE_URL = "https://readwise.io/api/v2/highlights/"
HEADERS = {
    "Authorization": f"Token {TOKEN}",
}

# --------------------------------------------------
# Date normalization
# --------------------------------------------------
def read_date(value: str) -> str:
    if not value:
        raise ValueError("Pusta data")

    try:
        if len(value) == 10:
            dt = datetime.strptime(value, "%Y-%m-%d")
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            value = value.replace("Z", "")
            dt = datetime.fromisoformat(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        raise ValueError(f"Niepoprawny format daty: {value}")

# --------------------------------------------------
# CLI
# --------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Readwise → Postgres words ingest"
    )
    parser.add_argument("--from", dest="date_from", help="updated__gt")
    parser.add_argument("--to", dest="date_to", help="updated__lt")
    return parser.parse_args()

# --------------------------------------------------
# Fetch + Insert
# --------------------------------------------------
def fetch_and_insert(date_from, date_to, page_size=1000):
    page = 1

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            while True:
                params = {
                    "page": page,
                    "pageSize": page_size,
                    "updated__gt": date_from,
                    "updated__lt": date_to,
                }

                r = requests.get(
                    BASE_URL,
                    headers=HEADERS,
                    params=params,
                    timeout=30,
                )
                r.raise_for_status()

                data = r.json()
                results = data.get("results", [])

                if not results:
                    break

                for h in results:
                    raw_text = h.get("text")
                    word = normalize_word(raw_text)

                    if not word:
                        continue

                    cur.execute(
                        """
                        INSERT INTO words (word)
                        VALUES (%s)
                        ON CONFLICT DO NOTHING
                        """,
                        (word,),
                    )

                conn.commit()

                if not data.get("next"):
                    break

                page += 1

# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":
    args = parse_args()

    now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = now - timedelta(days=1)

    raw_from = args.date_from or yesterday.strftime("%Y-%m-%d")
    raw_to = args.date_to or now.strftime("%Y-%m-%d")

    date_from = read_date(raw_from)
    date_to = read_date(raw_to)

    fetch_and_insert(date_from, date_to)
