import argparse
import sites.shops.yuyutei as yyt
import sites.databases.encore as enc
import sites.databases.hotc as hotc
import sites.shops.novatcg as nova
import proxy.generate as gen
from data.card import Card
import json

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




# v = enc.enc_get_decklist('X6LSRnhEL')
# c = yyt.yyt_scrape_cards('rz')
# c.update(yyt.yyt_scrape_cards('rz2.0'))
# c.update(yyt.yyt_scrape_cards('rz3.0'))
# c.update(yyt.yyt_scrape_cards('rzext1.0'))
# for card in v:
#     card_code = card[0]
#     if card_code in c:
#         img_url = c[card_code].img_url
#         gen.generate_proxy(card_code, img_url, f'{card_code.split("/")[-1]}.png')

# c = hotc.hotc_get_card('AW/S43-025')
# print(c)

# print(yyt.yyt_scrape_sets('ok'))

# code_to_image_mappings = {}

# sets = yyt.yyt_scrape_sets()
# for key in sets:
#     print(f'processing {key}')
#     codes = yyt.yyt_scrape_codes(key)

#     for code in codes:
#         if code in code_to_image_mappings:
#             code_to_image_mappings[code].append(key)
#         else:
#             code_to_image_mappings[code] = [key]

# with open('yyt_mappings.json', 'w') as f:
#     json.dump(code_to_image_mappings, f)

parser = ArgumentParser()
parser.add_argument('-dc', '--deck_code', help='Deck code on EncoreDecks')

args = parser.parse_args()

dl = enc.enc_get_decklist(args.deck_code)

for c in dl.cards:
    card_code = c.card_code
    ec = nova.nova_get_card_sale(card_code)

    gen.generate_proxy(c, ec.img_url, f'{card_code.split("/")[-1]}.png')