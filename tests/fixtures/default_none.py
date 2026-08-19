"""Spoke fixture: an argument whose default is explicitly None."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Default None spoke")
    parser.add_argument("--briefing", default=None)
    args = parser.parse_args()
    print(args.briefing)


if __name__ == "__main__":
    main()
