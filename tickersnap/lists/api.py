"""
Tickersnap Assets List Client

A module for accessing list of all available assets (stocks and ETFs)
from the Tickertape API.

This module provides a streamlined way to fetch lists of stocks and ETFs
from Tickertape, with optional filtering capabilities.

Features:
    - Fetch complete list of all available assets (stocks and ETFs)
    - Filter assets by starting letter ('a'-'z') or 'others'
    - Preserve and access the original tickertape API response structure
    - Simple client interface with proper error handling
"""

from typing import Optional

import httpx
from pydantic import ValidationError

from .models import AssetsListResponse


class AssetsListAPI:
    """
    Client for fetching assets list data from Tickertape.

    Supports fetching the complete list of stocks and ETFs, or filtering by
    starting letter. The filter can be any letter from 'a' to 'z' (case insensitive)
    or 'others' (case insensitive) for assets that don't start with letters.

    - BASE_URL: "https://api.tickertape.in/stocks/list"

    Example:
        ```python
        # Using as a client object (don't forget to close)
        assets = AssetsListAPI()
        data = assets.get_data()  # Get all assets
        data_filtered = assets.get_data(filter='a')  # Get assets starting with 'a'
        assets.close()
        ```

        ```python
        # Using as context manager (automatically closed)
        with AssetsListAPI() as assets:
            data = assets.get_data(filter='x')
            print(f"Found {len(data.data)} assets")
        ```
    """

    BASE_URL = "https://api.tickertape.in/stocks/list"
    VALID_LETTERS = set("abcdefghijklmnopqrstuvwxyz")
    VALID_OTHERS = {"others"}
    VALID_FILTERS = VALID_LETTERS | VALID_OTHERS
    VALID_FILTERS_SORTED_LIST = sorted(VALID_LETTERS) + list(VALID_OTHERS)

    def __init__(self, timeout: int = 10):
        """
        Initialize the Assets List client.

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

    def get_data(self, filter: Optional[str] = None) -> AssetsListResponse:
        """
        Fetch all available list of assets (stocks and ETFs) from Tickertape,
        with optional filtering by starting letter or 'others'.

        Args:
            filter (Optional[str]): Filter to apply. Can be:

                - Any letter `'a'` to `'z'` (case insensitive):
                    assets starting with that letter
                - `'others'` (case insensitive): assets not starting with letters
                - None (default): fetch all assets

        Returns:
            AssetsListResponse: Parsed API response containing list of assets.

        Raises:
            ValueError: If filter is not a valid option.
            Exception: If HTTP request fails or data validation fails.
        """

        # input filter parameter validation and normalization
        if filter is not None:
            # validate filter is not empty or contains whitespaces
            filter_stripped = filter.strip()
            if filter_stripped == "":
                raise ValueError(
                    f"Empty filter '{filter}' not allowed. "
                    f"Use filter=None or omit the parameter to get all assets. "
                    f"Valid filters: {', '.join(self.VALID_FILTERS_SORTED_LIST)}"
                )

            # validate filter does not contain leading or trailing whitespaces
            if filter_stripped != filter:
                raise ValueError(
                    f"Filter '{filter}' contains leading or trailing whitespaces. "
                    f"Please remove the whitespaces and try again with correct filter. "
                    f"Valid filters: {', '.join(self.VALID_FILTERS_SORTED_LIST)}"
                )

            # validate and normalize filter to accept both upper and lower case letters
            filter_lower = filter.lower()
            if filter_lower not in self.VALID_FILTERS:
                raise ValueError(
                    f"Invalid filter '{filter}'. Valid options are: "
                    f"{', '.join(self.VALID_FILTERS_SORTED_LIST)}. "
                    f"All filters are case insensitive."
                )
            filter = filter_lower

        try:
            # build request parameters
            params = {}
            if filter is not None:
                params["filter"] = filter

            response = self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            json_res = response.json()

            return AssetsListResponse.model_validate(json_res)

        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP {e.response.status_code} error: {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Request failed: {e}")
        except ValidationError as e:
            raise Exception(f"Data validation error: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")
