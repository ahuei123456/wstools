from pathlib import Path

import pytest

from wstools.errors import ProxyGenerationError
from wstools.models import Card, Decklist
from wstools.proxy import service


def test_generate_proxy_deck_writes_unique_cards(monkeypatch, tmp_path: Path) -> None:
    card = Card(
        card_code="PAD/S105-001",
        attributes=("Trait",),
        abilities=("Ability",),
        card_type="CH",
        color="blue",
        image_path="JP/S105/001.png",
    )
    decklist = Decklist(source="encoredecks", cards=[card, card])
    outputs: list[Path] = []

    monkeypatch.setattr("wstools.proxy.service.encore.fetch_decklist", lambda deck_code: decklist)
    monkeypatch.setattr(
        "wstools.proxy.service.generate_proxy",
        lambda card_obj, image_url, output_path: outputs.append(Path(output_path))
        or Path(output_path),
    )

    result = service.generate_proxy_deck("deck123", tmp_path)

    assert result == [tmp_path / "S105-001.png"]
    assert outputs == [tmp_path / "S105-001.png"]


def test_build_card_image_url_requires_image_path() -> None:
    card = Card(
        card_code="PAD/S105-001",
        attributes=(),
        abilities=(),
        card_type="CH",
        color="blue",
        image_path=None,
    )

    with pytest.raises(ProxyGenerationError):
        service.build_card_image_url(card)
