"""Connect to local MySQL database and manage the data exchange."""
import mysql.connector
from mysql.connector.errors import DatabaseError

from handlers.log_handler import log


# Send a query to insert a single seller into the database.
def insert_single_seller(cursor, conn, seller):
    '''Send a query to insert a single seller into the database.'''
    seller_ID = seller['seller_ID']
    seller_name = seller['seller_name']
    seller_type = seller['seller_type']
    member_since = seller['member_since']
    country = seller['country']
    address = seller['address']

    sql_query = "INSERT INTO seller VALUES ("
    + f"{seller_ID}, {seller_name}, {seller_type}, "
    + f"{member_since}, {country}, {address});"

    try:
        # Execute the SQL command and commit changes in the database
        cursor.execute(sql_query)
        conn.commit()
    except DatabaseError as db_error:
        # Rolling back in case of error
        conn.rollback()
        log(db_error)


# Connect to a local database of given name.
def connect_to_local_db(database_name):
    '''Connect to a local database of given name.'''
    conn = mysql.connector.connect(user='root',
                                   password='P@ssword',
                                   host='127.0.0.1',
                                   database=database_name)
    cursor = conn.cursor()
    log("Database connection established\n")
    return conn, cursor
