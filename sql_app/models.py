from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from .database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    observation = Column(String, index=True)
    proba = Column(Float, index=True)
    true_class = Column(Integer, index=True)
