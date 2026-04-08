from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from wstools.models import Card
from wstools.providers.sales import CardSale

NOVA_TCG_URL = "https://www.novatcg.com/product/"
REQUEST_TIMEOUT_SECONDS = 15


class NovaTCGCard(CardSale):
    """NovaTCG sale listing."""


def fetch_sale(card_code: str) -> NovaTCGCard:
    content = _fetch_product_page(card_code)

    stock_input = content.find("input", class_="input-text qty text")
    max_value = stock_input.get("max") if stock_input is not None else "0"
    if not isinstance(max_value, str):
        max_value = "0"

    gallery = content.find("div", class_="woocommerce-product-gallery__image")
    if gallery is None:
        raise ValueError(f"Could not find product image for {card_code}.")

    gallery_link = gallery.find("a")
    if gallery_link is None:
        raise ValueError(f"Could not find product image link for {card_code}.")

    img_url = gallery_link.get("href")
    if not isinstance(img_url, str):
        raise ValueError(f"Could not find product image URL for {card_code}.")

    return NovaTCGCard(
        cid=card_code,
        price=0,
        stock=max_value or "0",
        rarity="C",
        img_url=img_url,
    )


def fetch_card(card_code: str) -> Card:
    content = _fetch_product_page(card_code)
    table = content.find("table", class_="cards")
    if table is None:
        raise ValueError(f"Could not find card metadata table for {card_code}.")

    previous_paragraph = table.find_previous_sibling("p")
    abilities = ()
    if previous_paragraph is not None:
        abilities = tuple(line for line in previous_paragraph.get_text().split("\n") if line)

    target_fields = {"Color", "Type", "Trait 1", "Trait 2"}
    extracted_values: dict[str, str] = {}

    for row in table.find_all("tr"):
        columns = row.find_all("td")
        for column in columns:
            field_name = column.get_text(strip=True).removesuffix(":")
            if field_name not in target_fields:
                continue
            sibling = column.find_next_sibling("td")
            if sibling is not None:
                extracted_values[field_name] = sibling.get_text(strip=True)

    return Card(
        card_code=card_code,
        attributes=tuple(value for value in _trait_values(extracted_values) if value),
        abilities=abilities,
        card_type=_normalize_card_type(extracted_values["Type"]),
        color=extracted_values["Color"],
    )


def _fetch_product_page(card_code: str) -> BeautifulSoup:
    normalized_code = card_code.replace("/", "-")
    response = requests.get(
        f"{NOVA_TCG_URL}{normalized_code}/",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    content = BeautifulSoup(response.content, "html.parser")

    for line_break in content.find_all("br"):
        line_break.replace_with("\n")

    return content


def _normalize_card_type(card_type: str) -> str:
    if card_type == "Character":
        return "CH"
    if card_type == "Climax":
        return "CX"
    return "EV"


def _trait_values(extracted_values: dict[str, str]) -> tuple[str | None, str | None]:
    return extracted_values.get("Trait 1"), extracted_values.get("Trait 2")
