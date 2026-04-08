from __future__ import annotations

import argparse
from pathlib import Path

from wstools.proxy.service import generate_proxy_card, generate_proxy_deck, generate_proxy_pdf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wstools",
        description="Weiss Schwarz scraping and proxy-generation tools.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    proxy_deck = subparsers.add_parser(
        "proxy-deck",
        help="Generate one proxy image per unique card in an EncoreDecks deck.",
    )
    proxy_deck.add_argument("deck_code", help="EncoreDecks deck code or URL suffix.")
    proxy_deck.add_argument(
        "--output-dir",
        default="generated/proxies",
        help="Directory to write generated proxies into.",
    )
    proxy_deck.set_defaults(handler=run_proxy_deck)

    proxy_card = subparsers.add_parser(
        "proxy-card",
        help="Generate one proxy image for a single EncoreDecks card code.",
    )
    proxy_card.add_argument("card_code", help="EncoreDecks card code, for example PAD/S105-001.")
    proxy_card.add_argument(
        "--output-file",
        default=None,
        help="Image file path to write. Defaults to generated/proxies/<card_code>.png.",
    )
    proxy_card.set_defaults(handler=run_proxy_card)

    proxy_pdf = subparsers.add_parser(
        "proxy-pdf",
        help="Generate a letter-size printable PDF with 5x2 proxy cards per page.",
    )
    proxy_pdf.add_argument("deck_code", help="EncoreDecks deck code or URL suffix.")
    proxy_pdf.add_argument(
        "--output-file",
        default=None,
        help="PDF file path to write. Defaults to generated/pdfs/<deck_code>.pdf.",
    )
    proxy_pdf.set_defaults(handler=run_proxy_pdf)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


def run_proxy_deck(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir)
    for output_path in generate_proxy_deck(args.deck_code, output_dir):
        print(f"Generated {output_path}")

    return 0


def run_proxy_card(args: argparse.Namespace) -> int:
    default_output = Path("generated") / "proxies" / f"{args.card_code.split('/')[-1]}.png"
    output_file = Path(args.output_file) if args.output_file else default_output

    generate_proxy_card(args.card_code, output_file)
    print(f"Generated {output_file}")
    return 0


def run_proxy_pdf(args: argparse.Namespace) -> int:
    default_output = Path("generated") / "pdfs" / f"{args.deck_code.split('/')[-1]}.pdf"
    output_file = Path(args.output_file) if args.output_file else default_output

    generate_proxy_pdf(args.deck_code, output_file)
    print(f"Generated {output_file}")
    return 0
