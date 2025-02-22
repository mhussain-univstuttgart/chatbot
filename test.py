import unittest
from fastapi.testclient import TestClient
from chatbot import app  # Importing the FastAPI app from chatbot.py

# Initialize Test Client
test_client = TestClient(app)

class ChatbotTestCase(unittest.TestCase):
    def test_chat_endpoint(self):
        test_data = {
            "dialog_id": "dialog1",
            "user_id": "user1",
            "user_input": "Tell me about funding options."
        }
        response = test_client.post("/chat", json=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())
        self.assertIn("matching", response.json())
        self.assertIsInstance(response.json()["matching"], list)

if _name_ == "_main_":
    unittest.main()