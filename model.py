from pydantic import BaseModel
from typing import List, Optional

# Pydantic Models
class ChatRequest(BaseModel):
    dialog_id: str
    user_id: str
    user_input: str


class ChatResponse(BaseModel):
    response: str
    matching: List[str]
