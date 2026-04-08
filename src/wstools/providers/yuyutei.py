from __future__ import annotations

import requests
from bs4 import BeautifulSoup, PageElement, Tag

from wstools.providers.sales import CardSale

YYT_URL = "https://yuyu-tei.jp/game_ws/sell/sell_price.php"
REQUEST_TIMEOUT_SECONDS = 15


class YuyuteiCard(CardSale):
    """Yuyutei sale listing."""


def fetch_sets() -> dict[str, str]:
    response = requests.get(YYT_URL, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    content = BeautifulSoup(response.content, "html.parser")

    set_list = content.find("ul", attrs={"data-ui": "expand"})
    if set_list is None:
        raise ValueError("Could not find Yuyutei set list.")

    set_labels = set_list.find_all("input", attrs={"type": "checkbox"})
    result: dict[str, str] = {}
    for set_label in set_labels:
        value = set_label.get("value")
        parent = set_label.parent
        if isinstance(value, str) and isinstance(parent, Tag):
            result[value] = parent.get_text(strip=True)
    return result


def fetch_card_sales(version: str) -> dict[str, YuyuteiCard]:
    content = _fetch_version_page(version)
    card_data = content.find(class_="card_list_box")
    if card_data is None:
        raise ValueError(f"Could not find Yuyutei card list for {version}.")

    cards: dict[str, YuyuteiCard] = {}
    rarities = [node for node in card_data.contents if isinstance(node, Tag)]

    for rarity in rarities:
        card_list = _get_card_list(rarity)
        if card_list is None:
            continue

        rarity_text = _get_rarity_text(rarity)
        if rarity_text is None:
            continue

        card_units = card_list.find_all(class_=f"card_unit {rarity_text}")
        rarity_official = rarity_text.split("_")[-1]
        for card_unit in card_units:
            card_id = _find_text(card_unit, "id")
            price_text = _find_text(card_unit, "price")
            stock_text = _find_text(card_unit, "stock")
            img_url = _find_image_url(card_unit)
            if card_id is None or price_text is None or stock_text is None or img_url is None:
                continue

            price = int(price_text.strip().split()[-1][:-1])
            stock = stock_text[2:]
            if stock == "×":
                stock = "0"
            elif stock == "◯":
                stock = "10+"

            normalized_card_id = card_id.upper()
            cards[normalized_card_id] = YuyuteiCard(
                normalized_card_id,
                price,
                stock,
                rarity_official,
                img_url,
            )

    return cards


def fetch_card_codes(version: str) -> set[str]:
    content = _fetch_version_page(version)
    card_data = content.find(class_="card_list_box")
    if card_data is None:
        raise ValueError(f"Could not find Yuyutei card list for {version}.")

    codes: set[str] = set()
    rarities = [node for node in card_data.contents if isinstance(node, Tag)]
    for rarity in rarities:
        card_list = _get_card_list(rarity)
        if card_list is None:
            continue

        rarity_text = _get_rarity_text(rarity)
        if rarity_text is None:
            continue

        card_units = card_list.find_all(class_=f"card_unit {rarity_text}")
        for card_unit in card_units:
            card_id = _find_text(card_unit, "id")
            if card_id is None:
                continue
            codes.add(card_id.split("/")[0])

    return codes


def _fetch_version_page(version: str) -> BeautifulSoup:
    response = requests.get(
        YYT_URL,
        params={"ver": version},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def _get_card_list(rarity: Tag) -> Tag | None:
    if len(rarity.contents) <= 3:
        return None

    card_list = rarity.contents[3]
    if isinstance(card_list, Tag):
        return card_list

    if isinstance(card_list, PageElement):
        return None

    return None


def _get_rarity_text(rarity: Tag) -> str | None:
    rarity_classes = rarity.get("class")
    if not isinstance(rarity_classes, list) or len(rarity_classes) < 2:
        return None

    rarity_text = rarity_classes[1]
    return rarity_text if isinstance(rarity_text, str) else None


def _find_text(card_unit: Tag, class_name: str) -> str | None:
    node = card_unit.find(class_=class_name)
    if node is None:
        return None
    return node.get_text(strip=True)


def _find_image_url(card_unit: Tag) -> str | None:
    image_container = card_unit.find(class_="image")
    if image_container is None or image_container.img is None:
        return None

    src = image_container.img.get("src")
    if not isinstance(src, str):
        return None

    return src.replace("90_126", "front")
