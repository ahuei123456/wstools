from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class Card:
    """Card metadata used across deck, price, and proxy workflows."""

    card_code: str
    attributes: tuple[str, ...]
    abilities: tuple[str, ...]
    card_type: str
    color: str
    image_path: str | None = None


@dataclass(frozen=True)
class Decklist:
    """Decklist plus helper methods for grouping and counting cards."""

    source: str
    cards: list[Card]

    def unique_cards(self) -> dict[str, Card]:
        return {card.card_code: card for card in self.cards}

    def card_counts(self) -> Counter[str]:
        return Counter(card.card_code for card in self.cards)
