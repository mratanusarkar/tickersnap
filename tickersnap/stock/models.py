from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

# --------------------------------------------------------------------------------------
# Tickertape API Models (Scorecard)
# --------------------------------------------------------------------------------------


class ScoreData(BaseModel):
    """
    Score information for scorecard categories.

    This model follows tickertape API response's schema for scorecard data
    within performance, valuation, growth, and profitability categories.

    Note:
        - internal use only
        - used by models: `ScorecardItem`
        - used only in "score" field of: performance, valuation, growth, profitability
    
    Disclaimer:
        - some fields can be missing (`None`) for some stocks when the data is not available
    """

    percentage: bool
    max: int
    value: Optional[float] = None
    key: str


class ScorecardElement(BaseModel):
    """
    Individual element within scorecard categories like Entry Point and Red Flags.

    This model follows tickertape API response's schema for elements data
    within entry point and red flags categories.

    Note:
        - internal use only
        - used by models: `ScorecardItem`
        - used only in "elements" field of: entry_point, red_flags
    
    Disclaimer:
        - some fields can be missing (`None`) for some stocks when the data is not available
    """

    title: str
    type: str
    description: Optional[str] = None
    flag: Optional[str] = None
    display: bool
    score: Optional[Any] = None
    source: Optional[str] = None


class ScorecardItem(BaseModel):
    """
    Individual scorecard category item (Performance, Valuation, Growth, Profitability, Entry Point, Red Flags).

    This model follows tickertape API response's schema for individual scorecard items.
    Each item represents one of the 6 scorecard categories with their respective data.

    Note:
        - internal use only
        - used by models: `ScorecardResponse`
    
    Disclaimer:
        - some fields can be missing (`None`) for some stocks when the data is not available
        - `score` will be `None` for "entry point" and "red flag" types
        - `elements` will be empty for "performance", "valuation", "growth", "profitability" types
    """
    
    name: str
    tag: Optional[str] = None
    type: str
    description: Optional[str] = None
    colour: Optional[str] = None
    score: Optional[ScoreData] = None
    rank: Optional[Any] = None
    peers: Optional[Any] = None
    locked: bool
    callout: Optional[Any] = None
    comment: Optional[str] = None
    stack: int
    elements: List[ScorecardElement] = Field(default_factory=list) 


class ScorecardResponse(BaseModel):
    """
    Represents API response payload from
    `analyze.api.tickertape.in/stocks/scorecard/{sid}` endpoint.

    It contains the complete scorecard information for a stock including
    all 6 categories (when available): Performance, Valuation, Growth,
    Profitability, Entry Point, and Red Flags.

    Note:
        - matches the exact API response structure
        - some stocks may have missing categories (success=true but limited data)
        - failed requests return success=false with data=null

    Reference:
        - HTTP Request: GET
        - URL: https://analyze.api.tickertape.in/stocks/scorecard/{sid}
            - where `sid` is the stock's Security ID
        - Response Body: `ScorecardResponse`
    """

    success: bool
    data: Optional[List[ScorecardItem]] = None
