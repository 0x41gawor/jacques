from common.logging import logger

class Fetch:
    def __init__(self, readwise_service):
        self.readwise_service = readwise_service

    def run(self, date_from: str, date_to: str):
        result = self.readwise_service.fetch_words(date_from=date_from, date_to=date_to)
        logger.info(f"Fetched {len(result)} words from Readwise.")