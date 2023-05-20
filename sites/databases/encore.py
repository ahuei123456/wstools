from argparse import ArgumentError
from collections import Counter
from data.card import Card
from data.card import Decklist
import requests

ENC_API_URL_DECK = 'https://www.encoredecks.com/api/deck'
ENC_API_URL_CARD = 'https://www.encoredecks.com/api/card'


def enc_get_decklist(deckcode: str):
    sp = deckcode.split('/')
    deckcode = sp[-1]
    resp = requests.get(f'{ENC_API_URL_DECK}/{deckcode}')
    data = resp.json()

    decklist = Decklist('encoredecks',
                        [enc_parse_card_json(c) for c in data['cards']])

    return decklist


def enc_get_card(cardcode: str):
    resp = requests.get(ENC_API_URL_CARD, params={'cardcode': cardcode})
    data = resp.json()

    return enc_parse_card_json(data)


def enc_parse_card_json(data):
    card = Card(data['cardcode'], 
                data['locale']['EN']['attributes'], 
                data['locale']['EN']['ability'],
                data['cardtype'],
                data['colour'])

    return card
