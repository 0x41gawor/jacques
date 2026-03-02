import time

def exponential_backoff(attempt: int, base: int = 1, max_delay: int = 60):
    delay = min(base * (2 ** attempt), max_delay)
    time.sleep(delay)