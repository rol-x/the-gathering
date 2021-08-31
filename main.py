"""Scrape the card market website to get all the neccessary data."""
import globals
import handlers.database_handler as db_handler
import handlers.local_files_handler as local_files_handler
from entity.card import add_card, get_card_ID, is_card_saved
from entity.card_stats import add_card_stats, are_card_stats_saved_today
from entity.date import add_date
from entity.sale_offer import add_offers
from entity.seller import add_seller, get_seller_names, is_seller_saved
from handlers.log_handler import log, log_url
from handlers.web_handler import *

# TODO: Better logging of new cards and card stats (as in sellers).
# TODO: Are all sale offers by separate sellers? Change the summary.
# TODO: Look into handling of wild Firefox processes.
# TODO: Try to clean up main :)

# Main function
if __name__ == "__main__":

    # Setup
    local_files_handler.prepare_files()
    globals.current_date_ID = add_date()
    local_files_handler.prepare_expansion_list_file(globals.expansion_name)
    driver = create_webdriver()
    conn, cursor = db_handler.connect_to_local_db('gathering')

    # Card pages count
    progress = 0

    # Loop over every card name
    card_list = get_card_names(driver, globals.expansion_name)
    for card_name in card_list:
        # Log the progress in data acquisition (done card by card)
        progress += 1
        log(f" == {card_name} == \t({progress}/{len(card_list)}  "
            + str(round(100*progress/len(card_list), 2))
            + "%)")

        # Bang and scream at the door until they let you in
        wait_time = 10.0
        while True:

            # Craft the card url and open it with the driver
            card_url_name = urlify(card_name)
            card_url = globals.base_url + globals.expansion_name \
                + '/' + card_url_name
            driver.get(card_url)
            log_url(driver.current_url)
            realistic_pause(0.6*globals.max_wait*globals.wait_coef)
            log("                Expanding page...\n")
            click_load_more_button(driver)

            # Save the parsed page content for later use
            card_soup = BeautifulSoup(driver.page_source, 'html.parser')
            if is_valid_card_page(card_soup):
                break
            else:
                log('Card page invalid: ' + driver.current_url)
                log('Waiting and reconnecting... (cooldown '
                    + f'{round(wait_time, 1)} seconds)')
                wait_time = exponential_wait(wait_time, 1.6)
                if wait_time > 40.0:
                    driver = restart_webdriver(driver)

        # Save the card if not saved already
        if not is_card_saved(card_name):
            add_card(card_soup)
        else:
            if globals.verbose_mode:
                log(f'Card {card_name} already saved\n')

        # Save the card market statistics if not saved today
        card_ID = get_card_ID(card_name)
        if not are_card_stats_saved_today(card_ID):
            add_card_stats(card_soup, card_ID)
        else:
            # if globals.verbose_mode:
            log(f'Stats of {card_name} [{card_ID}] already saved today\n')

        # Get all sellers from the card page
        log(" = Sellers = ")
        log("Task - Updating sellers list")
        sellers = get_seller_names(card_soup)
        sellers_before = len(local_files_handler.load_df('seller').index)
        read_sellers = len(sellers)
        new_sellers = 0
        for seller_name in sellers:

            # Check if a recent record already exists
            if not is_seller_saved(seller_name):
                # Wait to cool down requests from this IP
                realistic_pause(0.7*globals.max_wait*globals.wait_coef)
                # Get the page and add seller info
                driver.get(globals.users_url + seller_name)
                seller_soup = BeautifulSoup(driver.page_source, 'html.parser')
                add_seller(seller_soup)
                new_sellers += 1
            else:
                if globals.verbose_mode:
                    log('Already saved: ' + seller_name + '\n')

        # Logging
        total_sellers = sellers_before + new_sellers
        log(f"Done - {new_sellers} new sellers added  "
            + f"(out of: {read_sellers}, total: {total_sellers})\n")

        if new_sellers == 0:
            globals.speed_up()
        else:
            globals.wait_coef = 1.0

        # Get all sale offers from the page
        add_offers(card_soup)

    # Logging
    log("All cards, sellers and sale offers acquired")

    # Close the webdriver
    driver.close()
    log("Webdriver closed")

    # Close the connection to the database
    conn.close()
    log("Database connection closed")
