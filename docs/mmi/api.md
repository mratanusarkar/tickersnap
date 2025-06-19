# API Reference

## Overview

The MMI API provides programmatic access to Tickertape's Market Mood Index data through two main endpoints.
This unofficial Python client wraps the Tickertape APIs with robust error handling and response validation.

**Base URLs and Request Types:**

| API | Request Type | Base URL | Response Type |
|-----|--------------|----------|---------------|
| Period Data | GET | `https://analyze.api.tickertape.in/homepage/mmi?period={period}` | JSON (application/json) |
| Current Data | GET | `https://api.tickertape.in/mmi/now` | JSON (application/json) |

**Headers:**

- **Authentication:** None required
- **Rate Limiting:** Not specified by Tickertape
- **Response Format:** JSON (application/json)

## API Details

??? info "MMI Period Data"

    ### 1. MMI Period

    #### 1.1 API Details:

    Retrieve MMI data with historical time series for a specified period.

    **Endpoint:** `GET /homepage/mmi`  
    **Base URL:** `https://analyze.api.tickertape.in`  
    **Full URL:** `https://analyze.api.tickertape.in/homepage/mmi?period={period}`

    #### 1.2 Parameters:

    | Parameter | Type | Required | Range | Default | Description |
    |-----------|------|----------|-------|---------|-------------|
    | `period` | integer | No | 1-10 | 4 | Number of historical data points to return |

    #### 1.3 Request Example:

    ```bash
    curl -X GET "https://analyze.api.tickertape.in/homepage/mmi?period=1"
    ```

    #### 1.4 Python Usage:

    === "MMIPeriod"

        ```python
        from tickersnap.mmi import MMIPeriod

        # Basic usage
        with MMIPeriod() as client:
            response = client.get_data(period=1)
            print(f"Current MMI: {response.data.indicator}")
            print(f"Historical days: {len(response.data.days_historical)}")

        # With custom timeout
        with MMIPeriod(timeout=30) as client:
            response = client.get_data()  # Uses default period=4
        ```

    #### 1.5 Response Schema:

    ```json
    {
    "success": true,
    "data": {
        "date": "2025-06-17T05:39:00.065Z",
        "indicator": 52.02,
        "fii": -101743,
        "vix": -14.45,
        "nifty": 24874.55,
        "gold": 97321,
        "daysHistorical": [...],
        "monthsHistorical": [...]
    }
    }
    ```

    #### 1.6 Response Fields:

    - **success** (boolean): API call status
    - **data** (object): Main payload containing current MMI and historical data
    - **data.indicator** (float): Current MMI value (0-100)
    - **data.daysHistorical** (array): Daily historical data points
    - **data.monthsHistorical** (array): Monthly historical data points

??? info "MMI Now Data"

    ### 2. MMI Now

    #### 2.1 API Details:

    Retrieve current MMI data with historical comparisons (day, week, month, year).

    **Endpoint:** `GET /mmi/now`  
    **Base URL:** `https://api.tickertape.in`  
    **Full URL:** `https://api.tickertape.in/mmi/now`

    #### 2.2 Parameters:

    None required.

    #### 2.3 Request Example:

    ```bash
    curl -X GET "https://api.tickertape.in/mmi/now"
    ```

    #### 2.4 Python Usage:

    === "MMINow"

        ```python
        from tickersnap.mmi import MMINow

        # Basic usage
        with MMINow() as client:
            response = client.get_data()
            print(f"Current MMI: {response.data.current_value}")
            print(f"Last week MMI: {response.data.last_week.indicator}")
            print(f"Change from last month: {response.data.indicator - response.data.last_month.indicator:.2f}")

        # Manual client management
        client = MMINow()
        try:
            response = client.get_data()
            # Process response...
        finally:
            client.close()
        ```

    #### 2.5 Response Schema:

    ```json
    {
    "success": true,
    "data": {
        "date": "2025-06-17T05:39:00.065Z",
        "currentValue": 52.02,
        "indicator": 52.02,
        "lastDay": {...},
        "lastWeek": {...},
        "lastMonth": {...},
        "lastYear": {...},
        "daily": [...]
    }
    }
    ```

    #### 2.6 Response Fields:

    - **success** (boolean): API call status  
    - **data** (object): Main payload with current and comparison data
    - **data.currentValue** (float): Current MMI value (0-100)
    - **data.lastDay** (object): Previous trading day data
    - **data.lastWeek** (object): Data from one week ago
    - **data.lastMonth** (object): Data from one month ago
    - **data.lastYear** (object): Data from one year ago
    - **data.daily** (array): Daily MMI time series

## Error Handling

**1 HTTP Status Codes:**

| Code | Description | Response |
|------|-------------|----------|
| 200 | Success | Valid JSON response with data |
| 4xx | Client Error | Error message in response.text |
| 5xx | Server Error | Error message in response.text |

**2 Python Exception Types:**

```terminal
# Parameter validation error
ValueError: Period must be between 1 and 10, got 15

# HTTP request errors  
Exception: HTTP 404 error: Not Found
Exception: Request failed: Connection timeout

# Response validation errors
Exception: Data validation error: Field 'indicator' missing
```

**3 Error Handling Example:**

```python
from tickersnap.mmi import MMIPeriod

try:
    with MMIPeriod() as client:
        response = client.get_data(period=15)  # Invalid period
except ValueError as e:
    print(f"Parameter error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## Client Configuration

=== "Timeout Settings"

    ```python
    # Default timeout: 10 seconds
    client = MMIPeriod()

    # Custom timeout: 30 seconds  
    client = MMIPeriod(timeout=30)

    # For slower connections
    client = MMINow(timeout=60)
    ```

=== "Connection Management"

    ```python
    # Context manager (recommended)
    with MMIPeriod() as client:
        response = client.get_data()
        # Client automatically closed

    # Manual management
    client = MMIPeriod()
    try:
        response = client.get_data()
    finally:
        client.close()  # Important: always close
    ```

## Usage Examples

=== "Real-time Monitoring"

    ```python
    import time
    from tickersnap.mmi import MMINow

    def monitor_mmi():
        while True:
            client = MMINow()
            response = client.get_data()
            mmi = response.data.current_value
            client.close()

            if mmi <= 30:
                print(f"🟢 EXTREME FEAR: MMI {mmi:.2f}")
                print(f"      good time to buy stocks!")
            elif mmi >= 70:
                print(f"🔴 EXTREME GREED: MMI {mmi:.2f}")
                print(f"      avoid fresh positions!")
            else:
                print(f"⚪ NEUTRAL Zone: MMI {mmi:.2f}")
                print(f"      observe market conditions")
            
            # check every day at 12:00 AM
            time.sleep(24 * 60 * 60)
    ```

=== "Historical Analysis"

    ```python
    from tickersnap.mmi import MMIPeriod

    def analyze_trend():
        with MMIPeriod() as client:
            # get 10 days of data
            response = client.get_data(period=10)
            
            # current vs historical average
            current = response.data.indicator
            historical = [day.indicator for day in response.data.days_historical]
            avg_historical = sum(historical) / len(historical)
            
            print(f"Current MMI: {current:.1f}")
            print(f"Historical Avg: {avg_historical:.1f}")
            print(f"Trend: {'📈 Rising' if current > avg_historical else '📉 Falling'}")
    ```

=== "Data Comparison"

    ```python
    from tickersnap.mmi import MMINow

    def compare_periods():
        with MMINow() as client:
            response = client.get_data()
            data = response.data
            
            comparisons = {
                "vs Yesterday": data.indicator - data.last_day.indicator,
                "vs Last Week": data.indicator - data.last_week.indicator, 
                "vs Last Month": data.indicator - data.last_month.indicator,
                "vs Last Year": data.indicator - data.last_year.indicator
            }
            
            print(f"Current MMI: {data.current_value:.1f}")
            for period, change in comparisons.items():
                direction = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                print(f"{period}: {direction} {change:+.1f}")
    ```

## Rate Limiting & Best Practices

### Recommended Intervals

- **Real-time monitoring**: Every 5-15 minutes
- **Historical analysis**: Once per hour
- **Batch processing**: Implement delays between requests

=== "Client Reuse"

    ✅ Good: Reuse client for multiple calls

    ```python
    with MMIPeriod() as client:
        for period in [1, 2, 3]:
            response = client.get_data(period=period)
            # process response...
    ```

    ❌ Avoid: Creating new client for each call  

    ```python
    for period in [1, 2, 3]:
        with MMIPeriod() as client:
            response = client.get_data(period=period)
    ```

=== "Error Recovery"

    ```python
    import time
    from tickersnap.mmi import MMINow

    def robust_data_fetch(retries=3):
        for attempt in range(retries):
            try:
                with MMINow(timeout=30) as client:
                    return client.get_data()
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)  # exponential backoff
    ```

---

::: tickersnap.mmi.api
