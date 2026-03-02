import requests

from app.protocols import ExternalSourceService

from .utils import normalize_word


class ReadwiseService(ExternalSourceService):

    def __init__(self, readwise_url: str, token: str):
        self.readwise_url = readwise_url
        self.token = token

    def fetch_words(self, date_from: str, date_to: str) -> list[str]:
        page = 1

        headers = {"Authorization": f"Token {self.token}"}

        result = []

        while True:
            params = {
                "page": page,
                "page_size": 1000,
                "date_from": date_from,
                "date_to": date_to
            }
            
            r = requests.get(
                url=self.readwise_url,
                headers=headers,
                params=params,
                timeout=30
            )
            r.raise_for_status()
            data = r.json()

            results = data.get("results", [])
            if not results:
                break

            for h in results:
                raw_text = h['text']
                word = normalize_word(raw_text)


                if not word:
                    continue

                result.append(word)
            
            if not data['next']:
                break

            page += 1

        return result

if __name__ == "__main__":
    import app.config as config
    cfg = config.load_config()
    print(cfg)
    service = ReadwiseService(readwise_url=cfg.readwise_url, token=cfg.readwise_token)

    words = service.fetch_words(date_from="2026-01-01T00:00", date_to="2026-03-02T00:00")
    print(words)
