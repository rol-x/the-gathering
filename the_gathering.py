"""Scrape the card market website to get all the neccessary data."""
import os
from time import sleep
from datetime import datetime
from random import normalvariate, random, sample
import pandas as pd
import mysql.connector
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


# Wait about mean_val seconds before proceeding to the rest of the code.
def realistic_pause(mean_val):
    '''Wait ~mean_val seconds before proceeding to the rest of the code.'''
    std_val = mean_val * random() * 0.25 + 0.05
    sleep_time = abs(normalvariate(mean_val, std_val)) + 0.1
    print(f'Sleeping for {sleep_time} seconds')
    sleep(sleep_time)


# Return the Firefox webdriver in headless mode.
def create_webdriver():
    '''Return the Firefox webdriver in headless mode.'''
    print('Opening the webdriver')
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    return browser


# Try to load a .csv file content into a dataframe.
def load_df(entity_name):
    '''Try to return a dataframe from the respective .csv file.'''
    try:
        df = pd.read_csv('data/' + entity_name + '.csv', sep=';')
    except pd.errors.EmptyDataError as empty:
        print(empty)
        print(f'Please prepare the headers in {entity_name}.csv!\n')
    return df


# Extract information about a card from provided soup.
def add_card(card_soup, current_date_ID):
    '''Extract information about a card from provided soup.'''

    # Load the card and date dataframes
    card_df = load_df('card')

    # Get rows from the card information table
    card_info = card_soup.findAll("dd", {"class": "col-6 col-xl-7"})
    if len(card_info) == 0:
        print('No card info found on current page')
        return

    # Get the attributes
    card_ID = len(card_df.index) + 1
    card_name = str(card_soup.find("h1")).split('<')[1][3:]
    rarity = card_info[0].find('span')['data-original-title']
    expansion_name = card_info[1].find('span')['data-original-title']
    available_items = card_info[3].string
    price_from = card_info[4].string[:-2].replace(',', '.')
    avg_30_price = card_info[6].string.string[:-2].replace(',', '.')
    avg_7_price = card_info[7].string.string[:-2].replace(',', '.')
    avg_1_price = card_info[8].string.string[:-2].replace(',', '.')

    # Save the card in local file
    with open('data/card.csv', 'a') as card_csv:
        card_csv.write(str(card_ID) + ';')
        card_csv.write(str(card_name) + ';')
        card_csv.write(str(expansion_name) + ';')
        card_csv.write(str(rarity) + ';')
        card_csv.write(str(price_from) + ';')
        card_csv.write(str(avg_30_price) + ';')
        card_csv.write(str(avg_7_price) + ';')
        card_csv.write(str(avg_1_price) + ';')
        card_csv.write(str(available_items) + ';')
        card_csv.write(str(current_date_ID) + '\n')

    # Console logging
    print('Card added: ' + card_name)


# Extract information about a seller from provided soup.
def add_seller(seller_soup):
    '''Extract information about a seller from provided soup.'''

    # Load the seller dataframe
    seller_df = load_df('seller')

    # Get rows from the seller information table on page
    seller_name = seller_soup.find("h1")

    # User not loaded correctly
    if seller_name is None:
        realistic_pause(1.618)
        print('Seller dropped!')
        realistic_pause(1.618)
        return

    # Check if seller is already in file
    seller_name = str(seller_name.string)

    # Seller ID
    seller_ID = len(seller_df.index) + 1

    # Type
    s_type = seller_soup.find("span",
                              {"class":
                               "ml-2 personalInfo-bold"}).string

    # Member since
    member_since = seller_soup.find("span",
                                    {"class": "ml-1 "
                                     + "personalInfo-light "
                                     + "d-none "
                                     + "d-md-block"}).string.split(' ')[-1]

    # Country
    country = seller_soup.find("div",
                               {"class":
                                "col-12 col-md-6"}) \
        .find("span")["data-original-title"]

    # Address
    address_div = seller_soup.findAll("div", {"class": "d-flex "
                                              + "align-items-center "
                                              + "justify-content-start "
                                              + "flex-wrap "
                                              + "personalInfo "
                                              + "col-8 "
                                              + "col-md-9"})[-1] \
        .findAll("p")
    address = ''
    for line in address_div:
        address = address + line.string + ', '
    address = address.strip(', ')
    if address == country:
        address = ''

    # Save the seller in local file
    with open('data/seller.csv', 'a') as seller_csv:
        seller_csv.write(str(seller_ID) + ';')
        seller_csv.write(seller_name + ';')
        seller_csv.write(s_type + ';')
        seller_csv.write(member_since + ';')
        seller_csv.write(country + ';')
        seller_csv.write(address + '\n')

    # Console logging
    print('Seller added to local file: ' + seller_name)


# Add the current date, return the date ID and its log file name.
def add_date():
    '''Add the current date, return the date ID and its log file name.'''

    # Load the date dataframe
    date_df = load_df('date')

    # Prepare the attributes
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y %H:%M").split(" ")
    day = date_time[0].split("/")[0]
    month = date_time[0].split("/")[1]
    year = date_time[0].split("/")[2]
    date_ID = len(date_df.index) + 1

    # Check for the same datetime record
    same_date = date_df[(date_df['day'] == int(day))
                        & (date_df['month'] == int(month))
                        & (date_df['year'] == int(year))
                        & (date_df['time'] == date_time[1])]['date_ID']
    if(len(same_date) > 0):
        print('Date [' + date_time[0] + ' ' + date_time[1]
              + '] already added: date_ID=' + str(same_date.values[0]))
        return same_date.values[0]

    # Save the date with its own ID to local file
    with open('data/date.csv', 'a') as date_csv:
        date_csv.write(str(date_ID) + ';')
        date_csv.write(day + ';')
        date_csv.write(month + ';')
        date_csv.write(year + ';')
        date_csv.write(str(now.weekday()) + ';')
        date_csv.write(date_time[1] + '\n')

    # Console logging
    print('Date [' + date_time[0] + ' ' + date_time[1]
          + '] added: date_ID=' + str(date_ID))

    # Create a log filename from the datetime
    log_filename = day + month + year + "_" \
        + date_time[1][:2] + date_time[1][3:5] + ".log"

    # Return the current date ID
    return [date_ID, log_filename]


# Extract information about the offers from provided card soup.
def add_offers(card_page):
    '''Extract information about the offers from provided card soup.'''
    card_name = card_page.find("h1").string
    table = card_page.find("div", {"class": "table"
                                   + "article-table "
                                   + "table-striped"})
    if table is None:
        print("No offers found on page!")
        print(card_page)
        return

    seller_names = table.findAll("span", {"class": "d-flex"
                                          + "has-content-centered"
                                          + "mr-1"})
    attrs = table.findAll("div", {"class": "product-attributes col"})
    for attr in attrs:
        icons = attr.findAll("span")
        condition = icons[0]["data-original-title"]
        card_lang = icons[1]["data-original-title"]
        other = attrs.find("span", {"class": "icon st_SpecialIcon mr-1"})
        if len(other) > 0:
            if other["data-original-title"] == 'Foil':
                is_foiled = True
            else:
                is_foiled = False
    price = table.findAll("span", {"class": "font-weight-bold color-primary"
                                   + "small text-right text-nowrap"})
    quantity = table.findAll("span", {"class": "item-count small text-right"})
    print('\nCard ' + card_name)
    print('Sellers: ' + len(seller_names))
    print(seller_names)
    print('Condition: ' + condition)
    print('Language: ' + card_lang)
    print('Is foiled: ' + is_foiled)
    input()


# Prepare .csv files for storing the scraped data locally
def prepare_files():
    '''Prepare .csv files for storing the scraped data locally.'''
    if not os.path.exists('data'):
        os.mkdir('data')
        print("Data directory created")

    seller_csv = open('data/seller.csv', 'a+')
    if os.path.getsize('data/seller.csv'):
        pass
    else:
        seller_csv.write('seller_ID;seller_name;type'
                         + ';member_since;country;address\n')
    seller_csv.close()

    card_csv = open('data/card.csv', 'a+')
    if os.path.getsize('data/card.csv'):
        pass
    else:
        card_csv.write('card_ID;card_name;expansion_name;rarity;price_from;'
                       + '30_avg_price;7_avg_price;1_avg_price;available_items'
                       + ';date_ID\n')
    card_csv.close()

    date_csv = open('data/date.csv', 'a+')
    if os.path.getsize('data/date.csv'):
        pass
    else:
        date_csv.write('date_ID;day;month;year;day_of_week;time\n')
    date_csv.close()

    sale_offer_csv = open('data/sale_offer.csv', 'a+')
    if os.path.getsize('data/sale_offer.csv'):
        pass
    else:
        sale_offer_csv.write('seller_ID;price;card_ID;card_condition;'
                             + 'is_foiled;date_ID\n')
    sale_offer_csv.close()

    # Console logging
    print('Local files ready')


# Prepare the local log file.
def prepare_log_file(log_filename):
    '''Prepare the local log file.'''
    if not os.path.exists('logs'):
        os.mkdir('logs')
        print("Logs directory created")

    timestamp = datetime.now().strftime("%H:%M:%S")
    local_log = open('logs/' + log_filename, 'a+')
    if os.path.getsize('logs/' + log_filename):
        local_log.write(timestamp + ": Another run logged to this file")
    else:
        local_log.write(timestamp + ": Created this file")
    local_log.close()

    # Console logging
    print('Log file ready')


# TODO: Send a query to the database
def send_query_seller(conn):
    '''TODO: Send a query to the database.'''
    seller_df = load_df('seller')
    for ID in seller_df.index:
        print(seller_df.iloc[ID])
        break
    # sql_query = "INSERT INTO seller (seller_name, type, country, address)
    # VALUES ('"
    # + names[i].string + "', 0, '" + country[15:] + "')"
    # try:
    #        # Executing the SQL command
    #        cursor.execute(sql
    #        # Commit your changes in the database
    #        conn.commit()
    #    except:
    #        # Rolling back in case of error
    #        conn.rollback()
    input()
    print(seller_df)


# Connect to a local database of given name.
def connect_to_local_db(database_name):
    '''Connect to a local database of given name.'''
    conn = mysql.connector.connect(user='root', password='P@ssword',
                                   host='127.0.0.1', database=database_name)
    cursor = conn.cursor()
    print("Database connection established")
    return conn, cursor


# Log the current url to the console.
def console_log_url(url):
    '''Log the current url to the console.'''
    print("URL change  ->  " + url)


# Return if a seller with the same name is present in the dataframe.
def is_seller_saved(seller_name):
    '''Return if a seller with the same name is present in the dataframe.'''
    seller_df = load_df('seller')
    if seller_name in seller_df['seller_name'].values:
        return True
    return False


# Return whether a card with the same name is saved during this hour.
def is_card_recently_saved(card_name, current_date_ID):
    '''Return whether a card with the same name is saved during this hour.'''
    card_df = load_df('card')
    date_df = load_df('date')
    date_IDs = card_df[(card_df['card_name'] == card_name)]['date_ID'].values
    if len(date_IDs) == 0:
        return False
    this_date = date_df[date_df['date_ID'] == current_date_ID]
    for id in date_IDs:
        card_date = date_df[date_df['date_ID'] == id]
        if this_date['day'].values[0] != card_date['day'].values[0]:
            continue
        if this_date['month'].values[0] != card_date['month'].values[0]:
            continue
        if this_date['year'].values[0] != card_date['year'].values[0]:
            continue
        if this_date['time'].values[0][:2] == card_date['time'].values[0][:2]:
            return True
    return False


# Return a list of all cards found in the expansion cards list.
def get_all_cards(driver, list_url):
    '''Return a list of all cards found in the expansion cards list.'''
    all_cards = []
    page_no = 1
    while True:
        # Separate divs that have card links and names
        driver.get(list_url + '?site=' + str(page_no))
        console_log_url(driver.current_url)
        list_soup = BeautifulSoup(driver.page_source, 'html.parser')
        card_elements = list_soup.findAll("div", {"class": "col-10 "
                                                  + "col-md-8 "
                                                  + "px-2 " + "flex-column "
                                                  + "align-items-start "
                                                  + "justify-content-center"})

        # Check if there are cards on the page
        if len(card_elements) == 0:
            print("Last page reached")
            break

        for card in card_elements:
            # Ignore the table header
            if card.string == 'Name':
                continue

            # Append this card to all cards
            all_cards.append(str(card.string))

        # Advance to the next page
        page_no += 1
        realistic_pause(0.5)

    # Return the complete cards list
    return all_cards


# Deplete the Load More button to have a complete list of card sellers.
def click_load_more_button(driver):
    '''Deplete the Load More button to have a complete list of card sellers.'''
    while True:
        load_more_button = driver \
            .find_element_by_xpath('//button[@id="loadMoreButton"]')
        if load_more_button.text == "":
            break
        driver.execute_script("arguments[0].click();", load_more_button)
        print('Extending the sellers view...')
        realistic_pause(0.5)


# Return a list of all sellers found in a card page.
def get_all_sellers(card_soup):
    '''Return a list of all sellers found in a card page.'''
    names_map = map(lambda x: str(x.find("a").string),
                    card_soup.findAll("span", {"class": "d-flex "
                                      + "has-content-centered " + "mr-1"}))
    return list(names_map)


# Return the name of the card from the url, like 'Spell-Snare'.
def get_card_url(card_name):
    '''Return the name of the card from the url, like 'Spell-Snare'.'''
    card_url_name = card_name.replace("'", "")       # Remove apostrophes
    card_url_name = card_url_name.replace("(", "")
    card_url_name = card_url_name.replace(")", "")   # Remove brackets
    card_url_name = card_url_name.replace("-", "")   # Remove dashes
    card_url_name = card_url_name.replace("/", "")   # Remove slashes
    card_url_name = card_url_name.replace(",", "")   # Remove commas
    card_url_name = card_url_name.replace(".", " ")  # Reduce periods
    card_url_name = card_url_name.replace(" ", "-")  # Change spaces to dashes
    return card_url_name


# Return whether the parsed page contains card info and offers info.
def is_valid_card_page(card_soup):
    '''Return whether the parsed page contains card info and offers info.'''
    card_name = card_soup.find("h1")
    card_info = card_soup.findAll("dd", {"class": "col-6 col-xl-7"})
    table = card_soup.find("div", {"class": "table "
                                   + "article-table "
                                   + "table-striped"})
    print(len(card_info))
    print(type(table))
    # For proper pages the execution ends here
    if len(card_info) > 0 and table is not None:
        return True
    if len(card_info) == 0:
        print("No card info found on page!")
    if table is None:
        print("No offers found on page!")

    # Output for debugging
    if card_name is not None:
        print("Card name: " + str(card_name.string))
    return False


# Log a message to a local file corresponding to a single run.
def local_log(msg, log_filename):
    '''Log a message to a local file corresponding to a single run.'''
    with open('logs/' + log_filename, 'a') as logfile:
        timestamp = datetime.now.strftime("%H:%M:%S")
        logfile.write(timestamp + ": " + msg)


# Main function
if __name__ == "__main__":

    # Setup
    prepare_files()
    [current_date_ID, log_filename] = add_date()
    prepare_log_file(log_filename)
    base_url = 'https://www.cardmarket.com/en/Magic/Products/Singles/'
    users_url = 'https://www.cardmarket.com/en/Magic/Users/'
    expansion_name = 'Battlebond'
    driver = create_webdriver()
    conn, cursor = connect_to_local_db('gathering')
    cached_pages = []

    # Loop over every card name
    card_list = get_all_cards(driver, base_url + expansion_name)
    for card_name in card_list:

        # Craft the card url and open it with the driver
        card_url_name = get_card_url(card_name)
        card_url = base_url + expansion_name + '/' + card_url_name
        driver.get(card_url)
        console_log_url(driver.current_url)
        realistic_pause(1.0)

        # Add the parsed page content to the list for later use
        card_soup = BeautifulSoup(driver.page_source, 'html.parser')
        if is_valid_card_page(card_soup):
            cached_pages.append(card_soup)
        else:
            print('No valid card page under ' + driver.current_url)
            input()
        continue

        # Check if a recent record already exists
        if is_card_recently_saved(card_name, current_date_ID):
            print('Card ' + card_name + ' already in the file')
        else:
            add_card(card_soup, current_date_ID)

        # Get all sellers from the card page
        sellers = get_all_sellers(card_soup)
        for seller_name in sellers:

            # Check if a recent record already exists
            if is_seller_saved(seller_name):
                print('Seller ' + seller_name + ' already in the file')
            else:
                driver.get(users_url + seller_name)
                seller_soup = BeautifulSoup(driver.page_source, 'html.parser')
                add_seller(seller_soup)
                realistic_pause(2.0)

    # Iterate through saved card pages for offers data
    for card_page in cached_pages:
        add_offers(card_page)

    # Close the webdriver
    driver.close()
    print("Webdriver closed")

    # Close the connection to the database
    conn.close()
    print("Database connection closed")
