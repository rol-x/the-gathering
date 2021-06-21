"""Scrape the card market website to get all the neccessary data."""
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


# Return the Firefox webdriver in headless mode.
def create_webdriver():
    '''Return the Firefox webdriver in headless mode.'''
    print('Opening the webdriver')
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    return browser


# Extract information about a card from provided soup, into card dictionary.
def add_card(card_soup, card_dict):
    '''Extract information about a card from provided soup, into card dictionary.'''

    # Get rows from the card information table
    card_info = card_soup.findAll("dd", {"class": "col-6 col-xl-7"})
    # Append the attributes
    card_dict['card_ID'].append(len(card_dict['card_ID']) + 1)
    card_dict['rarity'].append(card_info[0].find('span')['data-original-title'])
    card_dict['available_items'].append(card_info[3].string)
    card_dict['price_from'].append(card_info[4].string)
    card_dict['30_avg_price'].append(card_info[6].string)
    card_dict['7_avg_price'].append(card_info[7].string)
    card_dict['1_avg_price'].append(card_info[8].string)
    card_dict['expansion_name'].append(card_info[1].find('span')['data-original-title'])
    card_dict['card_name'].append(str(card_soup.find("h1")).split('<')[1][3:])

    # Console logging
    print('Card added: ' + card_name)


# Extract information about a seller from provided soup, into seller dictionary.
def add_seller(seller_soup, seller_dict):
    '''Extract information about a seller from provided soup, into seller dictionary.'''

    # Get rows from the seller information table
    seller_name = seller_soup.find("h1")
    if seller_name is None:
        sleep(1.618)
        print('Seller dropped, last seller: ' + seller_dict['seller_name'][-1])
        sleep(1.618)
        return
    if seller_name.string in seller_dict['seller_name']:
        print(f'Seller {seller_name.string} already saved')
        return

    # Append the attributes
    seller_dict['seller_ID'].append(len(seller_dict['seller_ID']) + 1)
    seller_dict['seller_name'].append(seller_name.string)
    seller_dict['type'].append(seller_soup.find("span", {"class": "ml-2 personalInfo-bold"}).string)
    # Member since
    seller_dict['member_since'].append((seller_soup.find("span",
        {"class": "fonticon-info d-none d-md-inline ml-1 small text-muted"}))["title"])
    # Country
    country_div = seller_soup.find("div",
        {"class": "col-12 col-md-6"}).find("span")
    seller_dict['country'].append(country_div["data-original-title"])
    # Address
    address_div = seller_soup.find("div", {"class":
         "d-flex align-items-center justify-content-start flex-wrap personalInfo col-8 col-md-9"}) \
        .findAll("p")
    address = ""
    for line in address_div:
        address = address + line.string + ', '
    seller_dict['address'].append(address.strip(", "))
    if seller_dict['address'][-1] == seller_dict['country'][-1]:
        seller_dict['address'][-1] = None

    # Console logging
    print('Seller added: ' + seller_name.string)

# Add a dummy date.
def add_date(date_dict):
    '''Add a dummy date.'''
    for key in date_dict.keys:
        date_dict[key].append(0)


if __name__ == "__main__":

    # Setup
    base_url = 'https://www.cardmarket.com/en/Magic/Products/Singles/'
    expansion_name = 'Battlebond'
    driver = create_webdriver()

    # Card pre-table
    card_dict = {'card_ID': [],
                 'card_name': [],
                 'expansion_name': [],
                 'rarity': [],
                 'price_from': [],
                 '30_avg_price': [],
                 '7_avg_price': [],
                 '1_avg_price': [],
                 'available_items': []}
    # Seller pre-table
    seller_dict = {'seller_ID': [],
                   'seller_name': [],
                   'type': [],
                   'member_since': [],
                   'country': [],
                   'address': []}
    # Date pre-table
    date_dict = {'date_ID': [],
                 'day': [],
                 'month': [],
                 'year': [],
                 'day_of_week': [],
                 'time': []}

    # Sale offer pre-table
    sale_offer_dict = {'seller_ID': [],
                       'price': [],
                       'card_ID': [],
                       'card_condition': [],
                       'is_foiled': [],
                       'date_ID': []}

    # Cards list iteration
    page_no = 1
    while True:
        # Separate divs with card links and names
        driver.get(base_url + expansion_name + '?site=' + str(page_no))
        print(driver.current_url)
        list_soup = BeautifulSoup(driver.page_source, 'html.parser')
        card_elements = list_soup.findAll("div", {"class":
                       "col-10 col-md-8 px-2 flex-column align-items-start justify-content-center"})
        # After the last page, there are 0 cards per page
        if len(card_elements) == 0:
            print("Last page reached")
            break
        # We open the wanted site and pass the soupified html to extracting function
        for card in card_elements:
            if card.string == 'Name':
                continue
            card_name = card.string
            card_url = base_url + expansion_name + '/' + card_name.replace(' ', '-')
            driver.get(card_url)
            print(driver.current_url)
            while True:
                load_more_button = driver.find_element_by_xpath('//button[@id="loadMoreButton"]')
                if load_more_button.text == "":
                    break
                driver.execute_script("arguments[0].click();", load_more_button)
                print('Extending the sellers view...')
                sleep(0.618)

            card_soup = BeautifulSoup(driver.page_source, 'html.parser')
            add_card(card_soup, card_dict)  # Card added to the dictionary

            sellers = card_soup.findAll('span', {'class': 'd-flex has-content-centered mr-1'})
            for seller in sellers:
                seller_name = seller.find('a').string
                driver.get('https://www.cardmarket.com/en/Magic/Users/' + seller_name)
                sleep(1.618)
                seller_soup = BeautifulSoup(driver.page_source, 'html.parser')
                add_seller(seller_soup, seller_dict)  # Seller added to the dictionary
                print('Seller added: ' + seller_name)

            add_date(date_dict)
            print('Date added')

        page_no += 1
