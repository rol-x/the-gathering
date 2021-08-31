from random import normalvariate, random
from time import sleep, time

import globals
from bs4 import BeautifulSoup
from selenium import common, webdriver
from selenium.webdriver.firefox.options import Options

from handlers.log_handler import log, log_url


# Return the Firefox webdriver in headless mode.
def create_webdriver():
    '''Return the Firefox webdriver in headless mode.'''
    if globals.verbose_mode:
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
    realistic_pause(0.3*globals.max_wait*globals.wait_coef)
    driver = create_webdriver()
    return driver


# Return a list of all cards found in the expansion cards list.
def get_card_names(driver, expansion_name):
    '''Return a list of all cards found in the expansion cards list.'''
    # Load the number of cards stored in a local file
    exp_filename = urlify(expansion_name)
    exp_file = open('data/' + exp_filename + '.txt', 'r', encoding="utf-8")
    saved_cards = exp_file.read().split('\n')[:-1]
    exp_file.close()
    log("Task - Getting all card names from current expansion")

    all_cards = []
    page_no = 1
    while True:
        # Separate divs that have card links and names
        driver.get(globals.base_url + expansion_name + '?site=' + str(page_no))
        log_url(driver.current_url)
        list_soup = BeautifulSoup(driver.page_source, 'html.parser')
        card_elements = list_soup.findAll("div", {"class": "col-10 col-md-8 "
                                                  + "px-2 flex-column "
                                                  + "align-items-start "
                                                  + "justify-content-center"})

        # Check if there are cards on the page
        if len(card_elements) == 0:
            log("Last page reached\n")
            break

        # Check if there is a saved complete list of cards from this expansion
        if get_card_hits(list_soup) == len(saved_cards):
            log(f"Done - All card names from {expansion_name} saved\n")
            return saved_cards

        for card in card_elements:
            # Ignore the table header
            if card.string == 'Name':
                continue

            # Append this card's name to all cards
            all_cards.append(str(card.string))

        # Advance to the next page
        page_no += 1
        realistic_pause(0.2*globals.max_wait*globals.wait_coef)

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
        start_t = time()
        while True:
            load_more_button = driver \
                .find_element_by_xpath('//button[@id="loadMoreButton"]')
            if load_more_button.text == "":
                break
            driver.execute_script("arguments[0].click();", load_more_button)
            if globals.verbose_mode:
                log('Extending the sellers view...')
            realistic_pause(0.2*globals.max_wait*globals.wait_coef)
            elapsed_t = time() - start_t
            if elapsed_t > 60.0:
                log("Extending the sellers view timed out.")
                break
    except common.exceptions.NoSuchElementException:
        log("No button found on this page.")


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
        if globals.verbose_mode:
            log("No card info found on page!")
    if table is None:
        if globals.verbose_mode:
            log("No offers found on page!")

    # Output for debugging
    if card_name is not None:
        if globals.verbose_mode:
            log("Card name: " + str(card_name.string) + "\n")
    return False


# Wait about mean_val seconds before proceeding to the rest of the code.
def realistic_pause(mean_val):
    '''Wait ~mean_val seconds before proceeding to the rest of the code.'''
    std_val = mean_val * random() * 0.25 + 0.05
    sleep_time = abs(normalvariate(mean_val, std_val)) + 0.15
    if globals.verbose_mode:
        log(f'Sleeping for {round(sleep_time, 3)} seconds')
    sleep(sleep_time)


# Wait for specified amount of seconds and return exp times the amount.
def exponential_wait(wait_time, exponent):
    '''Wait for specified amount of seconds and return exp times the amount.'''
    realistic_pause(wait_time)
    return exponent * wait_time


# Return the number of cards in the search results.
def get_card_hits(list_soup):
    '''Return the number of cards in the search results.'''
    hits_div = list_soup.find("div", {"class": "row my-3 "
                                      + "align-items-center"})
    hits_str = str(hits_div.find("div", {"class": "col-auto "
                                         + "d-none d-md-block"}))
    return int(hits_str.split(">")[1].split(" ")[0])
