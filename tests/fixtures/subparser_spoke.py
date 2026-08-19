"""Spoke fixture: a command-dispatch spoke with two subcommands."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Subparser spoke")
    subparsers = parser.add_subparsers(dest="command")

    train_parser = subparsers.add_parser("train", help="train a model")
    train_parser.add_argument("--epochs", type=int, default=10)

    eval_parser = subparsers.add_parser("eval", help="evaluate a model")
    eval_parser.add_argument("--metric", required=True)

    args = parser.parse_args()
    print(args.command)


if __name__ == "__main__":
    main()
