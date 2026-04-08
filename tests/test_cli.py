from argparse import Namespace
from pathlib import Path

from wstools.cli import run_proxy_card, run_proxy_deck, run_proxy_pdf


def test_run_proxy_deck_uses_unique_cards(monkeypatch, tmp_path: Path) -> None:
    generated_files = [tmp_path / "S105-001.png"]
    monkeypatch.setattr(
        "wstools.cli.generate_proxy_deck",
        lambda deck_code, output_dir: generated_files,
    )

    result = run_proxy_deck(Namespace(deck_code="deck123", output_dir=str(tmp_path)))

    assert result == 0
    assert generated_files == [tmp_path / "S105-001.png"]


def test_run_proxy_pdf_uses_full_deck(monkeypatch, tmp_path: Path) -> None:
    output_files: list[Path] = []
    monkeypatch.setattr(
        "wstools.cli.generate_proxy_pdf",
        lambda deck_code, output_file: output_files.append(Path(output_file)),
    )

    result = run_proxy_pdf(Namespace(deck_code="deck123", output_file=str(tmp_path / "deck.pdf")))

    assert result == 0
    assert output_files == [tmp_path / "deck.pdf"]


def test_run_proxy_card_uses_encore_card_lookup(monkeypatch, tmp_path: Path) -> None:
    generated_files: list[Path] = []

    monkeypatch.setattr(
        "wstools.cli.generate_proxy_card",
        lambda card_code, output_path: generated_files.append(Path(output_path)),
    )

    result = run_proxy_card(
        Namespace(card_code="PAD/S105-001", output_file=str(tmp_path / "card.png"))
    )

    assert result == 0
    assert generated_files == [tmp_path / "card.png"]
