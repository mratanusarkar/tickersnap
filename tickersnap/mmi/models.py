from datetime import datetime
from enum import Enum
from typing import List, Literal

from pydantic import BaseModel, Field

# --------------------------------------------------------------------------------------
# Tickertape API Models
# --------------------------------------------------------------------------------------


class HistoricalData(BaseModel):
    """
    Represents historical data points of Market Mood Index (MMI).

    This model follows tickertape API response's schema for historical MMI data.
    There are various APIs that returns historic data for day, month, year, etc.
    The schema matches the response structure for all such APIs.

    Note:
        - internal use only
        - used by models: `MMIPeriodData` and `MMINowData`
    """

    date: datetime
    fii: int
    skew: float
    momentum: float
    gold_on_nifty: float = Field(alias="goldOnNifty")
    gold: int
    nifty: float
    extrema: float
    fma: float
    sma: float
    trin: float
    indicator: float
    raw: float
    vix: float


class MMIPeriodData(BaseModel):
    """
    Represents response data from
    `analyze.api.tickertape.in/homepage/mmi?period={period}` endpoint.

    It contains the full MMI information at present,
    along with historic data (day and month only) for the given period (1 to 10).

    Note:
        - internal use only
        - used by models: `MMIPeriodResponse`
    """

    date: datetime
    fii: int
    skew: float
    momentum: float
    gold_on_nifty: float = Field(alias="goldOnNifty")
    gold: int
    nifty: float
    extrema: float
    fma: float
    sma: float
    trin: float
    indicator: float
    raw: float
    vix: float
    days_historical: List[HistoricalData] = Field(alias="daysHistorical")
    months_historical: List[HistoricalData] = Field(alias="monthsHistorical")


class MMIPeriodResponse(BaseModel):
    """
    Represents API response payload from
    `analyze.api.tickertape.in/homepage/mmi?period={period}` endpoint.

    It contains the full MMI information at present,
    along with historic data (day and month only) for the given period (1 to 10).

    Note:
        - best used for getting historic data for a given period.
        - only supports day and month data upto 10 data points max.
        - can be used for observing trends in MMI over time.

    Reference:
        - HTTP Request: GET
        - URL: https://analyze.api.tickertape.in/homepage/mmi?period={period}
            - where `period` is a integer number between 1 and 10.
        - Response Body: `MMIPeriodResponse`
    """

    success: bool
    data: MMIPeriodData


class DailyData(BaseModel):
    """
    Represents daily MMI now data point with value and date.

    Note:
        - internal use only
        - used by models: `MMINowData`
    """

    value: float
    date: datetime


class MMINowData(BaseModel):
    """
    Represents response data from `api.tickertape.in/mmi/now` endpoint.

    It contains the full MMI information at present,
    along with single data points on last date, last week, last month, and last year.

    Note:
        - internal use only
        - used by models: `MMINowResponse`
    """

    date: datetime
    fii: int
    skew: float
    momentum: float
    gold_on_nifty: float = Field(alias="goldOnNifty")
    gold: int
    nifty: float
    extrema: float
    fma: float
    sma: float
    trin: float
    indicator: float
    raw: float
    vix: float
    last_day: HistoricalData = Field(alias="lastDay")
    last_week: HistoricalData = Field(alias="lastWeek")
    last_month: HistoricalData = Field(alias="lastMonth")
    last_year: HistoricalData = Field(alias="lastYear")
    current_value: float = Field(alias="currentValue")
    daily: List[DailyData]


class MMINowResponse(BaseModel):
    """
    Represents API response payload from `api.tickertape.in/mmi/now` endpoint.

    It contains the full MMI information at present,
    along with single data points on last date, last week, last month, and last year.

    Note:
        - best used for getting current MMI value.
        - can be used for comparing current MMI with
            last date, last week, last month, and last year.

    Reference:
        - HTTP Request: GET
        - URL: https://api.tickertape.in/mmi/now
        - Response Body: `MMINowResponse`
    """

    success: bool
    data: MMINowData


# --------------------------------------------------------------------------------------
# Tickersnap User-Facing Models
# --------------------------------------------------------------------------------------


class MMIZone(str, Enum):
    """
    Market Mood Index zones based on indicator value ranges:

    - `00-30`: Extreme Fear
    - `30-50`: Fear
    - `50-70`: Greed
    - `70-100`: Extreme Greed
    """

    EXTREME_FEAR = "Extreme Fear"
    FEAR = "Fear"
    GREED = "Greed"
    EXTREME_GREED = "Extreme Greed"

    @classmethod
    def calculate_zone(cls, value: float) -> "MMIZone":
        """
        Calculate MMI zone based on indicator value.

        Args:
            value (float): The MMI indicator value.

        Returns:
            MMIZone: The MMI zone based on the value.
        """

        if value >= 70:
            return cls.EXTREME_GREED
        elif value >= 50:
            return cls.GREED
        elif value >= 30:
            return cls.FEAR
        else:
            return cls.EXTREME_FEAR


class MMIDataPoint(BaseModel):
    """
    A single MMI data point with date and value.
    """

    date: datetime
    value: float


class MMICurrent(BaseModel):
    """
    The current MMI reading right now.
    contains current MMI value, zone, and date.
    """

    date: datetime
    value: float
    zone: MMIZone


class MMITrends(BaseModel):
    """
    MMI trends over time, with consicutive 10 data points.
    contains current MMI value, date, trends over last 10 days and 10 months.
    """

    current: MMIDataPoint
    last_10_days: List[MMIDataPoint]
    last_10_months: List[MMIDataPoint]


class MMIChanges(BaseModel):
    """
    MMI changes with respect to last day, last week, last month, and last year.
    contains current MMI value, date, and MMI values for
    last day, last week, last month, and last year.
    """

    current: MMIDataPoint
    last_day: MMIDataPoint
    last_week: MMIDataPoint
    last_month: MMIDataPoint
    last_year: MMIDataPoint

    @property
    def vs_last_day(self) -> float:
        return self.current.value - self.last_day.value

    @property
    def vs_last_week(self) -> float:
        return self.current.value - self.last_week.value

    @property
    def vs_last_month(self) -> float:
        return self.current.value - self.last_month.value

    @property
    def vs_last_year(self) -> float:
        return self.current.value - self.last_year.value

    def vs_last(self, period: Literal["day", "week", "month", "year"]) -> float:
        """
        Get difference vs specified period.

        Args:
            period (Literal["day", "week", "month", "year"]):
                The period to compare against.

        Returns:
            float: The difference between the current MMI value
                and the value of the specified period.
        """

        if period == "day":
            return self.vs_last_day
        elif period == "week":
            return self.vs_last_week
        elif period == "month":
            return self.vs_last_month
        elif period == "year":
            return self.vs_last_year
        else:
            raise ValueError(f"Invalid period: {period}")
