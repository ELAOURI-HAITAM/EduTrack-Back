from sqlalchemy import Column, Date, Integer, String , Enum , ForeignKey
from database.connexion import Base
import enum
from sqlalchemy.orm import relationship

class ProfessorGender(enum.Enum):
    Male = "Male"
    Female = "Female"


class Professor(Base) :
    __tablename__ = "professors"

    id = Column(Integer , primary_key =True , index=True)
    first_name = Column(String , index =True ,nullable=True)
    last_name = Column(String , index =True , nullable=True)
    birth_date = Column(Date , nullable=True  , index = True  )
    gender = Column(Enum(ProfessorGender) , nullable=True)
    phone_number = Column(String , nullable=True)
    user_id = Column(Integer , ForeignKey("users.id" , ondelete="CASCADE") , unique=True)
    
    user = relationship("User", back_populates="prof_data")
    modules = relationship("Module", back_populates="professor")
    subscriptions = relationship("Subscription", back_populates="professor")