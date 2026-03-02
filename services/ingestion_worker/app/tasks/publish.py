from common.logging import logger

class Publish:
    def __init__(self, publisher):
        self.publisher = publisher

    def run(self, words):
        self.publisher.publish(words)
        logger.info(f"Published {len(words)} words to the message queue.")