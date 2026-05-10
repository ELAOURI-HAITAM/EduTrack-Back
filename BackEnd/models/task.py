from datetime import datetime 
import enum
from sqlalchemy import Column,Enum, DateTime, Integer, String, ForeignKey, Text
from database.connexion import Base
from sqlalchemy.orm import relationship


class Difficulty(enum.Enum):
    Easy = "Easy"
    Medium = "Medium"
    Hard = "Hard"



class Task(Base) :
    __tablename__ = "tasks"

    id = Column(Integer , primary_key =True , index=True)
    title = Column(String , nullable=True)
    actual_minutes = Column(Integer)
    difficulty = Column(Enum(Difficulty))
    comment = Column(Text , nullable=True)
    student_id = Column(Integer , ForeignKey("students.id"))
    resource_id = Column(Integer , ForeignKey("resources.id"))
    completed_at = Column(DateTime , default=datetime.utcnow)
    
    student = relationship("Student" , back_populates="tasks")
    resource = relationship("Resource" , back_populates="tasks")
    
    
    
