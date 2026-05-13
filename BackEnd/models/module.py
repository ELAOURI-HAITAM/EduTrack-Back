from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from database.connexion import Base
from sqlalchemy.orm import relationship


class Module(Base):

    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    professor_id = Column(Integer,ForeignKey("professors.id" , ondelete="CASCADE"),nullable=False)
    created_at = Column(DateTime,default=datetime.utcnow)

    professor = relationship(
        "Professor",
        back_populates="modules"
    )

    resources = relationship(
        "Resource",
        back_populates="module",
        cascade="all, delete"
    )