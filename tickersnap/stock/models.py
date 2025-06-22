from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from ..lists.models import AssetData

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
        - some fields can be missing (`None`)
            for some stocks when the data is not available
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
        - some fields can be missing (`None`)
            for some stocks when the data is not available
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
    Individual scorecard category item
    (Performance, Valuation, Growth, Profitability, Entry Point, Red Flags).

    This model follows tickertape API response's schema for individual scorecard items.
    Each item represents one of the 6 scorecard categories with their respective data.

    Note:
        - internal use only
        - used by models: `ScorecardResponse`

    Disclaimer:
        - some fields can be missing (`None`)
            for some stocks when the data is not available
        - `score` will be `None` for "entry point" and "red flag" types
        - `elements` will be empty
            for "performance", "valuation", "growth", "profitability" types
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
        - URL: https://analyze.api.tickertape.in/stocks/scorecard/{sid},
            (where `sid` is the stock's Security ID)
        - Response Body: `ScorecardResponse`
    """

    success: bool
    data: Optional[List[ScorecardItem]] = None


# --------------------------------------------------------------------------------------
# Tickersnap User-Facing Models (Scorecard)
# --------------------------------------------------------------------------------------


class ScoreRating(str, Enum):
    """
    Unified rating system for all scorecard categories and elements.

    Provides a simple good/bad classification for any scorecard data point,
    making it easy for users to quickly assess stock conditions without
    needing to interpret complex financial metrics.

    Values:
        - GOOD: Positive indicator (green signals, favorable conditions)
        - OKAY: Neutral indicator (yellow/orange signals, average conditions)
        - BAD: Negative indicator (red signals, unfavorable conditions)
        - UNKNOWN: Missing/insufficient data or unable to determine rating
    """

    GOOD = "good"
    OKAY = "okay"
    BAD = "bad"
    UNKNOWN = "unknown"


class Score(BaseModel):
    """
    Represents a single scorecard data point with simplified user-friendly information.

    Used for both main categories (Performance, Valuation, etc.) and individual
    elements within Entry Point and Red Flags. Provides consistent structure
    across all scorecard data.

    Field Descriptions:
        - `name`: Display name of the scorecard item
        - `description`: Human-readable explanation of what this measures
        - `value`: The actual value/tag from the API (e.g., "High", "Low", "Good")
        - `rating`: Simplified good/bad/okay/unknown classification

    Note:
        - value can be None when data is not available
        - rating helps users quickly understand if something is positive or negative
        - consistent structure for both categories and elements
    """

    name: str
    description: str
    value: Optional[str] = None
    rating: ScoreRating


class StockScores(BaseModel):
    """
    Complete scorecard information (simplified) for a stock.

    Provides end-user focused access to all 6 scorecard categories with
    simplified good/bad ratings. Removes API complexity and presents
    data in an intuitive format for quick stock analysis.

    Categories:
        - Core Financial: performance, valuation, growth, profitability
        - Trading Focused: entry_point, red_flags (with detailed elements)

    Field Descriptions:
        - `performance`: Overall stock performance rating
        - `valuation`: Stock valuation assessment (expensive/cheap)
        - `growth`: Company growth prospects rating
        - `profitability`: Company profitability assessment
        - `entry_point`: Current entry timing assessment
        - `entry_point_elements`: Detailed entry point factors (List[Score])
        - `red_flags`: Overall red flags assessment
        - `red_flags_elements`: Detailed red flag factors (List[Score])

    Note:
        - All fields are Optional as some stocks may have missing categories
        - Elements provide detailed breakdown for entry_point and red_flags
        - Missing categories will be None (not populated)
        - Use rating field for quick good/bad assessment
    """

    # core financial categories
    performance: Optional[Score] = None
    valuation: Optional[Score] = None
    growth: Optional[Score] = None
    profitability: Optional[Score] = None

    # trading categories and their detailed elements
    entry_point: Optional[Score] = None
    entry_point_elements: Optional[List[Score]] = None

    red_flags: Optional[Score] = None
    red_flags_elements: Optional[List[Score]] = None


class StockWithScorecard(BaseModel):
    """
    Combined asset information with scorecard data.

    Provides a unified view of stock asset information along with scorecard analysis.
    This model combines the essential stock details (from AssetData) with the
    comprehensive scorecard evaluation (from StockScores).

    Field Descriptions:
        - `asset`: Complete stock asset information (SID, name, ticker, etc.)
        - `scorecard`: Scorecard analysis data (None if unavailable/failed)

    Use Cases:
        - Bulk stock analysis with both basic info and scorecard data
        - Portfolio screening with combined asset and performance metrics
        - Quick stock evaluation with all relevant data in one object

    Note:
        - scorecard can be None if the API call failed or data is unavailable
        - asset information is always present (from the input AssetData)
        - Follows composition pattern for clear data separation
    """

    asset: AssetData
    scorecard: Optional[StockScores] = None
