"""Spoke fixture: a multi-line add_argument call with trailing comma."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-line spoke")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="/tmp/out",
        required=False,
    )
    args = parser.parse_args()
    print(args.output_dir)


if __name__ == "__main__":
    main()
