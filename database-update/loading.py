from  dbconfig import db, dates, cards, sellers, cards_stats, sale_offers
import pandas as pd
import json
from sqlalchemy import desc
import os

def dates_load():
    datesdf = pd.read_csv('data/date.csv', sep=';')
    count = dates.query.count()
    last_id = dates.query.order_by(desc(dates.date_ID)).first()
    try:
        relevantdf = datesdf[datesdf.date_ID > last_id.date_ID] if last_id.date_ID == count else datesdf
    except AttributeError:
        relevantdf = datesdf
    for i in relevantdf.index:
        parsed = json.loads(relevantdf.loc[i].to_json())
        criteria = dict(filter(lambda v: (v[0], v[1]) if v[1] is not None else None, parsed.items()))
        check = dates.query.filter_by(**criteria).one_or_none()
        if check == None:
            date = dates(**criteria)
            db.session.add(date)
            db.session.commit()

def cards_load():
    cardsdf = pd.read_csv('data/card.csv', sep=';')
    last_id = cards.query.order_by(desc(cards.card_ID)).first()
    count = cards.query.count()
    try:
        relevantdf = cardsdf[cardsdf.card_ID > last_id.card_ID] if last_id.card_ID == count else cardsdf
    except AttributeError:
        relevantdf = cardsdf
    for i in relevantdf.index:
        parsed = json.loads(relevantdf.loc[i].to_json())
        criteria = dict(filter(lambda v: (v[0], v[1]) if v[1] is not None else None, parsed.items()))
        check = cards.query.filter_by(**criteria).one_or_none()
        if check == None:
            card = cards(**criteria)
            db.session.add(card)
            db.session.commit()

def cards_stats_load():
    statsdf = pd.read_csv('data/card_stats.csv', sep=';')
    last_id = cards_stats.query.order_by(desc(cards_stats.stat_ID)).first()
    count = cards_stats.query.count()
    if last_id.stat_ID == count:
        statsdf = statsdf.query('(date_ID == ' + str(last_id.date_ID) + ' and card_ID >= ' \
            + str(last_id.card_ID) + ') or date_ID > ' + str(last_id.date_ID))
        for row in statsdf.iterrows():
            if row[0] <= last_id.stat_ID:
                statsdf = statsdf.drop(row[0])
            else:
                break
    for row in statsdf.iterrows():
        parsed = json.loads(statsdf.loc[row[0]].to_json())
        criteria = dict(filter(lambda v: (v[0], v[1]) if v[1] is not None else None, parsed.items()))
        criteria['avg_price_30'] = criteria.pop('30_avg_price')
        criteria['avg_price_7'] = criteria.pop('7_avg_price')
        criteria['avg_price_1'] = criteria.pop('1_avg_price')
        criteria['stat_ID'] = row[0] + 1
        check = cards_stats.query.filter_by(**criteria).one_or_none()
        if check == None:
            stats = cards_stats(**criteria)
            db.session.add(stats)
            db.session.commit()

def sellers_load():
    sellersdf = pd.read_csv('data/seller.csv', sep=';')
    last_id = sellers.query.order_by(desc(sellers.seller_ID)).first()
    count = sellers.query.count()
    try:
        relevantdf = sellersdf[sellersdf.seller_ID > last_id.seller_ID] if count == last_id.seller_ID else sellersdf
    except AttributeError:
        relevantdf = sellersdf
    for i in relevantdf.index: 
        parsed = json.loads(relevantdf.loc[i].to_json())
        criteria = dict(filter(lambda v: (v[0], v[1]) if v[1] is not None else None, parsed.items()))
        check = sellers.query.filter_by(**criteria).one_or_none()
        if check == None:
            seller = sellers(**criteria)
            db.session.add(seller)
            db.session.commit()

def offers_load():
    offersdf = pd.read_csv('data/sale_offer.csv', sep=';')
    last_id = sale_offers.query.order_by(desc(sale_offers.offer_ID)).first()
    count = sale_offers.query.count()
    if last_id.offer_ID == count:
        offersdf = offersdf.query('(date_ID == ' + str(last_id.date_ID) + ' and card_ID >= ' \
            + str(last_id.card_ID) + ') or date_ID > ' + str(last_id.date_ID))
        for row in offersdf.iterrows():
            if row[0] <= last_id.offer_ID:
                offersdf = offersdf.drop(row[0])
            else:
                break
    for row in offersdf.iterrows():
        parsed = json.loads(offersdf.loc[row[0]].to_json())
        criteria = dict(filter(lambda v: (v[0], v[1]) if v[1] is not None else None, parsed.items()))
        criteria['offer_ID'] = row[0] + 1
        criteria['is_foiled'] = 'True' if criteria['is_foiled'] else 'False'
        check = sale_offers.query.filter_by(**criteria).one_or_none()
        if check == None:
            stats = sale_offers(**criteria)
            db.session.add(stats)
            db.session.commit()
    nr = 2
    offersdf = pd.read_csv('data/sale_offer.csv', sep=';')
    offset = offersdf.tail(1).index[0] + 1
    while(os.path.exists('data/sale_offer_' + str(nr) + '.csv')):
        offersdf = pd.read_csv('data/sale_offer_' + str(nr) + '.csv', sep=';')
        last_id = sale_offers.query.order_by(desc(sale_offers.offer_ID)).first()
        count = sale_offers.query.count()
        if last_id.offer_ID == count:
            offersdf = offersdf.query('(date_ID == ' + str(last_id.date_ID) + ' and card_ID >= ' \
                + str(last_id.card_ID) + ') or date_ID > ' + str(last_id.date_ID))
            for row in offersdf.iterrows():
                if row[0] + offset + 1 <= last_id.offer_ID:
                    offersdf = offersdf.drop(row[0])
                else:
                    break
        for row in offersdf.iterrows():
            parsed = json.loads(offersdf.loc[row[0]].to_json())
            criteria = dict(filter(lambda v: (v[0], v[1]) if v[1] is not None else None, parsed.items()))
            criteria['offer_ID'] = row[0] + 1 + offset
            criteria['is_foiled'] = 'True' if criteria['is_foiled'] else 'False'
            check = sale_offers.query.filter_by(**criteria).one_or_none()
            if check == None:
                stats = sale_offers(**criteria)
                db.session.add(stats)
                db.session.commit()
        offersdf = pd.read_csv('data/sale_offer_' + str(nr) + '.csv', sep=';')
        offset += offersdf.tail(1).index[0] + 1
        nr += 1

def test():

    offersdf = pd.read_csv('data/sale_offer_2.csv', sep=';')
    print(offersdf)