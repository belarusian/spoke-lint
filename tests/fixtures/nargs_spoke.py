"""Spoke fixture: positional and dashed args exercising nargs variants."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Nargs spoke")
    parser.add_argument("inputs", nargs="+", help="one or more input paths")
    parser.add_argument("config", nargs="?", help="optional config path")
    parser.add_argument("--tags", nargs="*", help="zero or more tags")
    args = parser.parse_args()
    print(args.inputs, args.config, args.tags)


if __name__ == "__main__":
    main()
