import os
import tempfile
from importlib import resources

import segno
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas

from .animals import ANIMAL_QR_PREFIX, ANIMALS, Animal

IMG_SUFFIXES = ["png", "jpg"]


def _generate_animal(
    cv: canvas.Canvas, animal: Animal, mutations: int, sil_mode: bool, paws_mode: bool
) -> None:
    for i in range(mutations):
        for suff in IMG_SUFFIXES:
            append = "_sil" if sil_mode else ""
            pawprint = (
                resources.files(__package__)
                / "pawprints"
                / f"{animal.name.lower()}{append}.{suff}"
            )
            if pawprint.is_file():
                cv.drawImage(
                    str(pawprint), 10 * mm, 158 * mm, 190 * mm, 120 * mm, preserveAspectRatio=True
                )

                if paws_mode:
                    cv.drawImage(
                        str(pawprint),
                        10 * mm,
                        10 * mm,
                        190 * mm,
                        120 * mm,
                        preserveAspectRatio=True,
                    )
                break

        if not paws_mode:
            with tempfile.TemporaryDirectory() as tmp_dir:
                qr_path = os.path.join(tmp_dir, f"{animal.name}_qr.png")
                qr = segno.make_qr(f"{ANIMAL_QR_PREFIX}{animal.name}:{i}")
                qr.save(qr_path)
                cv.drawImage(
                    qr_path, 10 * mm, 10 * mm, 190 * mm, 130 * mm, preserveAspectRatio=True
                )

        cv.showPage()
    print(f"Added {animal.name}")


def generate(dest_dir: str, mutations: int, sil_mode: bool, paws_mode: bool) -> None:
    os.makedirs(dest_dir, mode=0o755, exist_ok=True)

    file: str
    if paws_mode:
        file = "paws.pdf"
    elif sil_mode:
        file = "silhouettes.pdf"
    else:
        file = "paws_qr.pdf"

    dest_path = os.path.join(dest_dir, file)
    cv = canvas.Canvas(dest_path, pagesize=(210 * mm, 297 * mm))

    for a in ANIMALS:
        _generate_animal(cv, a, mutations, sil_mode, paws_mode)

    cv.save()
    print(f"Generated {dest_path}")
