from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.database import Base
from app.models import task


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="owner")