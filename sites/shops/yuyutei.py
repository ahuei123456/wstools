import requests
from bs4 import BeautifulSoup
import bs4
from sites.shops.sales import CardSale, Report


url = 'https://yuyu-tei.jp/game_ws/sell/sell_price.php'


class YYTCard(CardSale):
    pass


def yyt_get_images(card_codes: list[str]):
    for card_code in card_codes:
        pass


def yyt_save_data(output_file: str):
    sets = yyt_scrape_sets()


def yyt_scrape_sets():
    page = requests.get(url)

    content = BeautifulSoup(page.content, 'html.parser')
    set_list = content.find('ul', attrs={'data-ui': 'expand'})
    set_labels = set_list.find_all('input', attrs={'type': 'checkbox'})
    sets = {set_label['value']: set_label.parent.text.strip() for set_label in set_labels}
    
    return sets


def yyt_scrape_cards(ver: str):
    cards = {}
    page = requests.get(url, params={'ver': ver})

    content = BeautifulSoup(page.content, 'html.parser')
    card_data = content.find(class_='card_list_box')
    rarities = [x for x in card_data.contents if type(x) == bs4.element.Tag]
    
    for rarity in rarities:
        card_list = rarity.contents[3]
        rarity_text = rarity['class'][1]
        card_units = card_list.find_all(class_=f'card_unit {rarity_text}')
        rarity_official = rarity_text.split('_')[-1]
        for card_unit in card_units:
            id = card_unit.find(class_='id').text.strip()
            price = int(card_unit.find(class_='price').text.strip().split()[-1][:-1])
            stock = card_unit.find(class_='stock').text.strip()[2:]
            img_url = card_unit.find(class_='image').img['src'].replace('90_126', 'front')
            if stock == '×':
                stock = '0'
            elif stock == '◯':
                stock = '10+'
            cards[id.upper()] = YYTCard(id, price, stock, rarity_official, img_url)
    
    return cards


def yyt_scrape_codes(ver: str):
    codes = set()
    page = requests.get(url, params={'ver': ver})

    content = BeautifulSoup(page.content, 'html.parser')
    card_data = content.find(class_='card_list_box')
    try:
        rarities = [x for x in card_data.contents if type(x) == bs4.element.Tag]
    
        for rarity in rarities:
            card_list = rarity.contents[3]
            rarity_text = rarity['class'][1]
            card_units = card_list.find_all(class_=f'card_unit {rarity_text}')
            rarity_official = rarity_text.split('_')[-1]
            for card_unit in card_units:
                id = card_unit.find(class_='id').text.strip()
                codes.add(id.split('/')[0])
    except AttributeError:
        print(f'error in {ver}')

    return codes