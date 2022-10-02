from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/predict/", response_model=schemas.Prediction)
def predict(
    prediction: schemas.Prediction, db: Session = Depends(get_db)
):
    return crud.create_prediction(db=db, prediction=prediction)

@app.post('/update', response_model=schemas.Prediction)
def update(
    update: schemas.Update, db: Session = Depends(get_db)
):
    return crud.update_prediction(db=db, update=update)

@app.get("/list-predictions/", response_model=List[schemas.Prediction])
def list_predictions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    predictions = crud.get_predictions(db, skip=skip, limit=limit)
    return predictions
