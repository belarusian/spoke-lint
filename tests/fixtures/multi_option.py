"""Spoke fixture: an argument with both a short and a long option string."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-option spoke")
    parser.add_argument("-v", "--verbose", help="enable verbose logging")
    args = parser.parse_args()
    print(args.verbose)


if __name__ == "__main__":
    main()
