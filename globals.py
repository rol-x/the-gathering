"""Store and initialize global variables in the program."""

# Variables for user custom program configuration
max_wait = 3.0
verbose_mode = False
expansion_name = 'Battlebond'

# Variables connected to this run of the code.
log_filename = 'dump.log'
current_date_ID = 0
wait_coef = 1.0

# Fixed variables
base_url = 'https://www.cardmarket.com/en/Magic/Products/Singles/'
users_url = 'https://www.cardmarket.com/en/Magic/Users/'


# Speed up until about 1 s wait time.
def speed_up():
    '''Speed up until about 1.0 s wait time.'''
    global wait_coef
    if wait_coef * max_wait < 1.0:
        wait_coef *= 1.05
    wait_coef *= 0.9
