"""Spoke fixture: store-type actions (store_true and count)."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Store-action spoke")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--count", action="count")
    args = parser.parse_args()
    print(args.verbose, args.count)


if __name__ == "__main__":
    main()
