from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class JobOffer(BaseModel):
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    skills: Optional[str] = None
    job_description: Optional[str] = None  # Nouveau champ ajouté
    date: Optional[datetime] = None
