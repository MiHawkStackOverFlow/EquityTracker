from pydantic import BaseModel

class WatchlistCreate(BaseModel):
    symbol: str
