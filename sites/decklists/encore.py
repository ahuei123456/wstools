from argparse import ArgumentError
from collections import Counter
import requests

url = 'https://www.encoredecks.com/api/deck/'

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

        freq = Counter([x['cardcode'] for x in data['cards']])

        self.decklist = freq

    def get_decklist(self):
        return self.decklist.items()