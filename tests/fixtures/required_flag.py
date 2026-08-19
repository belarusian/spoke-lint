"""Spoke fixture: a single required flag."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Required flag spoke")
    parser.add_argument("--topic", required=True)
    args = parser.parse_args()
    print(args.topic)


if __name__ == "__main__":
    main()
