"""Scrape the card market website to get all the neccessary data."""
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def create_webdriver(url):
    '''Return the Firefox webdriver in headless mode, started at the provided url.'''
    print('Opening the webdriver')
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    print(f'Navigating to {url}')
    browser.get(url)
    return browser


def get_card_sellers(browser, url):
    '''Return all sellers that have an active offer on a card.'''
    # Move to the specified card page
    browser.get(url)

    # Load all sell offers
    while True:
        load_more_button = browser.find_element_by_xpath('//button[@id="loadMoreButton"]')
        if load_more_button.text == "":
            break
        browser.execute_script("arguments[0].click();", load_more_button)
        print('Extending the sellers view...')
        sleep(0.5)

    # Find all names (better to find all rows and extract info from each row)
    html_content = browser.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    names = soup.findAll("span", {"class": "d-flex has-content-centered mr-1"})
    conditions = soup.findAll("a", {"href": "/en/Magic/Help/CardCondition"})
    # print(conditions[0].find("span")['data-original-title'])

    # Add sellers names to a set
    sellers = set()
    for name in names:
        if name.string in sellers:
            print(name.string + ' already is in the set!')
        else:
            print(f'Adding {name.string} to card sellers')
            sellers.add(name.string)

    # Return the set of sellers
    print(f'Returning all sellers of card {url.split("/")[-1]}')
    # browser.close()
    return sellers


def get_all_sellers(expansion):
    '''Return all sellers that have an active offer in the provided expansion.'''
    # Open the webdriver
    browser = create_webdriver('https://www.cardmarket.com/en/Magic/Products/Singles/' + expansion)
    all_sellers = set()
    page_no = 1

    # Iterate through pages of card offers
    while True:
        # Open the next page
        browser.get('https://www.cardmarket.com/en/Magic/Products/Singles/'
                    + expansion + '?site=' + str(page_no))

        # Find all links to card offers
        html_content = browser.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        urls = soup.findAll("div", {"class":
                       "col-10 col-md-8 px-2 flex-column align-items-start justify-content-center"})

        # Exit the loop at the end of the list
        if len(urls) == 0:
            break

        # Create a webdriver for single card sellers
        mini_browser = create_webdriver('https://www.cardmarket.com')

        # Get every seller from each offer link
        for url in urls:
            link = url.find('a', href=True)
            if link is not None:
                print('Getting sellers from ', link['href'])
                # Have created browser and change the link to https://www.cardmarket.com + link['href]
                this_card_sellers = get_card_sellers(mini_browser, 'https://www.cardmarket.com' + link['href'])
                all_sellers.union(this_card_sellers)
                print('All sellers set expanded\n')

        # Increment the page counter
        page_no += 1

    mini_browser.close();

    # Return the set of all sellers
    return all_sellers


def save_to_file(collection, filename):
    '''Save a collection of items to a file.'''
    with open(filename, 'w') as writer:
        for item in collection:
            writer.write(str(item) + ',')
    print(f'Collection of type {type(collection)} saved to {filename} successfully.')


if __name__ == "__main__":
    # Getting a single card sellers
    # SSEEK = 'Battlebond/Spellseeker'
    # VIG = 'Battlebond/Vigor'
    # sellers = get_card_sellers('https://www.cardmarket.com/en/Magic/Products/Singles/'
    #                                       + SSEEK)
    # common_sellers.intersection_update(get_card_sellers(
     #   'https://www.cardmarket.com/en/Magic/Products/Singles/' + VIG))

    # Test saving to file
    # save_to_file(common_sellers, 'common_sellers.csv')

    # Getting all sellers of cards in given expansion
    EXPANSION = 'Battlebond'
    bb_sellers = get_all_sellers(EXPANSION.replace(' ', '-'))
    print(len(bb_sellers))

    # Save the sellers to a .csv file
    # save_to_file(kot_sellers, EXPANSION.replace('-', '') + '.csv')
