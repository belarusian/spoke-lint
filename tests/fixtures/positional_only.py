"""Spoke fixture: a single positional argument (no leading dash)."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Positional-only spoke")
    parser.add_argument("topic")
    args = parser.parse_args()
    print(args.topic)


if __name__ == "__main__":
    main()
