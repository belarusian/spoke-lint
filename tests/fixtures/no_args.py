"""Spoke fixture: an ArgumentParser with zero add_argument calls."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="No-arg spoke")
    parser.parse_args()
    print("no args")


if __name__ == "__main__":
    main()
