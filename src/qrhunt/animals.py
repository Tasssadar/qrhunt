import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Animal:
    name: str
    points: int


ANIMAL_QR_PREFIX = "ZV:"
ANIMAL_RE = re.compile(rf"{ANIMAL_QR_PREFIX}(\w+)(?::([0-9]+))?")

ANIMALS = (
    Animal("Jelen", 80),
    Animal("Prase", 60),
    Animal("Srnec", 40),
    Animal("Zajic", 20),
    Animal("Veverka", -20),
    Animal("Kun", -50),
    Animal("Pes", -50),
    Animal("Clovek", -100),
)

ANIMALS_BY_NAME = {animal.name: animal for animal in ANIMALS}
