from datetime import datetime
import enum
from sqlalchemy import Column,Enum, DateTime, Integer, String  , ForeignKey
from database.connexion import Base
from sqlalchemy.orm import relationship


class TaskType(enum.Enum):
    Exercice = "Exercice"
    Course = "Course"



class Resource(Base) :
    __tablename__ = "resources"

    id = Column(Integer , primary_key =True , index=True)
    title = Column(String , nullable=True)
    file_url = Column(String)
    task_type = Column(Enum(TaskType))
    estimated_minutes = Column(Integer)
    module_id = Column(Integer , ForeignKey("modules.id"))
    created_at = Column(DateTime , default=datetime.utcnow())
    
    module = relationship("Module" , back_populates="resources")
    tasks = relationship("Task" , back_populates="resource")
    
    
    
