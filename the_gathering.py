"""Scrape the card market website to get all the neccessary data."""
import os
import keyboard
from time import sleep
from datetime import datetime
from random import normalvariate, random, randint
import pandas as pd
import mysql.connector
from bs4 import BeautifulSoup
from selenium import webdriver, common
from selenium.webdriver.firefox.options import Options

# Global variables for user custom configuration
max_wait = 3.0
silent_mode = True

# Global variables connected to this run of the code.
log_filename = 'dump.log'
current_date_ID = 0

# Global fixed variables
base_url = 'https://www.cardmarket.com/en/Magic/Products/Singles/'
users_url = 'https://www.cardmarket.com/en/Magic/Users/'


# Wait about mean_val seconds before proceeding to the rest of the code.
def realistic_pause(mean_val):
    '''Wait ~mean_val seconds before proceeding to the rest of the code.'''
    std_val = mean_val * random() * 0.25 + 0.05
    sleep_time = abs(normalvariate(mean_val, std_val)) + 0.15
    if not silent_mode:
        log(f'Sleeping for {round(sleep_time, 3)} seconds')
    sleep(sleep_time)


# Return the Firefox webdriver in headless mode.
def create_webdriver():
    '''Return the Firefox webdriver in headless mode.'''
    if not silent_mode:
        log('Opening the webdriver')
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    log('Webdriver ready')
    return driver


# Return the Firefox webdriver in headless mode.
def restart_webdriver(driver):
    '''Return the Firefox webdriver in headless mode.'''
    log('Restarting the webdriver')
    driver.close()
    log('Closing the webdriver')
    realistic_pause(0.3 * max_wait)
    driver = create_webdriver()
    return driver


# Try to load a .csv file content into a dataframe.
def load_df(entity_name):
    '''Try to return a dataframe from the respective .csv file.'''
    try:
        df = pd.read_csv('data/' + entity_name + '.csv', sep=';')
        if not silent_mode:
            log('[read ' + entity_name + ']')
    except pd.errors.EmptyDataError as empty:
        log(str(empty))
        log(f'Please prepare the headers in {entity_name}.csv!\n')
    except pd.errors.ParserError as wrong_data:
        log(str(wrong_data))
        log(f'Please check the correctness of data in {entity_name}.csv!\n')
    return df


# Extract information about a card from provided soup.
def add_card(card_soup):
    '''Extract information about a card from provided soup.'''

    # Load the card and date dataframes
    card_df = load_df('card')

    # Get rows from the card information table
    card_info = card_soup.findAll("dd", {"class": "col-6 col-xl-7"})
    if len(card_info) == 0:
        if not silent_mode:
            log('No card info found on current page')
        return

    # Get the attributes
    avg_1_price = card_info[-1].string.string[:-2].replace(',', '.')
    avg_7_price = card_info[-2].string.string[:-2].replace(',', '.')
    avg_30_price = card_info[-3].string.string[:-2].replace(',', '.')
    price_from = card_info[-5].string[:-2].replace(',', '.')
    available_items = card_info[-6].string
    rarity = card_info[0].find('span')['data-original-title']
    expansion_name = card_info[1].find('span')['data-original-title']
    card_name = str(card_soup.find("h1")).split('<')[1][3:]
    card_ID = len(card_df.index) + 1

    # Logging
    if not silent_mode:
        log('== Add card ==')
        log('Card: \t\t\t' + str(card_name))
        log('Card ID: \t\t' + str(card_ID))
        log('Expansion: \t' + str(expansion_name))
        log('Rarity: \t\t\t' + str(rarity))
        log('Price from: \t\t' + str(price_from))
        log('30-day avg: \t\t' + str(avg_30_price))
        log('7-day avg: \t\t' + str(avg_7_price))
        log('1-day avg: \t\t' + str(avg_1_price))
        log('Amount: \t\t' + str(available_items))
        log('Date ID: \t\t' + str(current_date_ID))
        keyboard.read_key()

    # Save the card in local file
    with open('data/card.csv', 'a', encoding="utf-8") as card_csv:
        if not silent_mode:
            log('[write card]' + '\n')
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


# Extract information about a seller from provided soup.
def add_seller(seller_soup):
    '''Extract information about a seller from provided soup.'''

    # Get rows from the seller information table on page
    seller_name = seller_soup.find("h1")

    # User not loaded correctly
    if seller_name is None:
        realistic_pause(0.7*max_wait)
        log('Seller dropped!')
        log(f'Bad page soup dumped to logs/soups/{log_soup(seller_soup)}.log'
            + '\n')
        realistic_pause(0.7*max_wait)
        return

    # Seller name
    seller_name = str(seller_name.string)

    # Log
    log('Extracting seller info: ' + seller_name)
    realistic_pause(0.8*max_wait)

    # Seller ID
    seller_df = load_df('seller')
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

    # Logging
    if not silent_mode:
        log('== Add seller ==')
        log('Seller: \t\t\t' + str(seller_name))
        log('Seller ID: \t\t' + str(seller_ID))
        log('Type: \t\t\t' + str(s_type))
        log('Member since: \t' + str(member_since))
        log('Country: \t\t\t' + str(country))
        log('Address: \t\t\t' + str(address))
        log('Date ID: \t\t\t' + str(current_date_ID))
        # keyboard.readkey()

    # Save the seller in local file
    with open('data/seller.csv', 'a', encoding="utf-8") as seller_csv:
        if not silent_mode:
            log('[write seller]' + '\n')
        seller_csv.write(str(seller_ID) + ';')
        seller_csv.write(seller_name + ';')
        seller_csv.write(s_type + ';')
        seller_csv.write(member_since + ';')
        seller_csv.write(country + ';')
        seller_csv.write(address + '\n')


# Add the current date, return the date ID and its log file name.
def add_date():
    '''Add the current date, return the date ID and its log file name.'''

    # Load the date dataframe
    date_df = load_df('date')

    # Prepare the attributes
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y %H").split(" ")
    day = date_time[0].split("/")[0]
    month = date_time[0].split("/")[1]
    year = date_time[0].split("/")[2]
    hour = date_time[1]
    date_ID = len(date_df.index) + 1

    # Create a log filename from the datetime
    global log_filename
    log_filename = day + month + year + "_" + hour
    if not silent_mode:
        log_filename += "_verbose"
    log_filename += ".log"
    prepare_log_files()

    # Check for the same datetime record
    same_date = date_df[(date_df['day'] == int(day))
                        & (date_df['month'] == int(month))
                        & (date_df['year'] == int(year))
                        & (date_df['hour'] == int(hour))]['date_ID']
    if(len(same_date) > 0):
        print(f'Date [{date_time[0]} {date_time[1]}] '
              + f'already added (date_ID: {same_date.values[0]})')
        return same_date.values[0]

    # Save the date with its own ID to local file
    with open('data/date.csv', 'a', encoding="utf-8") as date_csv:
        if not silent_mode:
            log('[write date]')
        date_csv.write(str(date_ID) + ';')
        date_csv.write(day + ';')
        date_csv.write(month + ';')
        date_csv.write(year + ';')
        date_csv.write(str(now.weekday()) + ';')
        date_csv.write(hour + '\n')

    # Logging
    log('== Add date ==')
    log('Date: \t\t\t' + str(date_time[0]))
    log('Hour: \t\t\t' + str(hour))
    log('Date ID: \t\t\t' + str(date_ID))
    if not silent_mode:
        log('Log file name: \t' + str(log_filename))
    keyboard.read_key()
    # input()

    # Return the current date ID
    return date_ID


# Return a seller ID given its name.
def get_seller_ID(seller_name):
    '''Return a seller ID given its name.'''
    seller_df = load_df('seller')
    this_seller = seller_df[(seller_df['seller_name'] == card_name)]
    if len(this_seller) == 0:
        return -1
    return this_seller['seller_ID'].values[0]


# Return a session-valid card ID given its name.
def get_card_ID(card_name):
    '''Return a session-valid card ID given its name.'''
    card_df = load_df('card')
    this_card = card_df[(card_df['card_name'] == card_name)
                        & (card_df['date_ID'] == current_date_ID)]
    if len(this_card) == 0:
        return -1
    return this_card['card_ID'].values[0]


# Extract information about the offers from provided card soup.
def add_offers(card_page):
    '''Extract information about the offers from provided card soup.'''
    table = card_page.find("div", {"class": "table "
                                   + "article-table "
                                   + "table-striped"})
    if table is None:
        if not silent_mode:
            log("No offers found on page!")
            log(card_page.find("title"))
        return

    # Get static and list info from the page
    card_name = (str(card_page.find("div", {"class": "flex-grow-1"}))
                 .split(">")[2]).split("<")[0]
    seller_names = table.findAll("span", {"class": "d-flex "
                                          + "has-content-centered "
                                          + "mr-1"})
    prices = table.findAll("span", {"class": "font-weight-bold color-primary "
                                    + "small text-right text-nowrap"})
    amounts = table.findAll("span", {"class":
                            "item-count small text-right"})
    attributes = table.findAll("div", {"class": "product-attributes col"})

    # Ensure the table has proper content
    if not (len(prices) / 2) == len(amounts) \
            == len(seller_names) == len(attributes):
        log('The attributes columns don\'t match in size!\n')
        return

    # Acquire the data row by row
    for i in range(len(seller_names)):
        offer_attrs = []
        price = str(prices[2*i].string)[:-2].replace(".", "") \
            .replace(",", ".")
        amount = amounts[i].string
        seller_name = seller_names[i].string

        # Get card attributes
        for attr in attributes[i].findAll("span"):
            if attr is None:
                if not silent_mode:
                    log("Empty attribute!\n" + str(card_name)
                        + " by " + seller_name + " for " + price)
            else:
                offer_attrs.append(attr["data-original-title"])
            is_foiled = False
            other = attr.find("span", {"class": "icon st_SpecialIcon mr-1"})
            if other is not None:
                if other["data-original-title"] == 'Foil':
                    is_foiled = True

        # Interpret the attributes
        if len(offer_attrs) >= 2:
            condition = offer_attrs[0]
            card_lang = offer_attrs[1]
        else:
            condition = 'NaN'
            card_lang = 'NaN'
            log("A card in a sale offer has incomplete attributes"
                + "(language, condition)")

        # Get dependent values
        seller_ID = get_seller_ID(seller_name)
        card_ID = get_card_ID(card_name)

        # Determine whether the same offer is already saved
        sale_offer_df = load_df('sale_offer')
        offers = sale_offer_df[(sale_offer_df['seller_ID'] == seller_ID)
                               & (sale_offer_df['card_ID'] == card_ID)
                               & (sale_offer_df['price'] == price)
                               & (sale_offer_df['card_condition'] == condition)
                               & (sale_offer_df['language'] == card_lang)
                               & (sale_offer_df['is_foiled'] == is_foiled)
                               & (sale_offer_df['amount'] == amount)
                               & (sale_offer_df['date_ID'] == current_date_ID)]
        # If there are matching offers, don't add this one
        if len(offers) > 0:
            if not silent_mode:
                log(f"Already saved transaction  ({seller_ID} -> {card_ID}"
                    + f" for {price}")
            continue

        # Logging
        if not silent_mode:
            log('== Add sale offer ==')
            log('Seller: \t\t\t' + str(seller_name))
            log('Seller ID: \t\t' + str(seller_ID))
            log('Price: \t\t\t' + str(price))
            log('Card: \t\t\t' + str(card_name))
            log('Card ID: \t\t\t' + str(card_ID))
            log('Condition: \t\t' + str(condition))
            log('Language: \t\t' + str(card_lang))
            log('Is foiled: \t\t' + str(is_foiled))
            log('Amount: \t\t\t' + str(amount))
            log('Date ID: \t\t\t' + str(current_date_ID))
            # keyboard.read_key()

        # Save the seller in local file
        with open('data/sale_offer.csv', 'a', encoding="utf-8") as offers_csv:
            if not silent_mode:
                log('[write sale offer]' + '\n')
            offers_csv.write(str(seller_name) + ';')
            offers_csv.write(str(price) + ';')
            offers_csv.write(str(card_name) + ';')
            offers_csv.write(str(condition) + ';')
            offers_csv.write(str(card_lang) + ';')
            offers_csv.write(str(is_foiled) + ';')
            offers_csv.write(str(amount) + ';')
            offers_csv.write(str(current_date_ID) + '\n')


# Prepare .csv files for storing the scraped data locally
def prepare_files():
    '''Prepare .csv files for storing the scraped data locally.'''
    if not os.path.exists('data'):
        os.mkdir('data')
        print("Data directory created")

    seller_csv = open('data/seller.csv', 'a+', encoding="utf-8")
    if os.path.getsize('data/seller.csv'):
        pass
    else:
        seller_csv.write('seller_ID;seller_name;type'
                         + ';member_since;country;address\n')
    seller_csv.close()

    card_csv = open('data/card.csv', 'a+', encoding="utf-8")
    if os.path.getsize('data/card.csv'):
        pass
    else:
        card_csv.write('card_ID;card_name;expansion_name;rarity;price_from;'
                       + '30_avg_price;7_avg_price;1_avg_price;available_items'
                       + ';date_ID\n')
    card_csv.close()

    date_csv = open('data/date.csv', 'a+', encoding="utf-8")
    if os.path.getsize('data/date.csv'):
        pass
    else:
        date_csv.write('date_ID;day;month;year;day_of_week;hour\n')
    date_csv.close()

    sale_offer_csv = open('data/sale_offer.csv', 'a+', encoding="utf-8")
    if os.path.getsize('data/sale_offer.csv'):
        pass
    else:
        sale_offer_csv.write('seller_ID;price;card_ID;card_condition;'
                             + 'language;is_foiled;amount;date_ID\n')
    sale_offer_csv.close()

    # Console logging
    print('Local files ready')


# Prepare the local log files.
def prepare_log_files():
    '''Prepare the local log files.'''
    if not os.path.exists('logs'):
        os.mkdir('logs')
        print("Logs directory created")
    if not os.path.exists('logs/soups'):
        os.mkdir('logs/soups')
        print("Soups directory created")

    logfile = open('logs/' + log_filename, "a+", encoding="utf-8")
    if os.path.getsize('logs/' + log_filename):
        log("=== Another run of the code ===")
    else:
        log("=== Creation of this file ===")
    logfile.close()


# Prepare the expansion cards list file.
def prepare_expansion_list_file(expansion_name):
    '''Prepare the expansion cards list file.'''
    exp_filename = urlify(expansion_name)
    exp_file = open('data/' + exp_filename + '.txt', 'a+', encoding="utf-8")
    exp_file.close()


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
    log("Database connection established\n")
    return conn, cursor


# Log the current url to the console and log file.
def log_url(url):
    '''Log the current url to the console and log file.'''
    log("URL change  ->  " + url)


# Return if a seller with the same name is present in the dataframe.
def is_seller_saved(seller_name):
    '''Return if a seller with the same name is present in the dataframe.'''
    seller_df = load_df('seller')
    if seller_name in seller_df['seller_name'].values:
        return True
    return False


# Return whether a card with the same name is saved during this hour.
def is_card_recently_saved(card_name):
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
        if this_date['hour'].values[0] == card_date['hour'].values[0]:
            log(f'Card {card_name} saved recently ('
                + str(card_date['hour'].values[0]) + ')')
            return True
    return False


# Return the number of cards in the search results.
def get_card_hits(list_soup):
    '''Return the number of cards in the search results.'''
    hits_div = list_soup.find("div", {"class": "row my-3 "
                                      + "align-items-center"})
    hits_str = str(hits_div.find("div", {"class": "col-auto "
                                         + "d-none d-md-block"}))
    return int(hits_str.split(">")[1].split(" ")[0])


# Return a list of all cards found in the expansion cards list.
def get_card_names(driver, expansion_name):
    '''Return a list of all cards found in the expansion cards list.'''
    # Load the number of cards stored in a local file
    exp_filename = urlify(expansion_name)
    exp_file = open('data/' + exp_filename + '.txt', 'r', encoding="utf-8")
    saved_cards = exp_file.read().split('\n')[:-1]
    exp_file.close()
    log("Task - Compiling a list of all card names in current expansion")

    all_cards = []
    page_no = 1
    while True:
        # Separate divs that have card links and names
        driver.get(base_url + expansion_name + '?site=' + str(page_no))
        log_url(driver.current_url)
        list_soup = BeautifulSoup(driver.page_source, 'html.parser')
        card_elements = list_soup.findAll("div", {"class": "col-10 col-md-8 "
                                                  + "px-2 flex-column "
                                                  + "align-items-start "
                                                  + "justify-content-center"})

        # Check if there are cards on the page
        if len(card_elements) == 0:
            log("Last page reached")
            break

        # Check if there is a saved complete list of cards from this expansion
        if get_card_hits(list_soup) == len(saved_cards):
            log(f"Done - Card names from {expansion_name} are already saved\n")
            return saved_cards

        for card in card_elements:
            # Ignore the table header
            if card.string == 'Name':
                continue

            # Append this card's name to all cards
            all_cards.append(str(card.string))

        # Advance to the next page
        page_no += 1
        realistic_pause(0.2*max_wait)

    # Save the complete cards list to a file
    exp_file = open('data/' + exp_filename + '.txt', 'w', encoding="utf-8")
    for card_name in all_cards:
        exp_file.write(card_name + '\n')
    exp_file.close()

    # Return the complete cards list
    return all_cards


# Deplete the Load More button to have a complete list of card sellers.
def click_load_more_button(driver):
    '''Deplete the Load More button to have a complete list of card sellers.'''
    try:
        while True:
            load_more_button = driver \
                .find_element_by_xpath('//button[@id="loadMoreButton"]')
            if load_more_button.text == "":
                break
            driver.execute_script("arguments[0].click();", load_more_button)
            if not silent_mode:
                log('Extending the sellers view...')
            realistic_pause(0.2*max_wait)
    except common.exceptions.NoSuchElementException:
        if not silent_mode:
            log(f"No button found on page {driver.current_url}")


# Return a list of all sellers found in a card page.
def get_seller_names(card_soup):
    '''Return a list of all sellers found in a card page.'''
    names_map = map(lambda x: str(x.find("a").string),
                    card_soup.findAll("span", {"class": "d-flex "
                                      + "has-content-centered " + "mr-1"}))
    return list(names_map)


# Return the given string in url-compatible form, like 'Spell-Snare'.
def urlify(name):
    '''Return the given string in url-compatible form, like 'Spell-Snare'.'''
    url_name = name.replace("'", "")       # Remove apostrophes
    url_name = url_name.replace("(", "")
    url_name = url_name.replace(")", "")   # Remove brackets
    url_name = url_name.replace("-", "")   # Remove dashes
    url_name = url_name.replace("/", "")   # Remove slashes
    url_name = url_name.replace(",", "")   # Remove commas
    url_name = url_name.replace(".", " ")  # Reduce periods
    url_name = url_name.replace(" ", "-")  # Change spaces to dashes
    return url_name


# Return whether the parsed page contains card info and offers info.
def is_valid_card_page(card_soup):
    '''Return whether the parsed page contains card info and offers info.'''
    card_name = card_soup.find("h1")
    card_info = card_soup.findAll("dd", {"class": "col-6 col-xl-7"})
    table = card_soup.find("div", {"class": "table "
                                   + "article-table "
                                   + "table-striped"})
    # For proper pages the execution ends here
    if len(card_info) > 0 and table is not None:
        return True
    if len(card_info) == 0:
        if not silent_mode:
            log("No card info found on page!")
    if table is None:
        if not silent_mode:
            log("No offers found on page!")

    # Output for debugging
    if card_name is not None:
        if not silent_mode:
            log("Card name: " + str(card_name.string) + "\n")
    return False


# Log a message to a local file and the console.
def log(msg):
    '''Log a message to a local file and the console.'''
    msg = str(msg)
    with open('logs/' + log_filename, 'a', encoding="utf-8") as logfile:
        timestamp = datetime.now().strftime("%H:%M:%S")
        logfile.write(timestamp + ": " + msg + "\n")
    print(msg)


# Log a soup to a separate file for inspection.
def log_soup(soup):
    '''Log a soup to a separate file for inspection.'''
    # Chose available soup identification number and create a filename
    soup_names = os.listdir('logs/soups')
    print(soup_names)  # Debug
    while True:
        soup_id = randint(100000, 999999)
        filename = str(soup_id) + '.log'
        if filename not in soup_names:
            break

    # Create a file and dump the soup inside
    with open('logs/soups/' + filename, 'w+', encoding="utf-8") as soup_file:
        soup_file.write(str(soup))

    # Return the soup identification number for diagnostic purposes
    return soup_id


# Wait for specified amount of seconds and return exp times the amount.
def exponential_wait(wait_time, exponent):
    '''Wait for specified amount of seconds and return exp times the amount.'''
    realistic_pause(wait_time)
    return exponent * wait_time


# TODO: Add progress
# Main function
if __name__ == "__main__":

    # Setup
    prepare_files()
    current_date_ID = add_date()
    expansion_name = 'Battlebond'
    prepare_expansion_list_file(expansion_name)
    driver = create_webdriver()
    conn, cursor = connect_to_local_db('gathering')

    # Loop over every card name
    card_list = get_card_names(driver, expansion_name)
    for card_name in card_list:

        while True:
            # Craft the card url and open it with the driver
            card_url_name = urlify(card_name)
            card_url = base_url + expansion_name + '/' + card_url_name
            driver.get(card_url)
            log_url(driver.current_url)
            realistic_pause(0.6*max_wait)
            log("                Expanding page...")
            click_load_more_button(driver)

            # Add the parsed page content to the list for later use
            card_soup = BeautifulSoup(driver.page_source, 'html.parser')
            wait_time = 20
            if is_valid_card_page(card_soup):
                break
            else:
                log('Card page invalid: ' + driver.current_url)
                wait_time = exponential_wait(wait_time, 1.5)
                if wait_time > 60:
                    driver = restart_webdriver(driver)

        # Check if a recent record already exists
        if not is_card_recently_saved(card_name):
            add_card(card_soup)

        # Get all sellers from the card page
        log("Task - Updating sellers list")
        sellers = get_seller_names(card_soup)
        for seller_name in sellers:

            # Check if a recent record already exists
            if is_seller_saved(seller_name):
                if not silent_mode:
                    log('Already saved: ' + seller_name + '\n')
            else:
                driver.get(users_url + seller_name)
                seller_soup = BeautifulSoup(driver.page_source, 'html.parser')
                add_seller(seller_soup)

        # Logging
        log(f"Done - All sellers of card {card_name} saved")

        # Get all sale offers from the page
        add_offers(card_soup)

    # Close the webdriver
    driver.close()
    print("Webdriver closed")

    # Close the connection to the database
    conn.close()
    print("Database connection closed")
