from typing import Tuple
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO

PROXY_IMG_WIDTH = 500
PROXY_IMG_HEIGHT = 700
PROXY_IMG_DIMENSIONS = (PROXY_IMG_WIDTH, PROXY_IMG_HEIGHT)

PROXY_MARGIN_BOTTOM = 90
PROXY_MARGIN_SIDE = 15

PROXY_BORDER_WIDTH = 2

PROXY_LOWER_Y = PROXY_IMG_HEIGHT - PROXY_MARGIN_BOTTOM
PROXY_LEFT_X = PROXY_MARGIN_SIDE
PROXY_RIGHT_X = PROXY_IMG_WIDTH - PROXY_MARGIN_SIDE

PROXY_TEXT_BOX_WIDTH = PROXY_RIGHT_X - PROXY_LEFT_X - 2 * PROXY_BORDER_WIDTH
PROXY_TEXT_PADDING_WIDTH = 5  # Number of pixels between the text and the sides of the image
PROXY_TEXT_PADDING_HEIGHT = 5  # Number of pixels between each line of text

PROXY_FONT_SIZE = 15

PROXY_FONT = 'NotoSansJP-Regular.ttf'


def resize_image(img: Image) -> Image:
    return img.resize(PROXY_IMG_DIMENSIONS)


def text_to_image(text: str, bg_color: str) -> Image:
    # Set the font size and type
    font_size = PROXY_FONT_SIZE
    font = ImageFont.truetype(PROXY_FONT, font_size)
    
    # Split the text into words
    words = text.split()
    
    # Build lines of text that fit within the maximum width
    lines = []
    current_line = words[0]
    for word in words[1:]:
        if font.getlength(current_line + ' ' + word) <= PROXY_TEXT_BOX_WIDTH - 2 * PROXY_TEXT_PADDING_WIDTH:
            current_line += ' ' + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    
    # Get the size of the text and create a new image with that size
    text_height = font_size
    image_width = PROXY_TEXT_BOX_WIDTH
    image_height = text_height * len(lines) + PROXY_TEXT_PADDING_HEIGHT * (len(lines) - 1) + 2 * PROXY_TEXT_PADDING_HEIGHT
    image = Image.new('RGB', (image_width, image_height), bg_color)
    
    # Draw the text on the image
    draw = ImageDraw.Draw(image)
    x_text = PROXY_TEXT_PADDING_WIDTH
    y_text = 0
    for line in lines:
        draw.text((x_text, y_text), line, font=font, fill='black')
        y_text += text_height + PROXY_TEXT_PADDING_HEIGHT
    
    return image


def merge_images_vertically(*images: Image) -> Image:
    # Get the width of the images
    width = images[0].size[0]

    # Calculate the height of the merged image
    total_height = sum(image.size[1] for image in images)

    # Create a new image with the merged size
    merged_image = Image.new("RGB", (width, total_height))

    # Merge the images vertically
    y_offset = 0
    for image in images:
        merged_image.paste(image, (0, y_offset))
        y_offset += image.size[1]

    return merged_image


def add_border(im: Image, border=PROXY_BORDER_WIDTH) -> Image:
    return ImageOps.expand(im, border=PROXY_BORDER_WIDTH, fill='black')


def add_merged_image_to_background(merged_image: Image, background_image: Image, margins: Tuple[int, int]=(PROXY_MARGIN_SIDE, PROXY_MARGIN_BOTTOM)) -> Image:
    # Calculate the position to paste the merged image
    x_offset = margins[0]
    y_offset = background_image.size[1] - merged_image.size[1] - margins[1]

    # Add a border to the merged image
    bordered_image = add_border(merged_image)

    # Paste the merged image onto the background image
    background_image.paste(bordered_image, (x_offset, y_offset))

    return background_image


def load_image_fom_url(url: str) -> Image:
    response = requests.get(url, verify=False)
    img_data = response.content
    return Image.open(BytesIO(img_data))


def retrieve_tl(card_data):
    try:
        return card_data["locale"]["EN"]["ability"]
    except:
        return 'TL not available'

if __name__ == '__main__':
    # Set the text and background color
    text: str = '[C] – All of your other《Knocker-Up》or《Yura Island》Characters gain +500 Power.'
    bg_color: str = 'blue'

    # Generate the image
    image: Image = text_to_image(text, bg_color)

    text2: str = '[S] – [(1) Send this STAND card to Memory] Choose one [夢見る高校生 蘭堂], [虹がかかるひととき 蘭堂], or [古堅 蘭堂], add it to your Hand.'
    bg_color2: str = 'blue'


    image2 : Image = text_to_image(text2, bg_color2)

    image3 = merge_images_vertically(image, image2)

    background_image = Image.open('antisalvage.jpg')

    result = add_merged_image_to_background(image3, background_image)

    # Save the image to a file
    filename: str = 'output.png'
    result.save(filename)

