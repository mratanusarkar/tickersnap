"""
Tickersnap Market Mood Index (MMI) Client

A module for accessing Market Mood Index data from the Tickertape API.

This module provides a streamlined way to fetch, process, and work with MMI data,
while maintaining the integrity of the original API responses,
as well as providing a utility-focused classes and functions to work with MMI data.

Features:
    - Simplified data access through intuitive classes and functions
    - Comprehensive MMI data retrieval including historical data
    - Preserve and access the original tickertape API response structure
    - Utility-focused design from tickersnap for simple workflow with MMI data
"""

from typing import Optional

import httpx
from pydantic import ValidationError

from .models import MMINowResponse, MMIPeriodResponse


class MMIPeriodAPI:
    """
    Client for fetching Market Mood Index (MMI) data for specified periods.

    Supports fetching current MMI data along with historical data (days and months)
    for periods ranging from 1 to 10 data points.

    - BASE_URL: "https://analyze.api.tickertape.in/homepage/mmi?period=4"

    Example:
        ```python
        # Using as a client object (don't forget to close)
        mmi = MMIPeriodAPI()
        data = mmi.get_data(period=1)
        print(data.data.indicator)
        mmi.close()
        ```

        ```python
        # Using as context manager (automatically closed)
        with MMIPeriodAPI() as mmi:
            data = mmi.get_data(period=1)
            print(data.data.indicator)
        ```
    """

    BASE_URL = "https://analyze.api.tickertape.in/homepage/mmi"
    DEFAULT_PERIOD = 4
    MIN_PERIOD = 1
    MAX_PERIOD = 10

    def __init__(self, timeout: int = 10):
        """
        Initialize the MMI Period client.

        Args:
            timeout (int): Request timeout in seconds. Defaults to 10.
        """

        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def __enter__(self):
        """
        Context manager entry.
        """

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        """

        self.close()

    def close(self):
        """
        Close the HTTP client.
        """

        self.client.close()

    def get_data(self, period: Optional[int] = None) -> MMIPeriodResponse:
        """
        Fetch MMI data for the specified period.

        Args:
            period (Optional[int]): Number of historical data points to fetch (1-10).
                Defaults to DEFAULT_PERIOD (4) if not specified.

        Returns:
            MMIPeriodResponse: Parsed API response containing
                current and historical MMI data.

        Raises:
            ValueError: If period is not between MIN_PERIOD and MAX_PERIOD.
            Exception: If HTTP request fails or data validation fails.
        """

        if period is None:
            period = self.DEFAULT_PERIOD

        if not (self.MIN_PERIOD <= period <= self.MAX_PERIOD):
            raise ValueError(
                f"Period must be between {self.MIN_PERIOD} and {self.MAX_PERIOD}, "
                f"got {period}"
            )

        try:
            response = self.client.get(
                self.BASE_URL,
                params={"period": period},
            )
            response.raise_for_status()
            json_res = response.json()

            return MMIPeriodResponse.model_validate(json_res)

        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP {e.response.status_code} error: {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Request failed: {e}")
        except ValidationError as e:
            raise Exception(f"Data validation error: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")


class MMINowAPI:
    """
    Client for fetching the current Market Mood Index (MMI) data.

    Supports fetching the full MMI information at present,
    along with single data points on last date, last week, last month, and last year.

    - BASE_URL: https://api.tickertape.in/mmi/now
    """

    BASE_URL = "https://api.tickertape.in/mmi/now"

    def __init__(self, timeout: int = 10):
        """
        Initialize the MMI Now client.

        Args:
            timeout (int): Request timeout in seconds. Defaults to 10.
        """

        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def __enter__(self):
        """
        Context manager entry.
        """

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        """

        self.close()

    def close(self):
        """
        Close the HTTP client.
        """

        self.client.close()

    def get_data(self) -> MMINowResponse:
        """
        Fetch the current MMI data.

        Returns:
            MMINowResponse: Parsed API response containing current and
                past stats of MMI.

        Raises:
            Exception: If HTTP request fails or data validation fails.
        """

        try:
            response = self.client.get(self.BASE_URL)
            response.raise_for_status()
            json_res = response.json()

            return MMINowResponse.model_validate(json_res)

        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP {e.response.status_code} error: {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Request failed: {e}")
        except ValidationError as e:
            raise Exception(f"Data validation error: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")
