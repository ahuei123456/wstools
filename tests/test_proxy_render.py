from pathlib import Path

from PIL import Image

from wstools.models import Card
from wstools.proxy import render


def test_text_to_image_creates_rgb_image() -> None:
    image = render.text_to_image("sample ability text", "blue")

    assert image.mode == "RGB"
    assert image.size[0] == render.PROXY_TEXT_BOX_WIDTH
    assert image.size[1] > 0


def test_text_color_uses_white_for_dark_card_colors() -> None:
    assert render._text_color_for_background("red") == "white"
    assert render._text_color_for_background("blue") == "white"
    assert render._text_color_for_background("green") == "white"
    assert render._text_color_for_background("yellow") == "black"


def test_generate_proxy_writes_file(monkeypatch, tmp_path: Path) -> None:
    card = Card(
        card_code="PAD/S105-001",
        attributes=("Trait",),
        abilities=("This is a sample ability.",),
        card_type="CH",
        color="blue",
    )

    monkeypatch.setattr(
        render,
        "load_image_from_url",
        lambda url: Image.new("RGB", render.CARD_IMAGE_SIZE, "white"),
    )

    output_path = tmp_path / "proxy.png"
    result = render.generate_proxy(card, "https://example.com/card.png", output_path)

    assert result == output_path
    assert output_path.exists()


def test_compose_printable_pages_uses_letter_size_layout() -> None:
    card_images = [
        Image.new("RGB", render.CARD_IMAGE_SIZE, "red")
        for _ in range(render.TOTAL_CARDS + 1)
    ]

    pages = render.compose_printable_pages(card_images)
    origin_x, origin_y = render._page_origin()

    assert len(pages) == 2
    assert pages[0].size == render.PAGE_IMAGE_SIZE
    assert pages[1].size == render.PAGE_IMAGE_SIZE
    assert pages[0].getpixel((origin_x + 10, origin_y + 10)) == (255, 0, 0)
    assert pages[0].getpixel((10, 10)) == (255, 255, 255)


def test_generate_printable_pdf_writes_file(tmp_path: Path) -> None:
    card_images = [Image.new("RGB", render.CARD_IMAGE_SIZE, "white")]
    output_path = tmp_path / "deck.pdf"

    result = render.generate_printable_pdf(card_images, output_path)

    assert result == output_path
    assert output_path.exists()


def test_add_overlay_to_background_respects_footer_clearance() -> None:
    background = Image.new("RGB", render.CARD_IMAGE_SIZE, "white")
    overlay = Image.new("RGB", (100, 80), "red")

    result = render.add_overlay_to_background(overlay, background.copy())
    expected_x = render.PROXY_MARGIN_SIDE
    expected_y = render.CARD_HEIGHT_PIXELS - overlay.size[1] - render.PROXY_MARGIN_BOTTOM

    assert result.getpixel((expected_x + 5, expected_y + 5)) == (255, 0, 0)
    assert result.getpixel((expected_x + 5, render.CARD_HEIGHT_PIXELS - 5)) == (255, 255, 255)


def test_prepare_source_image_rotates_landscape_cx_card() -> None:
    card = Card(
        card_code="LHS/W122-069",
        attributes=(),
        abilities=(),
        card_type="CX",
        color="red",
    )
    landscape = Image.new("RGB", (560, 400), "red")

    result = render.prepare_source_image(card, landscape)

    assert result.size == (400, 560)
