from  loading import dates_load, cards_load, sellers_load, cards_stats_load, offers_load, test
from dbconfig import db

def launch():
    #db.create_all() 
    #dates_load()
    #cards_load()
    #cards_stats_load()
    #sellers_load()
    offers_load()
    #test()

if __name__ == "__main__":
    launch()