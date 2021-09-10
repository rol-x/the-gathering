"""Scrape the card market website to get all the neccessary data."""
import globals
import handlers.data_handler as data_handler
from entity.card import add_card, get_card_ID, is_card_saved
from entity.card_stats import add_card_stats, are_card_stats_saved_today
from entity.date import add_date
from entity.sale_offer import add_offers
from entity.seller import get_seller_names
from handlers.log_handler import log, log_url, log_progress
from handlers.web_handler import *

# TODO: Look into handling of wild Firefox processes.
# TODO: Change singular to plural in entities use, not in model.

# Main function
if __name__ == "__main__":

    # Setup
    data_handler.prepare_files()
    globals.this_date_ID = add_date()
    data_handler.prepare_expansion_list_file(globals.expansion_name)
    driver = create_webdriver()

    # Get card names and open each card's URL
    progress = 0
    card_list = get_card_names(driver, globals.expansion_name)
    for card_name in card_list:
        progress += 1
        log_progress(card_name, progress, len(card_list))

        # Bang and scream at the door until they let you in
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
                log('Waiting and reconnecting...  (cooldown for 30.0 seconds)')
                realistic_pause(30.0)
                globals.wait_coef *= 1.1
                driver = restart_webdriver(driver)

        # Save the card if not saved already
        if not is_card_saved(card_name):
            add_card(card_soup)

        # Save the card market statistics if not saved today
        card_ID = get_card_ID(card_name)
        if not are_card_stats_saved_today(card_ID):
            add_card_stats(card_soup, card_ID)
        else:
            log(' = Card stats = ')
            log(f"Card ID:  {card_ID}")
            log('Already saved today\n')

        # Get all sellers from the card page
        log(" = Sellers = ")
        log(f"Task - Updating sellers")
        sellers = get_seller_names(card_soup)

        # Investigate and add only not added sellers
        add_sellers_from_set(driver, sellers)

        # Get all sale offers from the page
        log(" = Offers = ")
        log("Task - Updating sale offers")
        add_offers(card_soup)

    # Log program task completion
    log("All cards, sellers and sale offers acquired")

    # Close the webdriver
    driver.close()
    log("Webdriver closed")

    # Validate the local data
    removed = data_handler.validate_local_data()
    log(f"Local data validated (removed {removed} records)\n")
    log("=== Program execution finished ===")
