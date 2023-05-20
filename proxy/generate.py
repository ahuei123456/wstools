from PIL import Image
import sites.databases.encore as enc
import proxy.utils as utils
from data.card import Card


def generate_proxy(card: Card, img_url: str, output_file: str):
    image = utils.load_image_fom_url(img_url)
    image = utils.resize_image(image)
    if card.card_type == 'CX':
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