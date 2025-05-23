from pydantic import BaseModel
from datetime import datetime

class WatchlistCreate(BaseModel):
    symbol: str

class WatchlistOut(BaseModel):
    id: int
    symbol: str
    created_at: datetime

    # Needed to convert SQLAlchemy model to Pydantic
    class Config:
        # from_attributes tells Pydantic to read from SQLAlchemy model attributes, not just dicts.
        # Required to serialize DB models into API response properly in Pydantic v2.
        model_config = { "from_attributes": True }