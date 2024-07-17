import argparse

from . import generate
from .app import HuntApp


def main() -> None:
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--generate", action="store_true", help="Generate QR codes for the animals"
    )
    parser.add_argument(
        "--generate-dest",
        default="./generated",
        help="Destination directory for the generated QR codes",
    )
    parser.add_argument(
        "--mutations",
        default=3,
        help="Amount of unique QR codes for each animal",
    )
    parser.add_argument(
        "--sil",
        action="store_true",
        help="Use siluette instead of pawprints",
    )
    parser.add_argument(
        "--paws",
        action="store_true",
        help="Generate only paws",
    )

    args = parser.parse_args()

    if args.generate:
        generate.generate(args.generate_dest, args.mutations, args.sil, args.paws)
        return

    app = HuntApp()
    app.run()


if __name__ == "__main__":
    main()
