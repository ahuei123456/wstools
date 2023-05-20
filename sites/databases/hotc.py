from bs4 import BeautifulSoup
import requests
from data.card import Card

HOTC_URL_CARD = r'https://www.heartofthecards.com/code/cardlist.html'


def hotc_get_card(cardcode: str) -> Card:
    cardcode = f'WS_{cardcode}'
    resp = requests.get(HOTC_URL_CARD, params={'card': cardcode})
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Find all the td elements with the class "cards"
    labels = soup.find_all('td', class_='cards')

    for br in soup.find_all("br"):
        br.replace_with("\n")

    # Iterate over each label and retrieve the associated data
    data = {}
    for label in labels:
        label_text = label.get_text(strip=True).replace(':', '')
        try:
            v = label.find_next('td', class_='cards2').get_text()
            data[label_text] = label.find_next('td', class_='cards2').get_text()
        except AttributeError:
            data[label_text] = label.find_next('td', class_='cards3').get_text()

    attributes = [data['Trait 1']]
    try:
        attributes.append(data['Trait 2'])    
        attributes.append(data['Trait 3'])
    except:
        pass

    return Card(
        data['Card No.'],
        attributes,
        data['English Card Text'].split('\n'),
        'CH' if data['Type'] == 'Character' else 'CX' if data['Type'] == 'Climax' else 'EV',
        data['Color']
    )


if __name__ == '__main__':
    hotc_get_card('WS_AW/S43-001')
