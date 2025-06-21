"""
MarketMoodIndex - Daily MMI Data for Market Analysis

MMI data that a common user might want to see:

- before market opens,
- in between market hours,
- after market closes.

Provides 3 key functions:

- `get_current_mmi()`: Current MMI value with zone classification
- `get_mmi_trends()`: MMI trends for charting (10 days + 10 months)
- `get_mmi_changes()`: MMI changes for comparison analysis
"""

from .api import MMINowAPI, MMIPeriodAPI
from .models import (
    MMIChanges,
    MMICurrent,
    MMIDataPoint,
    MMINowData,
    MMIPeriodData,
    MMITrends,
    MMIZone,
)


class MarketMoodIndex:
    """
    Simplified daily usage and utility focused MMI data for market analysis.

    It removes the Tickertape API complexity and unnecessary field data points,
    and provides simple functions to get purely the MMI data
    that a common user might want to see or use for their daily market analysis.
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize MarketMoodIndex.

        Args:
            timeout (int): Request timeout in seconds. Defaults to 10.
        """

        self.timeout = timeout

    def get_current_mmi(self) -> MMICurrent:
        """
        Get current MMI value with zone classification.

        Returns:
            MMICurrent: Current MMI value, zone, and date.
        """

        with MMINowAPI(timeout=self.timeout) as client:
            response = client.get_data()

        data = response.data
        zone = MMIZone.calculate_zone(data.indicator)

        return MMICurrent(date=data.date, value=data.indicator, zone=zone)

    def get_mmi_trends(self) -> MMITrends:
        """
        Get MMI trend series data for graphing and analysis.

        Fetches the current MMI + last 10 days + last 10 months of data,
        which can be useful for trend analysis and graphing.

        Returns:
            MMITrends: Current MMI + last 10 days + last 10 months of historical data.
        """

        with MMIPeriodAPI(timeout=self.timeout) as client:
            response = client.get_data(period=10)

        data = response.data

        # convert historical data to MMIDataPoint
        last_10_days = [
            MMIDataPoint(date=item.date, value=item.indicator)
            for item in data.days_historical
        ]

        last_10_months = [
            MMIDataPoint(date=item.date, value=item.indicator)
            for item in data.months_historical
        ]

        # convert current data to MMIDataPoint
        current = MMIDataPoint(date=data.date, value=data.indicator)

        return MMITrends(
            current=current, last_10_days=last_10_days, last_10_months=last_10_months
        )

    def get_mmi_changes(self) -> MMIChanges:
        """
        Get MMI comparison data against aggregated historical periods.

        Provides current MMI value along with values from last day,
        last week, last month, and last year for comparison or delta change analysis.

        Returns:
            MMIChanges: Current and historical MMI values with comparison properties.
        """

        with MMINowAPI(timeout=self.timeout) as client:
            response = client.get_data()

        data = response.data

        current = MMIDataPoint(date=data.date, value=data.indicator)
        last_day = MMIDataPoint(date=data.last_day.date, value=data.last_day.indicator)
        last_week = MMIDataPoint(
            date=data.last_week.date, value=data.last_week.indicator
        )
        last_month = MMIDataPoint(
            date=data.last_month.date, value=data.last_month.indicator
        )
        last_year = MMIDataPoint(
            date=data.last_year.date, value=data.last_year.indicator
        )

        return MMIChanges(
            current=current,
            last_day=last_day,
            last_week=last_week,
            last_month=last_month,
            last_year=last_year,
        )

    def get_raw_current_data(self) -> MMINowData:
        """
        Get raw tickertape api response for current MMI data.

        Disclaimer:
            - Advanced users only - contains all API fields.
            - For daily use, prefer `get_mmi_changes()` instead.

        Returns:
            MMINowData: raw data returned by Tickertape API.
        """

        with MMINowAPI(timeout=self.timeout) as client:
            response = client.get_data()

        return response.data

    def get_raw_period_data(self, period: int = 4) -> MMIPeriodData:
        """
        Get raw tickertape api response for MMI data over a period.

        Disclaimer:
            - Advanced users only - contains all API fields.
            - For daily use, prefer `get_mmi_trends()` instead.

        Args:
            period (int): Number of days and months to fetch. Defaults to 4.

        Returns:
            MMIPeriodData: raw data returned by Tickertape API.
        """

        with MMIPeriodAPI(timeout=self.timeout) as client:
            response = client.get_data(period=period)

        return response.data
