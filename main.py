"""Scrape the card market website to get all the neccessary data."""
import globals
import handlers.database_handler as db_handler
import handlers.local_files_handler as local_files_handler
from entity.card import add_card, get_card_ID, is_card_saved
from entity.card_stats import add_card_stats, are_card_stats_saved_today
from entity.date import add_date
from entity.sale_offer import add_offers
from entity.seller import get_seller_names
from handlers.log_handler import log, log_url, log_progress
from handlers.web_handler import *

# TODO: Find out why some offers are not added from read to new.
# TODO: Offers changed during the day may appear separately after two runs.
# TODO: Look into handling of wild Firefox processes.

# Main function
if __name__ == "__main__":

    # Setup
    local_files_handler.prepare_files()
    globals.current_date_ID = add_date()
    local_files_handler.prepare_expansion_list_file(globals.expansion_name)
    driver = create_webdriver()
    conn, cursor = db_handler.connect_to_local_db('gathering')

    # Get card names and open each card's URL
    progress = 0
    card_list = get_card_names(driver, globals.expansion_name)
    for card_name in card_list:
        progress += 1
        log_progress(card_name, progress, len(card_list))

        # Bang and scream at the door until they let you in
        wait_time = 15.0
        card_url = globals.base_url + globals.expansion_name + '/'
        card_url += urlify(card_name)

        while True:
            # Open the card page and extend the view maximally
            realistic_pause(globals.wait_coef)
            driver.get(card_url)
            log_url(driver.current_url)
            log("                Expanding page...\n")
            click_load_more_button(driver)

            # Validate and save the parsed page content for later use
            card_soup = BeautifulSoup(driver.page_source, 'html.parser')
            if is_valid_card_page(card_soup):
                break
            else:
                log('Card page invalid: ' + driver.current_url)
                log('Waiting and reconnecting...  (cooldown '
                    + f'{wait_time} seconds)')
                realistic_pause(wait_time)
                wait_time *= 2
                if wait_time == 30.0:
                    globals.wait_coef *= 1.1
                if wait_time == 60.0:
                    globals.wait_coef *= 1.1
                    driver = restart_webdriver(driver)

        # Save the card if not saved already
        if not is_card_saved(card_name):
            add_card(card_soup)
        else:
            if globals.verbose_mode:
                log(f'Card {card_name} already saved\n')

        # Save the card market statistics if not saved today
        card_ID = get_card_ID(card_name)
        log(' = Card stats = ')
        log(f"Card ID:  {card_ID}")
        if not are_card_stats_saved_today(card_ID):
            add_card_stats(card_soup, card_ID)
            log('Card stats added\n')
        else:
            log('Already saved today\n')

        # Get all sellers from the card page
        log(" = Sellers = ")
        log("Task - Updating sellers list")
        sellers = get_seller_names(card_soup)

        # Investigate and add only not added sellers
        add_sellers_from_list(driver, set(sellers))

        # Get all sale offers from the page
        log(" = Offers = ")
        log("Task - Updating sale offers")
        add_offers(card_soup)

    # Log program task completion
    log("All cards, sellers and sale offers acquired")

    # Close the webdriver
    driver.close()
    log("Webdriver closed")

    # Close the connection to the database
    conn.close()
    log("Database connection closed")
