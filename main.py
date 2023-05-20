import argparse
import sites.shops.yuyutei as yyt
import sites.databases.encore as enc
import sites.databases.hotc as hotc
import proxy.generate as gen
from data.card import Card

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

c = hotc.hotc_get_card('AW/S43-025')
print(c)


