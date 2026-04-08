from PIL import Image
import sites.databases.encore as enc
import proxy.utils as utils
from data.card import Card
import sys


# Configurations
CARD_WIDTH_INCHES = 2.5
CARD_HEIGHT_INCHES = 3.5
DPI = 300  # Dots per inch for printing
CARD_WIDTH_PIXELS = int(CARD_WIDTH_INCHES * DPI)
CARD_HEIGHT_PIXELS = int(CARD_HEIGHT_INCHES * DPI)

CARDS_PER_ROW = 5  # Number of cards in one row
CARDS_PER_COLUMN = 2  # Number of rows
TOTAL_CARDS = CARDS_PER_ROW * CARDS_PER_COLUMN

SHEET_WIDTH_PIXELS = CARD_WIDTH_PIXELS * CARDS_PER_ROW
SHEET_HEIGHT_PIXELS = CARD_HEIGHT_PIXELS * CARDS_PER_COLUMN


def generate_proxy(card: Card, img_url: str, output_file: str):
    image = utils.load_image_fom_url(img_url)
    image = utils.resize_image(image)
    if card.card_type == "CX":
        image.save(output_file)
        return

    skills = card.abilities

    images = []
    for skill in skills:
        images.append(utils.text_to_image(skill, card.color))

    skill_box = utils.merge_images_vertically(*images)
    skill_box = utils.add_border(skill_box)
    card_proxy = utils.add_merged_image_to_background(skill_box, image)

    card_proxy.save(output_file)


def create_print_sheet(image_paths, output_filename="print_sheet.png"):
    if len(image_paths) != TOTAL_CARDS:
        print(f"Error: Expected {TOTAL_CARDS} images, but got {len(image_paths)}")
        sys.exit(1)

    # Create a blank white sheet
    sheet = Image.new("RGB", (SHEET_WIDTH_PIXELS, SHEET_HEIGHT_PIXELS), "white")

    for idx, image_path in enumerate(image_paths):
        img = Image.open(image_path).convert("RGB")
        img = utils.resize_image(img)

        x_offset = (idx % CARDS_PER_ROW) * CARD_WIDTH_PIXELS
        y_offset = (idx // CARDS_PER_ROW) * CARD_HEIGHT_PIXELS

        sheet.paste(img, (x_offset, y_offset))

    sheet.save(output_filename, dpi=(DPI, DPI))
    print(f"Print sheet saved as {output_filename}")


# Example usage: Provide 10 image file paths
image_files = [
    "card1.jpg",
    "card2.jpg",
    ...,
    "card10.jpg",
]  # Replace with actual file paths
create_print_sheet(image_files)
