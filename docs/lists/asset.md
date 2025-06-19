# Assets

!!! note "Note"

    This module gets full data for all stocks or ETFs or both combined.
    If you want to get data for a specific stock or ETF, use the [AssetsList](./api.md) module.

A high-level Python interface for accessing Tickertape's **complete list of stocks and ETFs** with simplified, user-friendly methods.

It provides simple functions to get filtered lists of all stocks, ETFs, or combined assets for daily market analysis,
with no headache of complex API handling, and distraction free excessive data fields knowledge!

## Overview

!!! tip "Data Coverage"

    - **5,312 total assets** (5,041 stocks + 271 ETFs) listed on Indian stock exchanges as of June 2025.
    - The package will reflect the latest data from Tickertape's comprehensive database.

The `Assets` class provides a clean, intuitive API for accessing asset lists without dealing with complex API responses or field mappings. Perfect for portfolio management, screening applications, market analysis, and financial research.

**Key Features:**

- ✅ **Complete asset coverage** - All stocks and ETFs from Indian exchanges
- ✅ **Smart filtering** - Separate methods for stocks, ETFs, or combined lists  
- ✅ **Essential data only** - Only the fields you need for daily use
- ✅ **Fresh data** - Each call fetches latest asset information
- ✅ **Error handling** - Robust timeout and retry capabilities
- ✅ **Extensive Test Coverage** - A robust CI/CD pipeline to identify changes in Tickertape API.

## Quick Start

!!! example "Get Asset Lists"

    ```python
    from tickersnap.lists import Assets

    # Initialize Assets client
    assets = Assets()

    # Get all stocks
    stocks = assets.get_all_stocks()
    print(f"Total stocks: {len(stocks)}")
    print(f"Sample: {stocks[0].name} ({stocks[0].ticker})")

    # Get all ETFs
    etfs = assets.get_all_etfs()
    print(f"Total ETFs: {len(etfs)}")
    print(f"Sample: {etfs[0].name} ({etfs[0].ticker})")

    # Get all assets (stocks + ETFs)
    all_assets = assets.get_all_assets()
    print(f"Total assets: {len(all_assets)}")
    ```

## Core Methods

=== "All Stocks"

    Get complete list of all stocks listed on Indian exchanges.

    !!! info "Function Signature"

        ```python
        def get_all_stocks() -> List[AssetData]
        ```

    !!! success "Returns"

        - List of all stock assets (~5,041 stocks)
        - Essential fields: sid, name, ticker, slug, isin, type

    !!! example "Example"

        ```python
        assets = Assets()
        stocks = assets.get_all_stocks()

        print(f"Total stocks available: {len(stocks)}")

        # Browse stocks
        for stock in stocks[:5]:
            print(f"{stock.ticker}: {stock.name}")
            print(f"  ISIN: {stock.isin}")
            print(f"  Type: {stock.type}")  # Always 'stock'

        # Filter by name or ticker
        reliance_stocks = [s for s in stocks if 'reliance' in s.name.lower()]
        print(f"Reliance related stocks: {len(reliance_stocks)}")

        # Get specific stock by ticker
        hdfc_stock = next((s for s in stocks if s.ticker == 'HDFCBANK'), None)
        if hdfc_stock:
            print(f"Found: {hdfc_stock.name}")
        ```

=== "All ETFs"

    Get complete list of all ETFs listed on Indian exchanges.

    !!! info "Function Signature"

        ```python
        def get_all_etfs() -> List[AssetData]
        ```

    !!! success "Returns"

        - List of all ETF assets (~271 ETFs)
        - Essential fields: sid, name, ticker, slug, isin, type

    !!! example "Example"

        ```python
        assets = Assets()
        etfs = assets.get_all_etfs()

        print(f"Total ETFs available: {len(etfs)}")

        # Browse ETFs
        for etf in etfs[:5]:
            print(f"{etf.ticker}: {etf.name}")
            print(f"  ISIN: {etf.isin}")
            print(f"  Type: {etf.type}")  # Always 'etf'

        # Filter by category
        nifty_etfs = [e for e in etfs if 'nifty' in e.name.lower()]
        gold_etfs = [e for e in etfs if 'gold' in e.name.lower()]
        
        print(f"Nifty ETFs: {len(nifty_etfs)}")
        print(f"Gold ETFs: {len(gold_etfs)}")

        # Get specific ETF by ticker
        nifty_bees = next((e for e in etfs if e.ticker == 'NIFTYBEES'), None)
        if nifty_bees:
            print(f"Found: {nifty_bees.name}")
        ```

=== "All Assets"

    Get complete list of all assets (stocks + ETFs) in one call.

    !!! info "Function Signature"

        ```python
        def get_all_assets() -> List[AssetData]
        ```

    !!! success "Returns"

        - List of all assets (~5,312 total)
        - Combined stocks and ETFs
        - Essential fields: sid, name, ticker, slug, isin, type

    !!! example "Example"

        ```python
        assets = Assets()
        all_assets = assets.get_all_assets()

        print(f"Total assets: {len(all_assets)}")

        # Categorize by type
        stocks = [a for a in all_assets if a.type == 'stock']
        etfs = [a for a in all_assets if a.type == 'etf']
        
        print(f"Stocks: {len(stocks)} ({len(stocks)/len(all_assets)*100:.1f}%)")
        print(f"ETFs: {len(etfs)} ({len(etfs)/len(all_assets)*100:.1f}%)")

        # Search across all assets
        def search_assets(query):
            return [a for a in all_assets 
                   if query.lower() in a.name.lower() 
                   or query.lower() in a.ticker.lower()]

        tata_assets = search_assets("tata")
        print(f"Tata related assets: {len(tata_assets)}")
        ```

## Configuration

=== "Timeout Settings"

    Set the HTTP request timeout for the underlying API.

    !!! example "Example"

        ```python
        # Default timeout (10 seconds)
        assets = Assets()

        # Custom timeout for slower connections
        assets = Assets(timeout=30)
        ```

=== "Error Handling"

    Handle errors gracefully.

    !!! example "Example"

        ```python
        from tickersnap.lists import Assets

        try:
            assets = Assets(timeout=30)
            stocks = assets.get_all_stocks()
            print(f"Successfully fetched {len(stocks)} stocks")
        except Exception as e:
            print(f"Failed to fetch asset data: {e}")
        ```

## Usage Examples

!!! note "Note"

    - Since this module is meant to just get the list of assets, alone this module doesn't have much usage.
    - The slug fields can be used to directly navigate to www.tickertape.in/stocks/slug or www.tickertape.in/etfs/slug.
    - The sid fields can be used to interact with Tickertape APIs.
    - When combined with other modules from `Tickeersnap`, it can get very powerful for automated analysis!

## Data Fields

Each asset contains the following essential information:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `sid` | string | Tickertape security identifier | "RELIANCE" |
| `name` | string | Full company/fund name | "Reliance Industries Ltd" |
| `ticker` | string | Exchange trading symbol | "RELIANCE" |
| `type` | AssetType | Asset type (stock/etf) | "stock" |
| `slug` | string | URL path for Tickertape | "reliance-industries-ltd" |
| `isin` | string | International identifier | "INE002A01018" |

> See [Models](./models.md#field-reference) (field-reference section) for more details.

---

::: tickersnap.lists.asset 