# Models

## Details and Summary

- Tickertape Models: Pydantic models to hold and map the Tickertape API response, acting as a schema for the response.
- Tickersnap Models: Pydantic models to hold `Tickersnap` defined models, to work easily with the library data.

=== "Tickertape Models (API Response)"

    ### MMI Period

    - Main model: `MMIPeriodResponse`
    - Depends on: `MMIPeriodData`, `HistoricalData`
        - `MMIPeriodData`: holds the main MMI data
        - `HistoricalData`: holds the historical data


    ### MMI Now

    - Main model: `MMINowResponse`
    - Depends on: `MMINowData`, `HistoricalData`, `DailyData`
        - `MMINowData`: holds the main MMI data
        - `HistoricalData`: holds the historical data
        - `DailyData`: holds the daily data

=== "Tickersnap Models (Library Datatypes)"

    ### MMI Current

    - Main model: `MMICurrent`
    - Depends on: `MMIZone`
        - `MMIZone`: holds the MMI zone enum

    ### MMI Trends

    - Main model: `MMITrends`
    - Depends on: `MMIDataPoint`
        - `MMIDataPoint`: holds the MMI data point (date and value)

    ### MMI Changes

    - Main model: `MMIChanges`
    - Depends on: `MMIDataPoint`
        - `MMIDataPoint`: holds the MMI data point (date and value)

## Usage

| Model | Source API / Used By | Description | Usage | For Public? |
|-------|------------|-------------|-------|------------|
| `MMIPeriodResponse` | (GET) analyze [/homepage/mmi](https://analyze.api.tickertape.in/homepage/mmi?period=1) | MMI data for a given period | get mmi data + historic data in series | ✅ |
| `MMINowResponse` | (GET) api [/mmi/now](https://api.tickertape.in/mmi/now) | Current MMI data | current mmi data + past data for comparison | ✅ |
| `MMIPeriodData` | `MMIPeriodResponse` | holds main data payload | (internal use) | ❌ |
| `MMINowData` | `MMINowResponse` | holds the main MMI data | (internal use) | ❌ |
| `DailyData` | `MMINowData` | holds the daily data | (internal use) | ❌ |
| `HistoricalData` | `MMIPeriodData`, `MMINowData` | holds the historical data | (internal use) | ❌ |

## MMI Zones

- **0-30**: Extreme Fear (Good time to buy)
- **30-50**: Fear (Monitor trend)
- **50-70**: Greed (Consider selling)
- **70-100**: Extreme Greed (Avoid fresh positions)

## Field Reference

Below is a combined reference for all the fields found in all the API related (tickertape) models, grouped by logical sections:

??? info "Model Fields Reference"

    ### 1. Core MMI Data:

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `indicator` | Market Mood Indicator | `float` | 0-100 | Final MMI sentiment value (0=Extreme Fear, 100=Extreme Greed) |
    | `raw` | Raw MMI Value | `float` | varies | Raw MMI calculation before smoothing/normalization |
    | `current_value` | Current MMI Value | `float` | 0-100 | Current MMI value (same as indicator in MMINow) |

    ### 2. Market Sentiment Factors:

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `fii` | Foreign Institutional Investor | `int` | negative/positive | FII net flows in ₹ crores (negative=selling, positive=buying) |
    | `vix` | Volatility Index | `float` | varies | India VIX volatility index (market fear gauge) |
    | `skew` | Options Skew | `float` | varies | Options skew indicating market direction expectations |
    | `momentum` | Price Momentum | `float` | varies | Price momentum using moving average ratios |
    | `extrema` | Market Extrema | `float` | 0-1 | Market breadth ratio (52-week highs vs lows) |
    | `trin` | Trading Index | `float` | varies | TRIN (advance/decline + volume ratio) |
    | `gold_on_nifty` | Gold to Nifty Ratio | `float` | varies | Gold vs Nifty performance ratio (safe haven demand) |

    ### 3. Market Data:

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `nifty` | Nifty 50 Index | `float` | 20,000-30,000 | Current Nifty 50 index value |
    | `gold` | Gold Price | `int` | 60,000-100,000+ | Gold price per 10g in ₹ |
    | `fma` | Fast Moving Average | `float` | positive | Fast Moving Average of Nifty |
    | `sma` | Slow Moving Average | `float` | positive | Slow Moving Average of Nifty |

    ### 4. Timestamps:

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `date` | Date/Time | `datetime` | ISO format | Data timestamp in UTC |

    ### 5. Response Structure:

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `success` | Success Status | `bool` | true/false | API response success indicator |
    | `data` | Data Payload | `object` | - | Main data payload container |

    ### 6. Historical Arrays:

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `days_historical` | Daily Historical Data | `List[HistoricalData]` | 1-10 items | Historical daily MMI data points |
    | `months_historical` | Monthly Historical Data | `List[HistoricalData]` | 1-10 items | Historical monthly MMI data points |
    | `daily` | Daily Data Series | `List[DailyData]` | varies | Daily MMI value time series |

    ### 7. Comparison Fields (MMINow only):

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `last_day` | Previous Day Data | `HistoricalData` | - | MMI data from previous trading day |
    | `last_week` | Previous Week Data | `HistoricalData` | - | MMI data from one week ago |
    | `last_month` | Previous Month Data | `HistoricalData` | - | MMI data from one month ago |
    | `last_year` | Previous Year Data | `HistoricalData` | - | MMI data from one year ago |

::: tickersnap.mmi.models