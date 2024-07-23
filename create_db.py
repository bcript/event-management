import sqlite3

# Initialise SQL database
connection = sqlite3.connect("user_data.db")
cursor = connection.cursor()

# SQL Queries
command = """CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, password TEXT NOT NULL, email TEXT NOT NULL)"""
cursor.execute(command)
