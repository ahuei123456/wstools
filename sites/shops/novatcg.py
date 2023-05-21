import requests
from bs4 import BeautifulSoup
from data.card import Card
from sites.shops.sales import CardSale

NOVA_TCG_URL = 'https://www.novatcg.com/product/'

class NovaTCGCard(CardSale):
    pass


def nova_get_card_sale(card_code: str):
    card_code_f = card_code.replace('/', '-')
    url = f'{NOVA_TCG_URL}{card_code_f}/'

    page = requests.get(url)
    content = BeautifulSoup(page.content, 'html.parser')
    
    for br in content.find_all("br"):
        br.replace_with("\n")

    try:
        input_field = content.find('input', class_='input-text qty text')
        max_value = input_field.get('max')
    except AttributeError:
        max_value = 0

    div = content.find("div", class_='woocommerce-product-gallery__image')
    a_tag = div.find('a')

    img_url = a_tag.get("href")

    return NovaTCGCard(
        card_code,
        0,
        max_value,
        'C',
        img_url
    )


def nova_get_card(card_code: str):
    card_code_f = card_code.replace('/', '-')
    url = f'{NOVA_TCG_URL}{card_code_f}/'

    page = requests.get(url)
    content = BeautifulSoup(page.content, 'html.parser')
    
    for br in content.find_all("br"):
        br.replace_with("\n")

    table = content.find("table", class_="cards")
    previous_p = table.find_previous_sibling("p")
    text = previous_p.get_text()
    abilities = [x for x in text.split('\n') if len(x) > 0]

    print(abilities)

    # Define the target <td> elements to search for
    target_td_texts = ["Color", "Type", "Trait 1", "Trait 2"]

    # Initialize a dictionary to store the extracted values
    extracted_values = {}

    # Iterate over each <tr> element within the table
    for row in table.find_all("tr"):
        # Find all <td> elements within the row
        tds = row.find_all("td")

        # Iterate over each <td> element
        for td in tds:
            # Get the text of the <td> element
            td_text = td.get_text(strip=True)[:-1]

            # Check if the text matches the target
            if td_text in target_td_texts:
                # Get the text of the subsequent <td> element
                next_td_text = td.find_next_sibling("td").get_text(strip=True)
                # Add the extracted value to the dictionary
                extracted_values[td_text] = next_td_text

    # Print the extracted values
    for key, value in extracted_values.items():
        print(f"{key}: {value}")

    return Card(
        card_code,
        [extracted_values.get('Trait 1'), extracted_values.get('Trait 2')],
        abilities,
        'CH' if extracted_values['Type'] == 'Character' else 'CX' if extracted_values['Type'] == 'Climax' else 'EV',
        extracted_values['Color']
    )


if __name__ == '__main__':
    nova_get_card('PAD/S105-001')