import argparse
import sites.shops.yuyutei as yyt
import sites.decklists.encore as enc
from sites.shops.yuyutei import Yuyutei
from data.card import Card

from sites.decklists.encore import EncoreDecks
from argparse import ArgumentParser

"""
playset = ['RR+', 'RR', 'R', 'U', 'C', 'CR', 'CC']
code = '5hy/w90'

data = Yuyutei(code)

report = data.get_report()

total_price, instock_price, missing = report.get_playset_price(*playset)

print(f'Set: {code.upper()}\n---------------------\nPlayset price: {total_price}\nInstock price: {instock_price}\n')
if len(missing) > 0:
    print('Missing\n---------------------')
    for m in missing:
        print(f'{m[0]}: {m[1]}')
"""

"""
parser = ArgumentParser()
parser.add_argument('-dc', '--deck_code', help='Deck code on EncoreDecks')
parser.add_argument('-yyt', '--yuyutei_file', help='File with yuyutei set mappings')

args = parser.parse_args()

set_code = 'lsp/w92'
deck_code = args.deck_code

data = Yuyutei(set_code)
report = data.get_report()

decklist = EncoreDecks(deck_code)

deck = decklist.get_decklist()

total_price, instock_price, missing, errors = report.get_list_price(deck)

print(f'Deck code {deck_code} costs {total_price} on YYT')
"""

"""
v = enc.enc_get_decklist('BNC1m4Rmw')
c = yyt.yyt_scrape_cards('azl')

for card in v:
    if card[0] in c:
        card_data = enc.enc_get_card(card[0])
        print(f'{card[0]} ({card[1]}): {card_data["locale"]["EN"]["ability"]}')
        # print(f'{card[0]} ({card[1]}): {c[card[0]].img_url}')
"""

