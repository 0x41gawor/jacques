from __future__ import annotations
from dataclasses import dataclass
from typing import List, Any
import re


# ---------------------------
# Helpers
# ---------------------------

IPA_PATTERN = re.compile(r"^/.+/$")


# ---------------------------
# Core domain model
# ---------------------------

@dataclass(frozen=True)
class Front:
    word: str
    part: str
    ipa: str

    def __post_init__(self):
        if not self.word:
            raise ValueError("word cannot be empty")

        if not self.part:
            raise ValueError("part cannot be empty")

        if not IPA_PATTERN.match(self.ipa):
            raise ValueError("IPA must be wrapped in slashes, e.g. /ˈwɜːd/")


@dataclass(frozen=True)
class Example:
    sentence: str
    position: int

    def __post_init__(self):
        if self.position < 0:
            raise ValueError("position must be zero-based and non-negative")


@dataclass(frozen=True)
class Reverse:
    definition: str
    translation: List[str]
    example: Example
    synonyms: List[str]

    def __post_init__(self):
        if not self.definition:
            raise ValueError("definition cannot be empty")

        if not self.translation:
            raise ValueError("translation must contain at least one element")

        if not (2 <= len(self.synonyms) <= 4):
            raise ValueError("synonyms must contain 2–4 elements")


@dataclass(frozen=True)
class Flashcard:
    front: Front
    reverse: Reverse

    # -------- factory from dict --------
    @staticmethod
    def from_dict(data: dict[str, Any]) -> Flashcard:
        front = Front(**data["front"])

        example = Example(**data["reverse"]["example"])

        reverse = Reverse(
            definition=data["reverse"]["definition"],
            translation=data["reverse"]["translation"],
            example=example,
            synonyms=data["reverse"]["synonyms"],
        )

        return Flashcard(front=front, reverse=reverse)

    # -------- serialization --------
    def to_dict(self) -> dict[str, Any]:
        return {
            "front": {
                "word": self.front.word,
                "part": self.front.part,
                "ipa": self.front.ipa,
            },
            "reverse": {
                "definition": self.reverse.definition,
                "translation": self.reverse.translation,
                "example": {
                    "sentence": self.reverse.example.sentence,
                    "position": self.reverse.example.position,
                },
                "synonyms": self.reverse.synonyms,
            },
        }

# As for now Builder is not used, but it can be helpful if we want to have more complex construction logic in the future
# e.g. multiple sources of data e.g. IPA from CMUdcit, translations from WordNet, etc.
class FlashcardBuilder:
    def __init__(self, word: str):
        self.word = word
        self.part = None
        self.ipa = None
        self.definition = None
        self.translation = []
        self.example_sentence = None
        self.example_position = None
        self.synonyms = []

    def set_part(self, part: str):
        self.part = part

    def set_ipa(self, ipa: str):
        self.ipa = ipa

    def set_definition(self, definition: str):
        self.definition = definition

    def add_translation(self, translation: str):
        self.translation.append(translation)

    def set_example(self, sentence: str, position: int):
        self.example_sentence = sentence
        self.example_position = position

    def set_synonyms(self, synonyms: list[str]):
        self.synonyms = synonyms

    @classmethod
    def from_json(cls, data: dict) -> FlashcardBuilder:
        builder = cls(data["front"]["word"])

        builder.part = data["front"]["part"]
        builder.ipa = data["front"]["ipa"]

        builder.definition = data["reverse"]["definition"]
        builder.translation = data["reverse"]["translation"]

        sentence = data["reverse"]["example"]["sentence"]
        builder.example_sentence = sentence

        builder.example_position = data["reverse"]["example"]["position"] if "position" in data["reverse"]["example"] else None

        builder.synonyms = data["reverse"]["synonyms"]

        return builder

    def build(self) -> Flashcard:
        return Flashcard(
            front=Front(
                word=self.word,
                part=self.part,
                ipa=self.ipa,
            ),
            reverse=Reverse(
                definition=self.definition,
                translation=self.translation,
                example=Example(
                    sentence=self.example_sentence,
                    position=self.example_position,
                ),
                synonyms=self.synonyms,
            )
        )
