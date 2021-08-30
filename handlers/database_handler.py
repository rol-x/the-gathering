"""Connect to local MySQL database and manage the data exchange."""
import mysql.connector

from handlers.log_handler import log


# TODO: Send a query to the database
def send_query_seller(conn, seller_df):
    '''TODO: Send a query to the database.'''
    for ID in seller_df.index:
        print(seller_df.iloc[ID])
        break
    # sql_query = "INSERT INTO seller (seller_name, type, country, address)
    # VALUES ('"
    # + names[i].string + "', 0, '" + country[15:] + "')"
    # try:
    #        # Executing the SQL command
    #        cursor.execute(sql
    #        # Commit your changes in the database
    #        conn.commit()
    #    except:
    #        # Rolling back in case of error
    #        conn.rollback()
    input()
    print(seller_df)


# Connect to a local database of given name.
def connect_to_local_db(database_name):
    '''Connect to a local database of given name.'''
    conn = mysql.connector.connect(user='root', password='P@ssword',
                                   host='127.0.0.1', database=database_name)
    cursor = conn.cursor()
    log("Database connection established\n")
    return conn, cursor
