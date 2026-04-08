from dataclasses import dataclass


@dataclass(frozen=True)
class CardSale:
    """Sale data for a Weiss Schwarz card listing."""

    cid: str
    price: int
    stock: str
    rarity: str
    img_url: str

    def quantity_missing(self, quantity: int) -> int:
        if self.stock == "10+":
            return 0
        return max(quantity - int(self.stock), 0)

    def playset_price(self) -> int:
        return self.price * 4

    def playset_missing(self) -> int:
        return self.quantity_missing(4)


@dataclass(frozen=True)
class Report:
    """Collection of store listings keyed by card code."""

    cards: dict[str, CardSale]
    site: str

    def get_card(self, cid: str) -> CardSale:
        try:
            return self.cards[cid.lower()]
        except KeyError as exc:
            raise KeyError(f"Card id {cid} not found.") from exc

    def get_cards_by_rarity(self, *rarities: str) -> list[CardSale]:
        return [card for card in self.cards.values() if card.rarity in rarities]

    def get_list_price(
        self, card_list: list[tuple[str, int]]
    ) -> tuple[int, int, list[tuple[str, int]], list[str]]:
        errors: list[str] = []
        total_price = 0
        actual_price = 0
        missing_cards: list[tuple[str, int]] = []

        for cid, quantity in card_list:
            try:
                card = self.get_card(cid)
            except KeyError:
                errors.append(cid)
                continue

            missing_quantity = card.quantity_missing(quantity)
            total_price += quantity * card.price
            actual_price += quantity * card.price
            if missing_quantity:
                actual_price -= quantity * card.price
                missing_cards.append((cid, missing_quantity))

        return total_price, actual_price, missing_cards, errors

    def get_playset_price(self, *rarities: str) -> tuple[int, int, list[tuple[str, int]]]:
        total_price = 0
        actual_price = 0
        missing_cards: list[tuple[str, int]] = []

        for card in self.get_cards_by_rarity(*rarities):
            total_price += 4 * card.price
            missing_quantity = card.playset_missing()
            actual_price += (4 - missing_quantity) * card.price
            if missing_quantity:
                missing_cards.append((card.cid, missing_quantity))

        return total_price, actual_price, missing_cards
