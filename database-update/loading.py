import dbconfig
import pandas as pd
import json

def dates_load():

    dates = pd.read_csv('data/date.csv', sep=';')
    count = dbconfig.dates.query.filter_by().count()
    relevant = dates[dates.date_ID > count]
    for i in relevant.index:

        parsed = json.loads(relevant.loc[i].to_json())
        criteria = dict(filter(lambda v: (v[0], v[1]) if v[1] is not None else None, parsed.items()))
        check = dbconfig.dates.query.filter_by(**criteria).one_or_none()
        if check == None:

            date = dbconfig.dates(**criteria)
            dbconfig.db.session.add(date)
            dbconfig.db.session.commit()

def cards_load():

    cards = pd.read_csv('data/card.csv', sep=';')
    count = dbconfig.cards.query.filter_by().count()
    relevant = cards[cards.card_ID > count]
    for i in relevant.index:

        parsed = json.loads(relevant.loc[i].to_json())
        criteria = dict(filter(lambda v: (v[0], v[1]) if v[1] is not None else None, parsed.items()))
        check = dbconfig.cards.query.filter_by(**criteria).one_or_none()
        if check == None:

            card = dbconfig.cards(**criteria)
            dbconfig.db.session.add(card)
            dbconfig.db.session.commit()

def cards_stats_load():

    stats = pd.read_csv('data/card_stats.csv', sep=';')
    check = dbconfig.cards_stats.query.distinct(dbconfig.cards_stats.date_ID).count()
    scndcheck = dbconfig.cards_stats.query.filter_by(date_ID = check).distinct(dbconfig.cards_stats.card_ID).count()
    firstrelevant = stats[stats.date_ID >= check]
    relevant = firstrelevant[stats.card_ID > scndcheck]
    for row in relevant.iterrows():

        parsed = json.loads(relevant.loc[row[0]].to_json())
        criteria = dict(filter(lambda v: (v[0], v[1]) if v[1] is not None else None, parsed.items()))
        criteria['avg_price_30'] = criteria.pop('30_avg_price')
        criteria['avg_price_7'] = criteria.pop('7_avg_price')
        criteria['avg_price_1'] = criteria.pop('1_avg_price')
        check = dbconfig.cards_stats.query.filter_by(**criteria).one_or_none()
        if check == None:

            stats = dbconfig.cards_stats(**criteria)
            dbconfig.db.session.add(stats)
            dbconfig.db.session.commit()

def sellers_load():

    sellers = pd.read_csv('data/seller.csv', sep=';')
    count = dbconfig.sellers.query.filter_by().count()
    relevant = sellers[sellers.seller_ID > count]
    for i in relevant.index:

        parsed = json.loads(relevant.loc[i].to_json())
        criteria = dict(filter(lambda v: (v[0], v[1]) if v[1] is not None else None, parsed.items()))
        check = dbconfig.sellers.query.filter_by(**criteria).one_or_none()
        if check == None:

            seller = dbconfig.sellers(**criteria)
            dbconfig.db.session.add(seller)
            dbconfig.db.session.commit()

def offers_load():

    offers = pd.read_csv('data/sale_offer.csv', sep=';')
    relevant = offers[offers.card_ID < 1]
    relevant.to_csv('data/errors.csv', sep=';')
    relevant = offers[offers.card_ID > 0]

def test():

    offers = pd.read_csv('data/sale_offer.csv', sep=';')
    relevant = offers[offers.card_ID < 1]
    print(relevant)