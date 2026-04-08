from wstools.models import Card, Decklist


def test_card_counts_groups_duplicates() -> None:
    card = Card(
        card_code="PAD/S105-001",
        attributes=("Trait",),
        abilities=("Ability",),
        card_type="CH",
        color="blue",
    )
    deck = Decklist(source="test", cards=[card, card, card])

    assert deck.card_counts() == {"PAD/S105-001": 3}
    assert deck.unique_cards() == {"PAD/S105-001": card}
