"""Manage the local files with data stored in .csv format."""
import os

import globals
import pandas as pd

from handlers.log_handler import log


# Try to load a .csv file content into a dataframe.
def load_df(entity_name):
    '''Try to return a dataframe from the respective .csv file.'''
    try:
        df = pd.read_csv('data/' + entity_name + '.csv', sep=';')
    except pd.errors.EmptyDataError as empty:
        log(str(empty))
        log(f'Please prepare the headers in {entity_name}.csv!\n')
    except pd.errors.ParserError as wrong_data:
        log(str(wrong_data))
        log(f'Please check the correctness of data in {entity_name}.csv!\n')
    return df


# Return the number of rows of a specified dataframe.
def get_size(entity_name):
    '''Return the number of rows of a specified dataframe.'''
    entity_df = load_df(entity_name)
    return len(entity_df.index)


# Prepare .csv files for storing the scraped data locally
def prepare_files():
    '''Prepare .csv files for storing the scraped data locally.'''
    if not os.path.exists('data'):
        os.mkdir('data')
        print("Data directory created")

    seller_csv = open('data/seller.csv', 'a+', encoding="utf-8")
    if not os.path.getsize('data/seller.csv'):
        seller_csv.write('seller_ID;seller_name;seller_type'
                         + ';member_since;country;address\n')
    seller_csv.close()

    card_csv = open('data/card.csv', 'a+', encoding="utf-8")
    if not os.path.getsize('data/card.csv'):
        card_csv.write('card_ID;card_name;expansion_name;rarity\n')
    card_csv.close()

    card_stats_csv = open('data/card_stats.csv', 'a+', encoding="utf-8")
    if not os.path.getsize('data/card_stats.csv'):
        card_stats_csv.write('card_ID;price_from;30_avg_price;7_avg_price;'
                             + '1_avg_price;available_items;date_ID\n')
    card_stats_csv.close()

    date_csv = open('data/date.csv', 'a+', encoding="utf-8")
    if not os.path.getsize('data/date.csv'):
        date_csv.write('date_ID;day;month;year;day_of_week\n')
    date_csv.close()

    sale_offer_csv = open('data/sale_offer.csv', 'a+', encoding="utf-8")
    if not os.path.getsize('data/sale_offer.csv'):
        sale_offer_csv.write('seller_ID;price;card_ID;card_condition;'
                             + 'language;is_foiled;amount;date_ID\n')
    sale_offer_csv.close()

    # Console logging
    print('Local files ready')


# Prepare the expansion cards list file.
def prepare_expansion_list_file(exp_filename):
    '''Prepare the expansion cards list file.'''
    exp_file = open('data/' + exp_filename + '.txt', 'a+', encoding="utf-8")
    exp_file.close()
