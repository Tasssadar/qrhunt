import os
import tempfile
from importlib import resources

import segno
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas

from .animals import ANIMAL_QR_PREFIX, ANIMALS, Animal


def _generate_animal(animal: Animal, dest_dir: str) -> None:
    dest_path = os.path.join(dest_dir, f"{animal.name}.pdf")
    cv = canvas.Canvas(dest_path, pagesize=(210 * mm, 297 * mm))

    pawprint = resources.files(__package__) / "pawprints" / f"{animal.name.lower()}.png"
    if pawprint.is_file():
        cv.drawImage(
            str(pawprint), 10 * mm, 158 * mm, 190 * mm, 120 * mm, preserveAspectRatio=True
        )

    with tempfile.TemporaryDirectory() as tmp_dir:
        qr_path = os.path.join(tmp_dir, f"{animal.name}_qr.png")
        qr = segno.make_qr(f"{ANIMAL_QR_PREFIX}{animal.name}")
        qr.save(qr_path)
        cv.drawImage(qr_path, 10 * mm, 10 * mm, 190 * mm, 130 * mm, preserveAspectRatio=True)

    cv.showPage()
    cv.save()
    print(f"Generated {dest_path}")


def generate(dest_dir: str) -> None:
    os.makedirs(dest_dir, mode=0o755, exist_ok=True)
    for a in ANIMALS:
        _generate_animal(a, dest_dir)
