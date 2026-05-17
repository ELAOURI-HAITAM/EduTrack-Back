from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connexion import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    message = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)


    receiver = relationship(
        "User", 
        foreign_keys=[receiver_id], 
        backref="received_notifications"
    )
    
    sender = relationship(
        "User", 
        foreign_keys=[sender_id], 
        backref="sent_notifications"
    )