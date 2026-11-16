from pydantic import BaseModel, Field
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

class DependenceRequest(BaseModel):
    price_series: dict[str, list[float]] = Field(
        ...,
        description="Mapping of ticker symbols to chronological closing prices (min 3 observations)."
    )
    divergence_threshold: float = Field(default=0.25, ge=0.0, le=2.0)

class AnomalyEvaluateRequest(BaseModel):
    high: list[float] = Field(..., description="Chronological daily high prices (min 50 observations).")
    low: list[float] = Field(..., description="Chronological daily low prices (min 50 observations).")
    close: list[float] = Field(..., description="Chronological daily closing prices (min 50 observations).")
    volume: list[float] = Field(..., description="Chronological daily trading volumes (min 50 observations).")
    window: int = Field(default=30, ge=5, le=120)
    z_threshold: float = Field(default=2.5, ge=1.0, le=10.0)
    contamination: float = Field(default=0.05, gt=0.0, lt=0.5)    