from datetime import datetime
import enum
from sqlalchemy import Column,Enum, DateTime, Integer, String  , ForeignKey
from database.connexion import Base
from sqlalchemy.orm import relationship


class TaskType(enum.Enum):
    Exercice = "Exercice"
    Course = "Course"



class Task(Base) :
    __tablename__ = "tasks"

    id = Column(Integer , primary_key =True , index=True)
    title = Column(String , nullable=True)
    file_url = Column(String)
    task_type = Column(Enum(TaskType))
    estimated_minutes = Column(Integer)
    module_id = Column(Integer , ForeignKey("modules.id"))
    created_at = Column(DateTime , default=datetime.utcnow())
    
    module = relationship("Module" , back_populates="tasks")
    completed_tasks = relationship("CompletedTask" , back_populates="task")
    
    
    
