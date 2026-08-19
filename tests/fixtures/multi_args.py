"""Spoke fixture: multiple arguments to verify source-order preservation."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-arg spoke")
    parser.add_argument("--alpha", required=True)
    parser.add_argument("--beta", type=int, default=42)
    parser.add_argument("--gamma", default=None)
    args = parser.parse_args()
    print(args.alpha, args.beta, args.gamma)


if __name__ == "__main__":
    main()
