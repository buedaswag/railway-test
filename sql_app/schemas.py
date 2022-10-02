from typing import List, Union

from pydantic import BaseModel


class Prediction(BaseModel):
    id: int
    observation: str

    class Config:
        orm_mode = True

class Update(BaseModel):
    id: int
    true_class: Union[int, None]
