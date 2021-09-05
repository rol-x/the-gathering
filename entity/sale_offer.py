import globals
import numpy as np
import pandas as pd
from handlers.local_files_handler import load_df
from handlers.log_handler import log

from entity.card import get_card_ID
from entity.seller import get_seller_ID


# Extract information about the offers from provided card soup.
def add_offers(card_page):
    '''Extract information about the offers from provided card soup.'''
    table = card_page.find("div", {"class": "table "
                                   + "article-table "
                                   + "table-striped"})
    if table is None:
        if globals.verbose_mode:
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

    # Get the card ID (dependent on card_name and current_date_ID)
    card_ID = get_card_ID(card_name)

    # Ensure the table has proper content
    if not (len(prices) / 2) == len(amounts) \
            == len(seller_names) == len(attributes):
        log('The columns don\'t match in size!\n')
        return

    # Acquire the data row by row
    offers_dict = {"seller_ID": [], "price": [], "card_ID": [],
                   "card_condition": [], "language": [], "is_foiled": [],
                   "amount": [], "date_ID": []}
    for i in range(len(seller_names)):
        offer_attrs = []
        price = float(str(prices[2*i].string)[:-2].replace(".", "")
                      .replace(",", "."))
        amount = int(amounts[i].string)
        seller_name = seller_names[i].string

        # Get card attributes
        for attr in attributes[i].findAll("span"):
            if attr is None:
                if globals.verbose_mode:
                    log("Empty attribute!\n" + str(card_name)
                        + " by " + seller_name + " for " + price)
            else:
                offer_attrs.append(attr["data-original-title"])
            is_foiled = False
            foil = attributes[i].find("span", {"class":
                                               "icon st_SpecialIcon mr-1"})
            if foil is not None:
                if foil["data-original-title"] == 'Foil':
                    is_foiled = True

        # Interpret the attributes
        if len(offer_attrs) >= 2:
            condition = offer_attrs[0]
            card_lang = offer_attrs[1]
        else:
            condition = np.nan
            card_lang = np.nan
            log("A card in a sale offer has incomplete attributes"
                + "(language, condition)")

        # Load the entry into the dictionary
        seller_ID = get_seller_ID(seller_name)
        offers_dict['seller_ID'].append(seller_ID)
        offers_dict['price'].append(price)
        offers_dict['card_ID'].append(card_ID)
        offers_dict['card_condition'].append(condition)
        offers_dict['language'].append(card_lang)
        offers_dict['is_foiled'].append(is_foiled)
        offers_dict['amount'].append(amount)
        offers_dict['date_ID'].append(globals.current_date_ID)

    update_offers(offers_dict)


# Save a single offer row to the offer dataframe in .csv file.
def save_offer(seller_ID, price, card_ID, condition,
               card_lang, is_foiled, amount):
    '''Save a single card row to the card dataframe in .csv file.'''

    # Logging
    if globals.verbose_mode:
        log('== Add sale offer ==')
        log('Seller ID:     ' + str(seller_ID))
        log('Price:         ' + str(price))
        log('Card ID:       ' + str(card_ID))
        log('Condition:     ' + condition)
        log('Language:      ' + card_lang)
        log('Is foiled:     ' + str(is_foiled))
        log('Amount:        ' + str(amount))
        log('Date ID:       ' + str(globals.current_date_ID) + '\n')

    # Writing
    with open('data/sale_offer.csv', 'a', encoding="utf-8") as offers_csv:
        if globals.verbose_mode:
            log('[write sale offer]' + '\n')
        offers_csv.write(str(seller_ID) + ';')
        offers_csv.write(str(price) + ';')
        offers_csv.write(str(card_ID) + ';')
        offers_csv.write(condition + ';')
        offers_csv.write(card_lang + ';')
        offers_csv.write(str(is_foiled) + ';')
        offers_csv.write(str(amount) + ';')
        offers_csv.write(str(globals.current_date_ID) + '\n')


# Take new offers after comparing to saved ones and update the file.
def update_offers(offers_dict):
    '''Take new offers after comparing to saved ones and update the file.'''
    # Load and compare the local data
    current_offers_df = load_df('sale_offer')
    num_of_offers_before = len(current_offers_df.index)
    read_offers_df = pd.DataFrame(offers_dict)
    num_of_new_offers = 0

    # Save the new sale offers in a local file
    for i in read_offers_df.index:
        if not is_sale_offer_saved_today(read_offers_df.loc[i]):
            save_offer(read_offers_df.loc[i]['seller_ID'],
                       read_offers_df.loc[i]['price'],
                       read_offers_df.loc[i]['card_ID'],
                       read_offers_df.loc[i]['card_condition'],
                       read_offers_df.loc[i]['language'],
                       read_offers_df.loc[i]['is_foiled'],
                       read_offers_df.loc[i]['amount'])
            num_of_new_offers += 1

    # Decide on requesting speed
    if num_of_new_offers == 0:
        globals.speed_up()
    else:
        globals.wait_coef = 1.0

    # Log task finished
    log(f"Done - {num_of_new_offers} new offers added "
        + f" (out of: {len(read_offers_df)}, "
        + f"total: {num_of_offers_before + num_of_new_offers})\n")


# Return whether the provided sale offer is already saved.
def is_sale_offer_saved_today(df_row):
    '''Return whether the provided sale offer is already saved.'''
    seller_ID = df_row['seller_ID']
    price = df_row['price']
    card_ID = df_row['card_ID']
    card_condition = df_row['card_condition']
    language = df_row['language']
    is_foiled = df_row['is_foiled']
    amount = df_row['amount']

    sale_offers_df = load_df('sale_offer')
    sm = sale_offers_df[(sale_offers_df['seller_ID'] == seller_ID) &
                        (sale_offers_df['price'] == price) &
                        (sale_offers_df['card_ID'] == card_ID) &
                        (sale_offers_df['card_condition'] == card_condition) &
                        (sale_offers_df['language'] == language) &
                        (sale_offers_df['is_foiled'] == is_foiled) &
                        (sale_offers_df['amount'] == amount) &
                        (sale_offers_df['date_ID'] == globals.current_date_ID)]
    if len(sm) > 0:
        return True
    return False
