from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    email: str
    password: str
    username: Optional[str] = None  # Optionnel
    role: str
