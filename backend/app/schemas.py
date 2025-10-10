from pydantic import BaseModel
from datetime import datetime

class WatchlistCreate(BaseModel):
    symbol: str
    name: str
    market_cap: float
    pe_ratio: float
    price: float
    currency: str
    exchange: str

class WatchlistOut(BaseModel):
    id: int
    symbol: str
    name: str
    market_cap: float
    pe_ratio: float
    price: float
    currency: str
    exchange: str
    created_at: datetime

    # Needed to convert SQLAlchemy model to Pydantic
    class Config:
        # from_attributes tells Pydantic to read from SQLAlchemy model attributes, not just dicts.
        # Required to serialize DB models into API response properly in Pydantic v2.
        model_config = { "from_attributes": True }