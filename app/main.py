from typing import List, Union
import os

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

#
# db connection
#
engine = create_engine(os.environ['DATABASE_URL'])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

#
# db models
#
class DB_Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    observation = Column(String, index=True)
    proba = Column(Float, index=True)
    true_class = Column(Integer, index=True)

#
# fastapi models
#
class Prediction(BaseModel):
    id: int
    observation: str

    class Config:
        orm_mode = True

class Update(BaseModel):
    id: int
    true_class: Union[int, None]

#
# create db tables, start app
#
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/predict/", response_model=Prediction)
def predict(
    prediction: Prediction, db: Session = Depends(get_db)
):
    db_prediction = DB_Prediction(**prediction.dict())
    # make prediction
    db_prediction.proba = 0.5
    db.add(db_prediction)
    try:
        db.commit()
        db.refresh(db_prediction)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail='Observation ID: "{}" already exists'.format(db_prediction.id)
        )
    return db_prediction

@app.post('/update', response_model=Prediction)
def update(
    update: Update, db: Session = Depends(get_db)
):
    try:
        db_prediction = db.query(DB_Prediction).get(update.id)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail='Observation ID: "{}" does not exist'.format(update.id)
        )
    db_prediction.true_class = update.true_class
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

@app.get("/list-predictions/", response_model=List[Prediction])
def list_predictions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(DB_Prediction).offset(skip).limit(limit).all()
