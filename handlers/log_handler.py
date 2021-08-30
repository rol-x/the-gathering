"""Scrape the card market website to get all the neccessary data."""
import os
from datetime import datetime
from random import randint

import globals


# Log a soup to a separate file for inspection.
def log_soup(soup):
    '''Log a soup to a separate file for inspection.'''
    # Chose available soup identification number and create a filename
    soup_names = os.listdir('logs/soups')
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


# Log the current url to the console and log file.
def log_url(url):
    '''Log the current url to the console and log file.'''
    log("URL change  ->  " + url)


# Log a message to a local file and the console.
def log(msg):
    '''Log a message to a local file and the console.'''
    msg = str(msg)
    with open('logs/' + globals.log_filename, 'a', encoding="utf-8") \
            as logfile:
        timestamp = datetime.now().strftime("%H:%M:%S")
        logfile.write(timestamp + ": " + msg + "\n")
    print(msg)
