from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from wstools.models import Card

HOTC_URL_CARD = "https://www.heartofthecards.com/code/cardlist.html"
REQUEST_TIMEOUT_SECONDS = 15


def fetch_card(card_code: str) -> Card:
    response = requests.get(
        HOTC_URL_CARD,
        params={"card": f"WS_{card_code}"},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for line_break in soup.find_all("br"):
        line_break.replace_with("\n")

    data: dict[str, str] = {}
    for label in soup.find_all("td", class_="cards"):
        label_text = label.get_text(strip=True).replace(":", "")
        value_cell = label.find_next("td", class_="cards2")
        if value_cell is None:
            value_cell = label.find_next("td", class_="cards3")
        if value_cell is not None:
            data[label_text] = value_cell.get_text()

    attributes = [data["Trait 1"]]
    for key in ("Trait 2", "Trait 3"):
        if key in data:
            attributes.append(data[key])

    return Card(
        card_code=data["Card No."],
        attributes=tuple(attributes),
        abilities=tuple(line for line in data["English Card Text"].split("\n") if line),
        card_type=_normalize_card_type(data["Type"]),
        color=data["Color"],
    )


def _normalize_card_type(card_type: str) -> str:
    if card_type == "Character":
        return "CH"
    if card_type == "Climax":
        return "CX"
    return "EV"
