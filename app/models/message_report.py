from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class MessageReport(Base):
    """メッセージ通報モデル"""
    __tablename__ = "message_reports"
    __table_args__ = (
        UniqueConstraint("message_id", "reporter_user_id", name="uq_message_report_per_user"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    reporter_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    label = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<MessageReport(message_id={self.message_id}, reporter_user_id={self.reporter_user_id}, label={self.label})>"
