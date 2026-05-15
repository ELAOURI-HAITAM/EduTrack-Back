from datetime import datetime 
import enum
from sqlalchemy import Column,Enum, DateTime, Integer, String, ForeignKey, Text
from database.connexion import Base
from sqlalchemy.orm import relationship


class Difficulty(enum.Enum):
    Easy = "Easy"
    Medium = "Medium"
    Hard = "Hard"



class CompletedTask(Base) :
    __tablename__ = "completed_tasks"

    id = Column(Integer , primary_key =True , index=True)
    title = Column(String , nullable=True)
    actual_minutes = Column(Integer)
    difficulty = Column(Enum(Difficulty))
    comment = Column(Text , nullable=True)
    student_id = Column(Integer , ForeignKey("students.id" , ondelete="CASCADE"))
    task_id = Column(Integer , ForeignKey("tasks.id", ondelete="CASCADE"))
    completed_at = Column(DateTime , default=datetime.utcnow)
    
    student = relationship("Student" , back_populates="completed_tasks")
    task = relationship("Task" , back_populates="completed_tasks")
    
    
    
