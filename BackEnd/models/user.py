from sqlalchemy import Column, DateTime, Integer, String, Enum
from database.connexion import Base
import enum
from sqlalchemy.orm import relationship
class UserRole(enum.Enum):
    Professor = "Professor"
    Student = "Student"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer , primary_key = True , index=True)
    email = Column(String , unique = True , index = True)
    password = Column(String , index = True , nullable = True)
    otp = Column(String  , nullable = True)
    otp_expires_at = Column(DateTime , nullable = True)
    role = Column(Enum(UserRole))

    student_data = relationship(
        "Student",
        back_populates="user",
        uselist=False,
    )
    prof_data = relationship(
        "Professor",
        back_populates="user",
        uselist=False,
    )

    
    
    