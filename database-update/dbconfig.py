from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import INTEGER, DECIMAL, TINYINT
from sqlalchemy import ForeignKey
from urllib.parse import quote_plus

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:%s@localhost/gathering" % quote_plus('P@ssword')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class dates(db.Model):

    date_ID = db.Column(INTEGER(unsigned = True), primary_key = True, nullable = False, unique = True)
    day = db.Column(db.Integer, nullable = False)
    month = db.Column(db.Integer, nullable = False)
    year = db.Column(db.Integer, nullable = False)
    day_of_week = db.Column(db.Integer, nullable = False)

    def __repr__(self):

        return f"date(date_ID = {self.date_ID}, \
            day = {self.day}, month = {self.month},\
            year = {self.year}, day_of_week = {self.day_of_week})"

class cards(db.Model):

    card_ID = db.Column(INTEGER(unsigned = True), primary_key = True, nullable = False, unique = True)
    card_name = db.Column(db.String(30), nullable = False)
    expansion_name = db.Column(db.String(30), nullable = False)
    rarity = db.Column(db.String(20), nullable = False)

    def __repr__(self):

        return f"card(card_ID = {self.card_ID}, \
            name = {self.card_name}, expansion_name = {self.expansion_name},\
            rarity = {self.rarity})"

class cards_stats(db.Model):

    stat_ID = db.Column(INTEGER(unsigned = True), primary_key = True, nullable = False, unique = True)
    card_ID = db.Column(INTEGER(unsigned = True), ForeignKey('cards.card_ID'), nullable = False)
    price_from = db.Column(DECIMAL(19,2), nullable = False)
    avg_price_30 = db.Column(DECIMAL(19,2), nullable = False)
    avg_price_7 = db.Column(DECIMAL(19,2), nullable = False)
    avg_price_1 = db.Column(DECIMAL(19,2), nullable = False)
    available_items = db.Column(INTEGER(unsigned = True), nullable = False)
    date_ID = db.Column(INTEGER(unsigned = True), ForeignKey('dates.date_ID'), nullable = False)

    def __repr__(self):

        return f"card_stats(card_id = {self.card_ID}, \
            price_from = {self.price_from}, avg_price_30 = {self.avg_price_30},\
            avg_price_7 = {self.avg_price_7}, avg_price_1 = {self.avg_price_1},\
            availavle_items = {self.available_items}, date_id = {self.date_ID})"

class sellers(db.Model):

    seller_ID = db.Column(INTEGER(unsigned = True), primary_key = True, nullable = False, unique = True)
    seller_name = db.Column(db.String(30), nullable = False)
    type = db.Column(db.String(20), nullable = False)
    member_since = db.Column(db.String(4), nullable = False)
    country = db.Column(db.String(30), nullable = False)
    address = db.Column(db.String(100), nullable = True)

    def __repr__(self):

        return f"seller(seller_ID = {self.seller_ID},\
        seller_name = {self.seller_name}, type = {self.type},\
        country = {self.country}, address = {self.address})"

class sale_offers(db.Model):

    offer_ID = db.Column(INTEGER(unsigned = True), primary_key = True, nullable = False, unique = True)
    seller_ID = db.Column(INTEGER(unsigned = True), ForeignKey('sellers.seller_ID'), nullable = False)
    price = db.Column(DECIMAL(19,2), nullable = False)
    card_ID = db.Column(INTEGER(unsigned = True), ForeignKey('cards.card_ID'), nullable = False)
    card_condition = db.Column(db.String(20), nullable = False)
    language = db.Column(db.String(20), nullable = False)
    is_foiled = db.Column(db.Enum('True', 'False'), nullable = True)
    amount = db.Column(INTEGER(unsigned = True), nullable = False)
    date_ID = db.Column(INTEGER(unsigned = True), ForeignKey('dates.date_ID'), nullable = False)

    def __repr__(self):

        return f"offer(offer_id = {self.offer_ID}, seller_id = {self.seller_ID}, \
            price = {self.price}, card_id = {self.card_ID},\
            card_condition = {self.card_condition}, \
            is_foiled = {self.is_foiled}, date_id = {self.date_ID})"
