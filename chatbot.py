import os
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from model import ChatRequest, ChatResponse
from db import find_matches_and_context
from utils import get_db_connection

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# OpenAI client
client = OpenAI(api_key=openai_api_key)

# Chat API Endpoint
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    logger.info(f"Received chat request: {request}")

    # Find relevant matches and create structured context
    matches, structured_context = find_matches_and_context(request.user_input)

    # Generate chatbot response using context
    chatbot_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful chatbot that provides structured information."},
            {"role": "user", "content": request.user_input},
            {"role": "assistant", "content": structured_context}
        ]
    ).choices[0].message.content

    # Store message in database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO message (dialog_id, user_input, chatbot_response) VALUES (?, ?, ?)",
                   (request.dialog_id, request.user_input, chatbot_response))
    message_id = cursor.lastrowid

    # Store matches
    for match in matches:
        cursor.execute("INSERT INTO matching (message_id, match_name) VALUES (?, ?)", (message_id, match))
    conn.commit()
    conn.close()

    logger.info(f"Response generated for dialog_id {request.dialog_id} with matches: {matches}")
    return ChatResponse(response=chatbot_response, matching=matches or [])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)