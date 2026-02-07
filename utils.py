import re

_WORD_RE = re.compile(r"^[a-z]+(-[a-z]+)*$")

def normalize_word(text: str) -> str | None:
    """
    Sprawdza, czy `text` jest pojedynczym słowem do nauki.

    Akceptuje:
    - wielką literę na początku
    - myślnik w środku (co-operate)
    - znaki końcowe (. , ; : ! ?)
    - whitespace na początku / końcu

    Zwraca:
    - znormalizowane słowo (lowercase)
    - None jeśli to nie jest słówko
    """

    if not text:
        return None

    # trim whitespace (ważne)
    raw = text.strip()

    # odrzucamy frazy (po trimie)
    if " " in raw:
        return None

    # usuwamy znaki poboczne z końców
    cleaned = raw.strip(".,;:!?\"'()[]{}")

    if not cleaned:
        return None

    normalized = cleaned.lower()

    # tylko litery + myślniki w środku
    if not _WORD_RE.match(normalized):
        return None

    return normalized