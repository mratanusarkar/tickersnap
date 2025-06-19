from enum import Enum
from typing import List

from pydantic import BaseModel

# --------------------------------------------------------------------------------------
# Tickertape API Models + Tickersnap User-Facing Model: AssetData
# --------------------------------------------------------------------------------------


class AssetType(str, Enum):
    """
    Asset type (stock/ETF)

    - `STOCK`: stock (for stocks)
    - `ETF`: etf (for exchange traded funds)
    """

    STOCK = "stock"
    ETF = "etf"


class AssetData(BaseModel):
    """
    Represents a single security (stock/ETF) data point.

    This model follows tickertape API response's schema for list of assets data.
    Each asset contains basic information like SID, name, ticker, type, slug, and ISIN.

    Field Descriptions:
        - sid: Security ID (tickertape's own identifier)
        - name: Security name (exchange name/company name)
        - ticker: Exchange/Trading symbol
        - type: Security type (stock/ETF)
        - slug: URL path fragment in tickertape
        - isin: International Securities Identification Number (ISIN)

    Note:
        - internal use only
        - used by models: `AssetsListResponse`
    """

    sid: str
    name: str
    ticker: str
    type: AssetType
    slug: str
    isin: str


class AssetsListResponse(BaseModel):
    """
    Represents API response payload from
    `api.tickertape.in/stocks/list?filter={filter}` endpoint.

    It contains a list of securities (stocks and ETFs) that match the filter criteria.
    When no filter is provided, it returns the complete list of all assets.

    Note:
        - matches the exact API response structure
        - filter can be 'a'-'z' (case insensitive) or 'others'
        - no filter returns complete list

    Reference:
        - HTTP Request: GET
        - URL: https://api.tickertape.in/stocks/list?filter={filter}
            - where `filter` is optional and can be 'a'-'z' or 'others'
        - Response Body: `AssetsListResponse`
    """

    success: bool
    data: List[AssetData]
