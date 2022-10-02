from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import models, schemas
from fastapi import Depends, FastAPI, HTTPException



def get_predictions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Prediction).offset(skip).limit(limit).all()


def create_prediction(db: Session, prediction: schemas.Prediction):
    db_prediction = models.Prediction(**prediction.dict())
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

def update_prediction(db: Session, update: schemas.Update):
    try:
        db_prediction = db.query(models.Prediction).get(update.id)
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
