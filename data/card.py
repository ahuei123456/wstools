from dataclasses import dataclass

@dataclass
class Card:
    """Class containing card data"""
    card_code: str
    attributes: list[str]
    abilities: list[str]
    card_type: str
    color: str

@dataclass
class Decklist:
    """Class for handling data for a WS decklist"""
    source: str
    cards: list[Card]

    def get_unique_cards(self):
        return {card.card_code: card for card in self.cards}
    
    def get_card_count(self):
        count = {}
        for card in self.cards:
            count.setdefault(card.card_code, [card, 0])[1] += 1
        
        return count
        