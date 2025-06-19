# Models

## Details and Summary

- Tickertape Models: Pydantic models to hold and map the Tickertape API response for assets list, acting as a schema for the response.
- Tickersnap Models: Pydantic models to hold `Tickersnap` defined models, to work easily with the library data.

=== "Tickertape Models (API Response)"

    ### Assets List

    - Main model: `AssetsListResponse`
    - Depends on: `AssetData`, `AssetType`
        - `AssetData`: holds individual asset information
        - `AssetType`: enum for asset types (stock/ETF)

=== "Tickersnap Models (Library Datatypes)"

    (coming soon)

## Usage

| Model | Source API / Used By | Description | Usage | For Public? |
|-------|------------|-------------|-------|------------|
| `AssetsListResponse` | (GET) api [/stocks/list](https://api.tickertape.in/stocks/list?filter={filter}) | Complete list of assets with filtering | get stocks and ETFs list | ✅ |
| `AssetData` | `AssetsListResponse` | holds individual asset data | (internal use) | ❌ |
| `AssetType` | `AssetData` | asset type enumeration | (internal use) | ❌ |

## Asset Types

- **STOCK**: Individual company stocks
- **ETF**: Exchange Traded Funds

## Filter Options

- **Letters**: 'a'-'z' (case insensitive) - assets starting with that letter
- **Others**: 'others' (case insensitive) - assets not starting with letters  
- **None**: No filter - returns all available assets

## Field Reference

Below is a reference for all the fields found in the assets list API models:

??? info "Model Fields Reference"

    ### 1. Response Structure:

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `success` | Success Status | `bool` | true/false | API response success indicator |
    | `data` | Data Payload | `List[AssetData]` | array | List of asset data objects |

    ### 2. Asset Data Fields:

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `sid` | Security ID | `str` | alphanumeric | Works as the primary key across all Tickertape APIs (financials, news, screeners, etc.), and forms the last part of asset URLs |
    | `name` | Security Name | `str` | text | Human-readable security, company, or fund name |
    | `ticker` | Trading Symbol | `str` | uppercase | What brokers and market feeds show; fixed by the exchange and used in orders |
    | `type` | Asset Type | `AssetType` | stock/etf | Security type (stock or ETF) |
    | `slug` | URL Slug | `str` | lowercase-hyphenated | URL path fragment for Tickertape, useful to directly go to the assets's page on www.tickertape.in |
    | `isin` | International Securities Identification Number | `str` | 12 characters | 12-character, globally unique code defined by ISO 6166; guarantees you are settling the right security even if it trades under different tickers |

    ### 3. Asset Type Enum:

    | Value | Description |
    |-------|-------------|
    | `STOCK` | Individual company stock |
    | `ETF` | Exchange Traded Fund |

::: tickersnap.lists.models
