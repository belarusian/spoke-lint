"""Spoke fixture: a single short flag (-v)."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Short-flag spoke")
    parser.add_argument("-v", help="verbose output")
    args = parser.parse_args()
    print(args.v)


if __name__ == "__main__":
    main()
