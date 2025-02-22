from db import find_matches_and_context
import sqlite3

# Database configuration
DATABASE = "chatbot.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn