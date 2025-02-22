import os
import sqlite3
import logging
import uvicorn
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from db import setup_database, get_db_connection
from model import ChatRequest, ChatResponse

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# OpenAI client
client = OpenAI(api_key=openai_api_key)

setup_database()

# Load entire data.txt file into memory
def load_full_data():
    logger.info("Loading full data.txt into memory...")
    with open("data.txt", "r", encoding="utf-8") as file:
        return file.read()


FULL_CONTEXT = load_full_data()
logger.info("Full data.txt loaded into memory.")


# Chat API Endpoint with structured OpenAI response
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    logger.info(f"Received chat request: {request}")

    # Generate chatbot response using full context
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": "You are provided with set of Service categories and Service Names in the category. "
                        "Help user find Service Names matching his requirment or problems in the matching field. "
                        "Provide a structured JSON response in the following format: {\"response\": \"LLM response message\", \"matching\": [\"name_0\", \"name_1\", \"name_2\"]}."},
            {"role": "user", "content": request.user_input},
            {"role": "assistant", "content": FULL_CONTEXT}
        ],
        response_format=ChatResponse
    )

    response_data = completion.choices[0].message.content

    try:
        structured_response = ChatResponse.parse_raw(response_data)
    except Exception as e:
        logger.error(f"Failed to parse response as JSON: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse chatbot response")

    # Store message in database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO message (dialog_id, user_input, chatbot_response) VALUES (?, ?, ?)",
                   (request.dialog_id, request.user_input, structured_response.response))
    conn.commit()
    conn.close()

    logger.info(f"Response generated for dialog_id {request.dialog_id}")
    return structured_response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)