import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import bs4
from data.card import Card, Report


url = 'https://yuyu-tei.jp/game_ws/sell/sell_price.php'

SET_CODES = {
    'w92': 'lovelivesp',
    'w85': 'lovelivenj',
    'w56': 'saekano',
    'w71': 'saekano2.0',
    'w83': '5hy',
    'w90': '5hy2.0'
}

class Yuyutei:
    def __init__(self, set_code) -> None:
        try:
            self.ver = SET_CODES[set_code.lower()]
            self.params = {'ver': self.ver}
        except KeyError:
            raise ValueError(f'Set code {set_code} not detected in database.')
        
        self.load()
    
    def load(self) -> None:
        cards = []

        page = requests.get(url, params=self.params)

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
                if stock == '×':
                    stock = '0'
                elif stock == '◯':
                    stock = '10+'

                cards.append((id.lower(), Card(id, price, stock, rarity_official)))

        cards_dict = {}
        for card in cards:
            cards_dict[card[0]] = card[1]

        self.report = Report(cards_dict, 'yuyutei')
    
    def get_report(self) -> Report:
        return self.report


def yyt_scrape_sets(output_file: str):
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
            img_url = card_unit.find(class_='image').img['src']
            if stock == '×':
                stock = '0'
            elif stock == '◯':
                stock = '10+'
            cards[id.upper()] = Card(id, price, stock, rarity_official, img_url)
    
    return cards

