from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .database import Base

class Script(Base):
    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    platform = Column(String, index=True)
    language = Column(String)
    script_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_date = Column(DateTime, nullable=True)
