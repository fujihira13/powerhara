from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Channel(Base):
    """チャンネルモデル"""
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーション
    creator = relationship("User", backref="created_channels")
    messages = relationship("Message", back_populates="channel", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Channel(id={self.id}, name={self.name})>"
