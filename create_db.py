import sqlite3

# Initialise SQL database
connection = sqlite3.connect("user_data.db")
cursor = connection.cursor()

# SQL Queries

# command for users table
command = """CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, password TEXT NOT NULL, email TEXT NOT NULL)"""

# create table for events
cursor.execute('''CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        start_time DATETIME NOT NULL,
        end_time DATETIME NOT NULL,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
cursor.execute(command)
