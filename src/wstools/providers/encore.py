from __future__ import annotations

import requests

from wstools.models import Card, Decklist

ENC_API_URL_DECK = "https://www.encoredecks.com/api/deck"
ENC_API_URL_CARD = "https://www.encoredecks.com/api/card"
ENC_IMAGE_BASE_URL = "https://www.encoredecks.com/images"
REQUEST_TIMEOUT_SECONDS = 15


def fetch_decklist(deck_code: str) -> Decklist:
    normalized_code = deck_code.split("/")[-1]
    response = requests.get(
        f"{ENC_API_URL_DECK}/{normalized_code}",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()

    return Decklist(
        source="encoredecks",
        cards=[parse_card_json(card_data) for card_data in data["cards"]],
    )


def fetch_card(card_code: str) -> Card:
    response = requests.get(
        ENC_API_URL_CARD,
        params={"cardcode": card_code},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()
    return parse_card_json(data)


def parse_card_json(data: dict) -> Card:
    image_path = data.get("imagepath")
    if not isinstance(image_path, str):
        image_path = None

    return Card(
        card_code=data["cardcode"],
        attributes=tuple(data["locale"]["EN"]["attributes"]),
        abilities=tuple(data["locale"]["EN"]["ability"]),
        card_type=data["cardtype"],
        color=data["colour"],
        image_path=image_path,
    )


def build_image_url(image_path: str) -> str:
    return f"{ENC_IMAGE_BASE_URL}/{image_path.lstrip('/')}"
