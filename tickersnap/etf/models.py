from enum import Enum
from typing import Any, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field

from ..lists.models import AssetData

# --------------------------------------------------------------------------------------
# Tickertape API Models (ETF Scorecard)
# --------------------------------------------------------------------------------------


class SourceData(BaseModel):
    """
    Source data information for ETF scorecard elements.

    This model follows tickertape API response's schema for source data
    within ETF scorecard elements (typically RSI data).

    Note:
        - internal use only
        - used by models: `ETFScorecardElement`
        - contains technical indicator data and thresholds

    Disclaimer:
        - some fields can be missing (`None`)
            for some ETFs when the data is not available
    """

    key: str
    max: Optional[Any] = None
    percentage: bool
    value: str


class ETFScorecardElement(BaseModel):
    """
    Individual element within ETF scorecard Entry Point category.

    This model follows tickertape API response's schema for elements data
    within the entry point category for ETFs.

    Note:
        - internal use only
        - used by models: `ETFScorecardItem`
        - used only in "elements" field of: entry_point
        - contains technical analysis data (RSI, etc.)

    Disclaimer:
        - some fields can be missing (`None`)
            for some ETFs when the data is not available
    """

    type: str
    title: str
    description: str
    flag: str
    display: bool
    score: Optional[Any] = None
    source: SourceData


class ETFScorecardItem(BaseModel):
    """
    Individual ETF scorecard category item
    (Performance, Risk, Cost, Entry Point).

    This model follows tickertape API response's schema for individual ETF scorecard items.
    Each item represents one of the 4 ETF scorecard categories with their respective data.

    Note:
        - internal use only
        - used by models: `ETFScorecardResponse`

    Disclaimer:
        - some fields can be missing (`None`)
            for some ETFs when the data is not available
        - `elements` will be empty for "performance", "risk", "cost" types
        - `elements` will contain RSI data for "entry point" type
        - `lastUpdated` only appears in "entry point" items
    """

    name: str
    tag: str
    type: str
    description: str
    colour: str
    locked: bool
    score: Optional[Any] = None
    rank: Optional[int] = None
    peers: Optional[int] = None
    callout: Optional[Any] = None
    comment: Optional[str] = None
    stack: Optional[Any] = None
    elements: List[ETFScorecardElement] = Field(default_factory=list)
    lastUpdated: Optional[str] = None


class ETFScorecardResponse(BaseModel):
    """
    Represents API response payload from
    `analyze.api.tickertape.in/etfs/scorecard/{sid}` endpoint.

    It contains the complete ETF scorecard information including
    all 4 categories: Performance, Risk, Cost, and Entry Point.

    Note:
        - matches the exact API response structure
        - all ETFs have consistent 4-category structure
        - 100% success rate observed across all 281 ETFs

    Reference:
        - HTTP Request: GET
        - URL: https://analyze.api.tickertape.in/etfs/scorecard/{sid},
            (where `sid` is the ETF's Security ID)
        - Response Body: `ETFScorecardResponse`
    """

    success: bool
    data: List[ETFScorecardItem]
