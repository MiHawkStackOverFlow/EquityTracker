from sqlalchemy import Column, Integer, String, DateTime, Float, func
from .db_sync import Base

class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    market_cap = Column(Float, nullable=False)
    pe_ratio = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())