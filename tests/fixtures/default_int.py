"""Spoke fixture: an int-typed argument with a numeric default."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Default int spoke")
    parser.add_argument("--max-steps", type=int, default=150)
    args = parser.parse_args()
    print(args.max_steps)


if __name__ == "__main__":
    main()
