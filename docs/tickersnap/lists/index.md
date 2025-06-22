# Assets List

**Tickersnap** (this python package) provides complete access to all stocks and ETFs listed on Indian stock exchanges.

## Overview

The Assets List module provides comprehensive coverage of the Indian equity market with **5,312 total assets** (5,041 stocks + 271 ETFs) listed on Indian stock exchanges as of June 2025.

!!! note "Note"
    This is dynamic and sources its data from Tickertape's comprehensive database,
    hence the data is always up to date and the above numbers might change over time.

## Disclaimers

!!! warning "Disclaimer"

    - Since this module is meant to just get the list of assets, alone this module doesn't have much usage.
    - The `slug` fields can be used to directly navigate to www.tickertape.in/stocks/slug or www.tickertape.in/etfs/slug.
    - The `sid` fields can be used to interact with Tickertape APIs.
    - **When combined with other modules from `Tickersnap`, it can get very powerful for automated analysis!**

!!! danger "Disclaimer"

    The stock and ETF data provided through this module is for informational purposes only.
    Not financial advice. Always consult qualified financial advisors before making investment decisions.

## Modules

| Module | Description | Target Audience | For Public Use | When to use? |
|--------|-------------|-----------------|----------------|----------------|
| [Assets](asset.md) | High-level asset lists | General Users | ✅ | When you want to get the list of all stocks or ETFs or both combined |
| [API](api.md) | Raw API access | Advanced Users | ✅ | When you want to get combined data filtered by starting with a letter |
| [Models](models.md) | Data models | Internal Use | ❌ | NA |

## Usage Examples
