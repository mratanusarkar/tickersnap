"""
Tickersnap Stock Scorecard Client

A module for accessing stock scorecard data from the Tickertape API.

This module provides a streamlined way to fetch stock scorecard information
including performance, valuation, growth, profitability, entry point, and red flags.

Features:
    - Fetch complete scorecard data for any stock by SID
    - Automatic handling of missing categories and failed requests
    - Preserve and access the original tickertape API response structure
    - Simple client interface with proper error handling
"""

import httpx
from pydantic import ValidationError

from .models import ScorecardResponse


class StockScorecardAPI:
    """
    Client for fetching stock scorecard data from Tickertape.

    Supports fetching complete scorecard information for any stock using its SID.
    The scorecard includes 6 categories: Performance, Valuation, Growth,
    Profitability, Entry Point, and Red Flags (when available).

    - BASE_URL: "https://analyze.api.tickertape.in/stocks/scorecard"

    Example:
        ```python
        # Using as a client object (don't forget to close)
        scorecard = StockScorecardAPI()
        data = scorecard.get_data("TCS")
        print(data.success)
        scorecard.close()
        ```

        ```python
        # Using as context manager (automatically closed)
        with StockScorecardAPI() as scorecard:
            data = scorecard.get_data("TCS")
            if data.success and data.data:
                print(f"Found {len(data.data)} scorecard categories")
        ```
    """

    BASE_URL = "https://analyze.api.tickertape.in/stocks/scorecard"

    def __init__(self, timeout: int = 10):
        """
        Initialize the Stock Scorecard API client.

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

    def get_data(self, sid: str) -> ScorecardResponse:
        """
        Fetch stock scorecard data from Tickertape.

        Args:
            sid (str): Stock SID (Security ID) as used by Tickertape.
                Example: "TCS", "RELI", "INFY"

        Returns:
            ScorecardResponse: Raw API response or None if request fails.

        Raises:
            ValueError: If SID is empty or invalid.
            Exception: If HTTP request fails or data validation fails.
        """

        # Validate SID
        if not sid or not sid.strip():
            raise ValueError("SID cannot be empty")

        sid = sid.strip()

        try:
            url = f"{self.BASE_URL}/{sid}"
            response = self.client.get(url)
            response.raise_for_status()
            json_res = response.json()

            return ScorecardResponse.model_validate(json_res)

        except httpx.HTTPStatusError as e:
            raise Exception(
                f"HTTP {e.response.status_code}, "
                f"check 'sid' parameter, error: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise Exception(f"Request failed: {e}")
        except ValidationError as e:
            raise Exception(f"Data validation error: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")
