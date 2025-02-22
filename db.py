from sentence_transformers import SentenceTransformer
import sqlite3
from utils import get_db_connection
from openai import OpenAI
import os
import numpy as np
from typing import List, Optional

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Create tables
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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matching (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id INTEGER,
        match_name TEXT,
        short_description TEXT,
        long_description TEXT,
        headquarters TEXT,
        regions_served TEXT,
        additional_services TEXT,
        contact_info TEXT,
        embedding BLOB,
        FOREIGN KEY(message_id) REFERENCES message(id)
    )""")
    conn.commit()
    conn.close()

setup_database()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load data from text file and store embeddings
def load_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    with open("data.txt", "r") as file:
        content = file.read().split("────────────────────────────────────────────────────────")
        for block in content:
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            if lines:
                name = lines[0]
                short_desc = ""
                long_desc = ""
                headquarters = ""
                regions_served = ""
                additional_services = ""
                contact_info = ""

                for i, line in enumerate(lines[1:]):
                    if "Short Description:" in line:
                        short_desc = lines[i+2]
                    elif "Long Description:" in line:
                        long_desc = " ".join(lines[i+3:])
                    elif "Headquarters:" in line:
                        headquarters = lines[i+1]
                    elif "Regions Served:" in line:
                        regions_served = lines[i+1]
                    elif "Additional Services:" in line:
                        additional_services = lines[i+1]
                    elif "Contact Info:" in line:
                        contact_info = " ".join(lines[i+1:])

                embedding = embedding_model.encode(long_desc).tolist()
                cursor.execute("""
                    INSERT INTO matching (match_name, short_description, long_description, headquarters, regions_served, additional_services, contact_info, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, short_desc, long_desc, headquarters, regions_served, additional_services, contact_info, sqlite3.Binary(np.array(embedding, dtype=np.float32).tobytes())))
    conn.commit()
    conn.close()

load_data()

# Retrieve matches using vector search and structure context
def find_matches_and_context(user_input: str) -> List[dict]:
    user_embedding = embedding_model.encode(user_input)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT match_name, short_description, long_description, headquarters, regions_served, additional_services, contact_info, embedding FROM matching")
    matches = []
    context = ""
    for row in cursor.fetchall():
        stored_embedding = np.frombuffer(row[7], dtype=np.float32)
        similarity = np.dot(user_embedding, stored_embedding) / (np.linalg.norm(user_embedding) * np.linalg.norm(stored_embedding))
        if similarity > 0.6:  # Threshold for relevance
            matches.append(row[0])
            context += f"\n### {row[0]}\n- **Short Description:** {row[1]}\n- **Long Description:** {row[2]}\n- **Headquarters:** {row[3]}\n- **Regions Served:** {row[4]}\n- **Additional Services:** {row[5]}\n- **Contact Info:** {row[6]}\n"
    conn.close()
    return matches, context