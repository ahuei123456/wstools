from argparse import ArgumentError
from collections import Counter
import requests

ENC_API_URL_DECK = 'https://www.encoredecks.com/api/deck'
ENC_API_URL_CARD = 'https://www.encoredecks.com/api/card'

class EncoreDecks:
    def __init__(self, url: str):
        sp = url.split('/')
        self.deckcode = sp[-1]
        if len(self.deckcode) == 0:
            raise ArgumentError('Invalid EncoreDecks link')
        
        self.load()
    
    def load(self):
        resp = requests.get(f'{url}{self.deckcode}')
        data = resp.json()

        self.raw = data
        self.decklist = None
        self.sets = None

    def get_sets(self):
        if self.sets == None:
            self.sets = [f'{x["set"]}/{x["side"]}{x["release"]}' for x in self.raw['sets']]            
        return self.sets

    def get_decklist(self):
        if self.decklist == None:
            self.decklist = Counter([x['cardcode'] for x in self.raw['cards']])
        return list(self.decklist.items())


def enc_get_decklist(deckcode: str):
    sp = deckcode.split('/')
    deckcode = sp[-1]
    resp = requests.get(f'{ENC_API_URL_DECK}/{deckcode}')
    data = resp.json()

    return list(Counter([x['cardcode'] for x in data['cards']]).items())


def enc_get_card(cardcode: str):
    resp = requests.get(ENC_API_URL_CARD, params={'cardcode': cardcode})
    data = resp.json()

    return data
