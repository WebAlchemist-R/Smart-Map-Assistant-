from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: Optional[EmailStr]
    phone: Optional[str]
    password: Optional[str]
    display_name: Optional[str]

class UserOut(BaseModel):
    id: int
    email: Optional[EmailStr]
    display_name: Optional[str]
    created_at: datetime
    class Config:
        orm_mode = True

class SearchCreate(BaseModel):
    query: str
    lat: float
    lng: float

class ReportCreate(BaseModel):
    type: str
    description: Optional[str]
    lat: float
    lng: float
