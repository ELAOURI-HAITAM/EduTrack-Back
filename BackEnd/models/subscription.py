from datetime import datetime
from sqlalchemy import Column, DateTime, Integer , ForeignKey
from database.connexion import Base
from sqlalchemy.orm import relationship




class Subscription(Base) :
    __tablename__ = "subscriptions"

    id = Column(Integer , primary_key =True , index=True)
    student_id = Column(Integer , ForeignKey("students.id"))
    professor_id = Column(Integer , ForeignKey("professors.id"))
    created_at = Column(DateTime , default=datetime.utcnow())
    
    student = relationship("Student" , back_populates="subscriptions")
    professor = relationship("Professor" , back_populates="subscriptions")
    
    
    
