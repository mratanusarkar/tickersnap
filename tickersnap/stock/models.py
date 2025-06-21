from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

# --------------------------------------------------------------------------------------
# Tickertape API Models (Scorecard)
# --------------------------------------------------------------------------------------


class ScoreData(BaseModel):
    """
    Score information for scorecard categories.
    
    Note:
        - internal use only
        - used by models: `ScorecardItem`
        - used only in "score" field of: performance, valuation, growth, profitability
    """
    
    percentage: bool
    max: int
    value: Optional[float] = None
    key: str


class ScorecardElement(BaseModel):
    """
    Individual element within scorecard categories like Entry Point and Red Flags.
    
    Note:
        - internal use only
        - used by models: `ScorecardItem`
        - used only in "elements" field of: entry_point, red_flags
    """
    
    title: str
    type: str
    description: Optional[str] = None
    flag: Optional[str] = None
    display: bool
    # score: can be missing for some stocks
    score: Optional[Any] = None
    source: Optional[str] = None


class ScorecardItem(BaseModel):
    """
    Individual scorecard category item for categories like:
        Performance, Valuation, Growth, Profitability, Entry Point, Red Flags
    
    Note:
        - internal use only
        - used by models: `ScorecardResponse`
    """
    
    name: str
    # tag: can be missing for some stocks
    tag: Optional[str] = None
    type: str
    description: Optional[str] = None
    # colour: can be missing for some stocks
    colour: Optional[str] = None
    # score: is "None" for "entry point" and "red flag" types,
    # and can be missing for some stocks
    score: Optional[ScoreData] = None
    rank: Optional[Any] = None
    peers: Optional[Any] = None
    locked: bool
    callout: Optional[Any] = None
    comment: Optional[str] = None
    stack: int
    # elements: is empty for "performance", "valuation", "growth", "profitability" types
    # and can be missing for some stocks
    elements: List[ScorecardElement] = Field(default_factory=list) 


class ScorecardResponse(BaseModel):
    """
    Complete scorecard API response.
    
    Reference:
        - HTTP Request: GET
        - URL: https://analyze.api.tickertape.in/stocks/scorecard/{sid}
        - Response Body: `ScorecardResponse`
    """
    
    success: bool
    # data: is "None" when success is "False"
    data: Optional[List[ScorecardItem]] = None
