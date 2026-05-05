from sqlalchemy import Column, Date, Integer, String , Enum , ForeignKey
from database.connexion import Base
import enum
from sqlalchemy.orm import relationship

class Gender(enum.Enum):
    Male = "male"
    female = "female"


class Student(Base) :
    __tablename__ = "students"

    id = Column(Integer , primary_key =True , index=True)
    first_name = Column(String , index =True ,nullable=True)
    last_name = Column(String , index =True , nullable=True)
    birth_date = Column(Date , nullable=True  , index = True  )
    gender = Column(Enum(Gender) , nullable=True)
    user_id = Column(Integer , ForeignKey("users.id" , ondelete="CASCADE"))
    
    user = relationship("User", back_populates="student_data")
    subscriptions = relationship("Subscription", back_populates="student")
    task_logs = relationship("Task", back_populates="student")

    
    
