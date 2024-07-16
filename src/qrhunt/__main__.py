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

    args = parser.parse_args()

    if args.generate:
        generate.generate(args.generate_dest)
        return

    app = HuntApp()
    app.run()


if __name__ == "__main__":
    main()
