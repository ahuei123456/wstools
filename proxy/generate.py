from PIL import Image
import sites.databases.encore as enc
import proxy.utils as utils


def generate_proxy(card_code: str, img_url: str, output_file: str):
    card_data = enc.enc_get_card(card_code)
    image = utils.load_image_fom_url(img_url)
    image = utils.resize_image(image)
    if card_data['cardtype'] == 'CX':
        image.save(output_file)
        return
    
    skills = utils.retrieve_tl(card_data)

    images = []
    for skill in skills:
        images.append(utils.text_to_image(skill, card_data['colour']))
    
    skill_box = utils.merge_images_vertically(*images)
    skill_box = utils.add_border(skill_box)
    card_proxy = utils.add_merged_image_to_background(skill_box, image)

    card_proxy.save(output_file)