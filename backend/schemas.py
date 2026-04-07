from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class GenerateRequest(BaseModel):
    topic: str
    audience: str
    platform: str
    duration: Optional[str] = None
    language: Optional[str] = "English"
    tone: Optional[str] = "Educational"

class PlatformContent(BaseModel):
    hook: Optional[str] = None
    script: Optional[str] = None
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    title: Optional[str] = None
    cta: Optional[str] = None

class GenerateResponse(BaseModel):
    platform: str
    content: PlatformContent

class ScriptCreate(BaseModel):
    topic: str
    platform: str
    language: str
    script_content: str
    scheduled_date: Optional[datetime] = None

class ScriptResponse(ScriptCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class HookRequest(BaseModel):
    topic: str
    platform: Optional[str] = "General"
    language: Optional[str] = "English"

class HookResponse(BaseModel):
    hook: str

class CalendarRequest(BaseModel):
    topic: str
    audience: str
    platform: str
    post_count: int
    start_date: datetime
    language: Optional[str] = "English"
    tone: Optional[str] = "Educational"

class CalendarResponseElement(BaseModel):
    scheduled_date: datetime
    content: PlatformContent

class CalendarResponse(BaseModel):
    platform: str
    posts: List[CalendarResponseElement]
