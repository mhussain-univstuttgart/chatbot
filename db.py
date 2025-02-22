import os
import sqlite3
import logging
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Database configuration
DATABASE = "chatbot.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Database Setup
def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dialog (
        id TEXT PRIMARY KEY,
        user_id TEXT
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS message (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dialog_id TEXT,
        user_input TEXT,
        chatbot_response TEXT,
        FOREIGN KEY(dialog_id) REFERENCES dialog(id)
    )""")
    conn.commit()
    conn.close()
    logger.info("Database setup complete.")
