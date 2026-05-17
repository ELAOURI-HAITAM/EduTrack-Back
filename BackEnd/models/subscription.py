from datetime import datetime
from os import name
from sqlalchemy import Boolean, Column, DateTime, Integer , ForeignKey , UniqueConstraint
from database.connexion import Base
from sqlalchemy.orm import relationship




class Subscription(Base) :
    __tablename__ = "subscriptions"

    id = Column(Integer , primary_key =True , index=True)
    student_id = Column(Integer , ForeignKey("students.id"))
    professor_id = Column(Integer , ForeignKey("professors.id"))
    created_at = Column(DateTime , default=datetime.utcnow)
    is_follow = Column(Boolean , default=False)
    
    student = relationship("Student" , back_populates="subscriptions")
    professor = relationship("Professor" , back_populates="subscriptions")
    __table_args__ = (
        UniqueConstraint('student_id', 'professor_id', name='unique_student_professor'),
    )