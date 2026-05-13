import sqlite3

def get_connection():
    connection = sqlite3.connect("database/airline.db")

    connection.row_factory = sqlite3.Row

    return connection