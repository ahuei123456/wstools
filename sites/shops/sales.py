from dataclasses import dataclass

@dataclass
class CardSale:
    """Class for handling sale data for a WS card"""
    cid: str
    price: int
    stock: str
    rarity: str
    img_url: str

    def playset_price(self) -> int:
        return self.price * 4
    
    def playset_missing(self) -> int:
        return self.quantity_missing(4)

    def quantity_missing(self, qty: int) -> int:
        if self.stock == '10+':
            return 0
        return max(qty - int(self.stock), 0)

@dataclass
class Report:
    """Class for storing scraped data from an online store"""
    cards: dict[str, CardSale]
    site: str

    def get_card(self, cid: str) -> CardSale:
        if cid.lower() in self.cards:
            return self.cards[cid.lower()]
        
        raise KeyError(f'Card id {cid} not found.')

    def get_price(self, cid: str) -> int:
        return self.get_card(cid).price

    def get_cards_by_rarity(self, *rarities) -> list[CardSale]:
        cards = []
        for card in self.cards.values():
            if card.rarity in rarities:
                cards.append(card)
            
        return cards
    
    def get_list_price(self, card_list: list[tuple[str, int]]) -> tuple[int, int, list[str, int], list[str]]:
        errors = []

        total_price = 0
        actual_price = 0
        missing_cards = []
        for data in card_list:
            cid = data[0]
            qty = data[1]

            try:
                card = self.get_card(cid)
                missing_qty = card.quantity_missing(qty)
                total_price += qty * card.price
                actual_price += qty * card.price
                if missing_qty != 0:
                    actual_price -= qty * card.price
                    missing_cards.append((cid, missing_qty))
            except:
                errors.append(cid)
        
        return total_price, actual_price, missing_cards, errors

    def get_playset_price(self, *rarities) -> tuple[int, int, list[tuple[str, int]]]:
        total_price = 0
        actual_price = 0
        missing_cards = []
        for card in self.get_cards_by_rarity(*rarities):
            total_price += 4 * card.price
            missing_qty = card.playset_missing()
            actual_price += (4 - missing_qty) * card.price
            if missing_qty > 0:
                missing_cards.append((card.cid, missing_qty))
        
        return total_price, actual_price, missing_cards