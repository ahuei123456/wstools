from __future__ import annotations

from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

from wstools.models import Card

CARD_WIDTH_INCHES = 2.5
CARD_HEIGHT_INCHES = 3.5
DPI = 300
CARD_WIDTH_PIXELS = int(CARD_WIDTH_INCHES * DPI)
CARD_HEIGHT_PIXELS = int(CARD_HEIGHT_INCHES * DPI)
CARD_IMAGE_SIZE = (CARD_WIDTH_PIXELS, CARD_HEIGHT_PIXELS)

CARDS_PER_ROW = 5
CARDS_PER_COLUMN = 2
TOTAL_CARDS = CARDS_PER_ROW * CARDS_PER_COLUMN

LETTER_WIDTH_INCHES = 11
LETTER_HEIGHT_INCHES = 8.5
PAGE_MARGIN_INCHES = 0.25
CARD_GAP_INCHES = 0.125
PRINT_CARD_WIDTH_INCHES = 2.0
PRINT_CARD_HEIGHT_INCHES = PRINT_CARD_WIDTH_INCHES * (CARD_HEIGHT_INCHES / CARD_WIDTH_INCHES)

PAGE_WIDTH_PIXELS = int(LETTER_WIDTH_INCHES * DPI)
PAGE_HEIGHT_PIXELS = int(LETTER_HEIGHT_INCHES * DPI)
PAGE_IMAGE_SIZE = (PAGE_WIDTH_PIXELS, PAGE_HEIGHT_PIXELS)
PAGE_MARGIN_PIXELS = int(PAGE_MARGIN_INCHES * DPI)
CARD_GAP_PIXELS = int(CARD_GAP_INCHES * DPI)
PRINT_CARD_WIDTH_PIXELS = int(PRINT_CARD_WIDTH_INCHES * DPI)
PRINT_CARD_HEIGHT_PIXELS = int(PRINT_CARD_HEIGHT_INCHES * DPI)
PRINT_CARD_IMAGE_SIZE = (PRINT_CARD_WIDTH_PIXELS, PRINT_CARD_HEIGHT_PIXELS)

PROXY_MARGIN_BOTTOM = 160
PROXY_MARGIN_SIDE = 15
PROXY_BORDER_WIDTH = 2
PROXY_TEXT_BOX_WIDTH = CARD_WIDTH_PIXELS - (2 * PROXY_MARGIN_SIDE) - (2 * PROXY_BORDER_WIDTH)
PROXY_TEXT_PADDING_WIDTH = 5
PROXY_TEXT_PADDING_HEIGHT = 5
PROXY_FONT_SIZE = 26
REQUEST_TIMEOUT_SECONDS = 15


def generate_proxy(card: Card, img_url: str, output_file: str | Path) -> Path:
    proxy_image = generate_proxy_image(card, img_url)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    proxy_image.save(output_path)
    return output_path


def generate_proxy_image(card: Card, img_url: str) -> Image.Image:
    source_image = prepare_source_image(card, load_image_from_url(img_url))
    background = resize_image(
        source_image,
        preserve_aspect=source_image.width > source_image.height,
    )
    return compose_proxy_image(card, background)


def compose_proxy_image(card: Card, background: Image.Image) -> Image.Image:
    if card.card_type == "CX" or not card.abilities:
        return background

    skill_images = [text_to_image(skill, card.color) for skill in card.abilities if skill.strip()]
    if not skill_images:
        return background

    skill_box = add_border(merge_images_vertically(*skill_images))
    return add_overlay_to_background(skill_box, background)


def generate_printable_pdf(
    card_images: list[Image.Image],
    output_filename: str | Path,
) -> Path:
    if not card_images:
        raise ValueError("Expected at least one card image.")

    pages = compose_printable_pages(card_images)
    output_path = Path(output_filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(
        output_path,
        "PDF",
        resolution=DPI,
        save_all=True,
        append_images=pages[1:],
    )
    return output_path


def compose_printable_pages(card_images: list[Image.Image]) -> list[Image.Image]:
    pages: list[Image.Image] = []
    resized_cards = [resize_for_print(card_image.convert("RGB")) for card_image in card_images]

    for start in range(0, len(resized_cards), TOTAL_CARDS):
        page = Image.new("RGB", PAGE_IMAGE_SIZE, "white")
        page_cards = resized_cards[start : start + TOTAL_CARDS]
        origin_x, origin_y = _page_origin()
        for index, card_image in enumerate(page_cards):
            x_offset = origin_x + (index % CARDS_PER_ROW) * (
                PRINT_CARD_WIDTH_PIXELS + CARD_GAP_PIXELS
            )
            y_offset = origin_y + (index // CARDS_PER_ROW) * (
                PRINT_CARD_HEIGHT_PIXELS + CARD_GAP_PIXELS
            )
            page.paste(card_image, (x_offset, y_offset))

        pages.append(page)

    return pages


def resize_image(image: Image.Image, preserve_aspect: bool = False) -> Image.Image:
    return resize_to_canvas(image, CARD_IMAGE_SIZE, preserve_aspect=preserve_aspect)


def resize_for_print(image: Image.Image) -> Image.Image:
    return resize_to_canvas(
        image,
        PRINT_CARD_IMAGE_SIZE,
        preserve_aspect=image.width > image.height,
    )


def resize_to_canvas(
    image: Image.Image,
    target_size: tuple[int, int],
    preserve_aspect: bool = False,
) -> Image.Image:
    if not preserve_aspect:
        return image.resize(target_size, Image.Resampling.LANCZOS)

    contained = ImageOps.contain(image, target_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", target_size, "white")
    x_offset = (target_size[0] - contained.size[0]) // 2
    y_offset = (target_size[1] - contained.size[1]) // 2
    canvas.paste(contained.convert("RGB"), (x_offset, y_offset))
    return canvas


def text_to_image(text: str, background_color: str) -> Image.Image:
    lines = _wrap_text(text)
    image_height = (
        (PROXY_FONT_SIZE * len(lines))
        + (PROXY_TEXT_PADDING_HEIGHT * (len(lines) - 1))
        + (2 * PROXY_TEXT_PADDING_HEIGHT)
    )
    image = Image.new("RGB", (PROXY_TEXT_BOX_WIDTH, image_height), background_color)

    draw = ImageDraw.Draw(image)
    y_offset = 0
    font = _load_font()
    text_color = _text_color_for_background(background_color)
    for line in lines:
        draw.text((PROXY_TEXT_PADDING_WIDTH, y_offset), line, font=font, fill=text_color)
        y_offset += PROXY_FONT_SIZE + PROXY_TEXT_PADDING_HEIGHT

    return image


def merge_images_vertically(*images: Image.Image) -> Image.Image:
    if not images:
        raise ValueError("Expected at least one image to merge.")

    width = images[0].size[0]
    height = sum(image.size[1] for image in images)
    merged_image = Image.new("RGB", (width, height))

    y_offset = 0
    for image in images:
        merged_image.paste(image, (0, y_offset))
        y_offset += image.size[1]

    return merged_image


def add_border(image: Image.Image, border: int = PROXY_BORDER_WIDTH) -> Image.Image:
    return ImageOps.expand(image, border=border, fill="black")


def add_overlay_to_background(
    overlay_image: Image.Image,
    background_image: Image.Image,
    margin_side: int = PROXY_MARGIN_SIDE,
    margin_bottom: int = PROXY_MARGIN_BOTTOM,
) -> Image.Image:
    x_offset = margin_side
    y_offset = background_image.size[1] - overlay_image.size[1] - margin_bottom
    background_image.paste(overlay_image, (x_offset, y_offset))
    return background_image


def load_image_from_url(url: str) -> Image.Image:
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGB")


def prepare_source_image(card: Card, image: Image.Image) -> Image.Image:
    if card.card_type == "CX" and image.width > image.height:
        return image.transpose(Image.Transpose.ROTATE_270)
    return image


def _wrap_text(text: str) -> list[str]:
    font = _load_font()
    words = text.split()
    if not words:
        return [""]

    lines = [words[0]]
    for word in words[1:]:
        candidate = f"{lines[-1]} {word}"
        if font.getlength(candidate) <= PROXY_TEXT_BOX_WIDTH - (2 * PROXY_TEXT_PADDING_WIDTH):
            lines[-1] = candidate
        else:
            lines.append(word)

    return lines


def _load_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_path = Path(__file__).resolve().parent.parent / "assets" / "NotoSansJP-Regular.ttf"
    if font_path.exists():
        return ImageFont.truetype(str(font_path), PROXY_FONT_SIZE)

    repo_font = Path.cwd() / "NotoSansJP-Regular.ttf"
    if repo_font.exists():
        return ImageFont.truetype(str(repo_font), PROXY_FONT_SIZE)

    return ImageFont.load_default()


def _text_color_for_background(background_color: str) -> str:
    normalized = background_color.strip().lower()
    if normalized in {"red", "blue", "green"}:
        return "white"
    return "black"


def _page_origin() -> tuple[int, int]:
    grid_width = (CARDS_PER_ROW * PRINT_CARD_WIDTH_PIXELS) + ((CARDS_PER_ROW - 1) * CARD_GAP_PIXELS)
    grid_height = (CARDS_PER_COLUMN * PRINT_CARD_HEIGHT_PIXELS) + (
        (CARDS_PER_COLUMN - 1) * CARD_GAP_PIXELS
    )
    printable_width = PAGE_WIDTH_PIXELS - (2 * PAGE_MARGIN_PIXELS)
    printable_height = PAGE_HEIGHT_PIXELS - (2 * PAGE_MARGIN_PIXELS)
    extra_width = printable_width - grid_width
    extra_height = printable_height - grid_height

    return (
        PAGE_MARGIN_PIXELS + max(extra_width // 2, 0),
        PAGE_MARGIN_PIXELS + max(extra_height // 2, 0),
    )
