# AI-Powered Chatbot with Vector Search

A FastAPI-based chatbot application that uses OpenAI's GPT-3.5 Turbo for generating responses and sentence transformers for semantic search functionality.

## Features

- Vector-based semantic search using Sentence Transformers
- Integration with OpenAI's GPT-3.5 Turbo for natural language responses
- SQLite database for storing conversations and matches
- FastAPI REST API endpoints
- Docker support for easy deployment
- Structured logging

## Prerequisites

- Python 3.8+
- OpenAI API key
- Docker (optional)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Installation

### Using Docker

1. Build the Docker image:
```bash
docker build -t ai-chatbot .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env ai-chatbot
```

### Manual Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python chatbot.py
```

## API Endpoints

### POST /chat

Create a new chat message and get a response.

Request body:
```json
{
    "dialog_id": "string",
    "user_id": "string",
    "user_input": "string"
}
```

Response:
```json
{
    "response": "string",
    "matching": ["string"]
}
```

## Data Format

The application expects a `data.txt` file with entries separated by `────────────────────────────────────────────────────────`. Each entry should contain:

- Name/Title (first line)
- Detailed information (subsequent lines)

## Development

The application uses:
- FastAPI for the web framework
- SQLite for data storage
- Sentence Transformers for vector embeddings
- OpenAI's GPT-3.5 Turbo for response generation

## Logging

Logs are written to stdout with timestamp, log level, and message information.

## Requirements

See `requirements.txt` for a full list of dependencies.