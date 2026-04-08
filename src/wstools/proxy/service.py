from __future__ import annotations

from pathlib import Path

from requests import HTTPError, RequestException

from wstools.errors import ProxyGenerationError
from wstools.models import Card
from wstools.providers import encore
from wstools.proxy.render import generate_printable_pdf, generate_proxy, generate_proxy_image


def generate_proxy_card(card_code: str, output_file: str | Path) -> Path:
    try:
        card = encore.fetch_card(card_code)
        return generate_proxy(card, build_card_image_url(card), output_file)
    except HTTPError as exc:
        raise ProxyGenerationError(f"Failed to fetch card {card_code} from EncoreDecks.") from exc
    except RequestException as exc:
        raise ProxyGenerationError(
            "Network error while fetching card data from EncoreDecks."
        ) from exc


def generate_proxy_deck(deck_code: str, output_dir: str | Path) -> list[Path]:
    try:
        decklist = encore.fetch_decklist(deck_code)
    except HTTPError as exc:
        raise ProxyGenerationError(f"Failed to fetch deck {deck_code} from EncoreDecks.") from exc
    except RequestException as exc:
        raise ProxyGenerationError(
            "Network error while fetching deck data from EncoreDecks."
        ) from exc

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results: list[Path] = []
    for card_code, card in decklist.unique_cards().items():
        file_name = f"{card_code.split('/')[-1]}.png"
        results.append(generate_proxy(card, build_card_image_url(card), output_path / file_name))

    return results


def generate_proxy_pdf(deck_code: str, output_file: str | Path) -> Path:
    try:
        decklist = encore.fetch_decklist(deck_code)
    except HTTPError as exc:
        raise ProxyGenerationError(f"Failed to fetch deck {deck_code} from EncoreDecks.") from exc
    except RequestException as exc:
        raise ProxyGenerationError(
            "Network error while fetching deck data from EncoreDecks."
        ) from exc

    try:
        card_images = [
            generate_proxy_image(card, build_card_image_url(card))
            for card in decklist.cards
        ]
    except RequestException as exc:
        raise ProxyGenerationError(
            "Network error while fetching card art from EncoreDecks."
        ) from exc

    return generate_printable_pdf(card_images, output_file)


def build_card_image_url(card: Card) -> str:
    if card.image_path is None:
        raise ProxyGenerationError(
            f"EncoreDecks did not return an image path for {card.card_code}."
        )
    return encore.build_image_url(card.image_path)
