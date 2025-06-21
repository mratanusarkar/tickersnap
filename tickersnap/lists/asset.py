"""
Assets - Common usage focused List of Assets Data

Provides simplified access to stocks and ETFs data for common daily usage:

- `get_all_stocks()`: list of all stocks listed in India
- `get_all_etfs()`: list of all ETFs listed in India
- `get_all_assets()`: list of all assets (stocks and ETFs) listed in India

Removes API complexity and provides clean, filtered lists for daily market analysis.
"""

from typing import List

from .api import AssetsListAPI
from .models import AssetData, AssetType


class Assets:
    """
    Simplified common usage focused assets data for market analysis.

    Provides clean access to stocks and ETFs data without API complexity.

    Returns only the essential fields needed for daily use: sid, name, ticker,
    slug, isin (and type when getting all assets).
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize Assets client.

        Args:
            timeout (int): Request timeout in seconds. Defaults to 10.
        """

        self.timeout = timeout

    def get_all_stocks(self) -> List[AssetData]:
        """
        Get all available stocks.

        Returns:
            List[AssetData]: List of all stock assets with essential fields.
        """

        with AssetsListAPI(timeout=self.timeout) as client:
            response = client.get_data()

        return [asset for asset in response.data if asset.type == AssetType.STOCK]

    def get_all_etfs(self) -> List[AssetData]:
        """
        Get all available ETFs.

        Returns:
            List[AssetData]: List of all ETF assets with essential fields.
        """

        with AssetsListAPI(timeout=self.timeout) as client:
            response = client.get_data()

        return [asset for asset in response.data if asset.type == AssetType.ETF]

    def get_all_assets(self) -> List[AssetData]:
        """
        Get all available assets (stocks + ETFs).

        Returns:
            List[AssetData]: List of all assets with essential fields including type.
        """

        with AssetsListAPI(timeout=self.timeout) as client:
            response = client.get_data()

        return response.data
