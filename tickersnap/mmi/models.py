from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


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
