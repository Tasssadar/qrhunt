import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Animal:
    name: str
    points: int


ANIMAL_QR_PREFIX = "ZV:"
ANIMAL_RE = re.compile(rf"{ANIMAL_QR_PREFIX}(\w+)")

ANIMALS = (Animal("Srnec", 10), Animal("Clovek", -10))

ANIMALS_BY_NAME = {animal.name: animal for animal in ANIMALS}
