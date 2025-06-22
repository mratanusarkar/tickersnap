# API Reference

## Overview

The Stock Scorecard API provides programmatic access to Tickertape's comprehensive stock analysis data through a single endpoint.
This unofficial Python client wraps the Tickertape API with robust error handling, input validation, and response parsing.

**Base URL and Request Type:**

| API | Request Type | Base URL | Response Type |
|-----|--------------|----------|---------------|
| Stock Scorecard | GET | `https://analyze.api.tickertape.in/stocks/scorecard/{sid}` | JSON (application/json) |

**Headers:**

- **Authentication:** None required
- **Rate Limiting:** Not specified by Tickertape
- **Response Format:** JSON (application/json)

## API Details

??? info "Stock Scorecard Data"

    ### 1. Stock Scorecard

    #### 1.1 API Details:

    Retrieve complete stock scorecard analysis including 6 key categories: Performance, Valuation, Growth, Profitability, Entry Point, and Red Flags.

    **Endpoint:** `GET /stocks/scorecard/{sid}`  
    **Base URL:** `https://analyze.api.tickertape.in`  
    **Full URL:** `https://analyze.api.tickertape.in/stocks/scorecard/{sid}`

    #### 1.2 Parameters:

    | Parameter | Type | Required | Format | Description |
    |-----------|------|----------|--------|-------------|
    | `sid` | string | Yes | alphanumeric | Stock Security ID as used by Tickertape (e.g., "TCS", "RELI", "INFY") |

    **SID Examples:**
    - **Large Cap**: TCS, RELI, INFY, HDFC
    - **Mid Cap**: BAJFINANCE, TITAN, ASIANPAINT
    - **Small Cap**: INDL, ELLE, ATE, OSWAP

    #### 1.3 Request Example:

    ```bash
    # Get TCS scorecard
    curl -X GET "https://analyze.api.tickertape.in/stocks/scorecard/TCS"

    # Get Reliance scorecard
    curl -X GET "https://analyze.api.tickertape.in/stocks/scorecard/RELI"

    # Get HDFC Bank scorecard
    curl -X GET "https://analyze.api.tickertape.in/stocks/scorecard/HDFC"
    ```

    #### 1.4 Python Usage:

    === "StockScorecardAPI"

        ```python
        from tickersnap.stock import StockScorecardAPI

        # Basic usage - get TCS scorecard
        with StockScorecardAPI() as client:
            response = client.get_data("TCS")
            print(f"Success: {response.success}")
            print(f"Categories found: {len(response.data)}")
            
            # Print scorecard categories
            for item in response.data:
                print(f"{item.name}: {item.tag} ({item.colour})")

        # Multiple stocks
        stocks = ["TCS", "RELI", "INFY"]
        with StockScorecardAPI() as client:
            for sid in stocks:
                response = client.get_data(sid)
                if response.success:
                    print(f"{sid}: {len(response.data)} categories")

        # With custom timeout
        with StockScorecardAPI(timeout=30) as client:
            response = client.get_data("HDFC")
        ```

    #### 1.5 Response Schema:

    ```json
    {
        "success": true,
        "data": [
            {
                "name": "Performance",
                "tag": "Low",
                "type": "score",
                "description": "Hasn't fared well - amongst the low performers",
                "colour": "red",
                "score": {
                    "percentage": false,
                    "max": 10,
                    "value": null,
                    "key": "Performance"
                },
                "rank": null,
                "peers": null,
                "locked": true,
                "callout": null,
                "comment": null,
                "stack": 1,
                "elements": []
            },
            {
                "name": "Entry point",
                "tag": "Good",
                "type": "entryPoint",
                "description": "The stock is underpriced and is not in the overbought zone",
                "colour": "green",
                "score": null,
                "rank": null,
                "peers": null,
                "locked": false,
                "callout": null,
                "stack": 5,
                "elements": [
                    {
                        "title": "Fundamentals",
                        "type": "flag",
                        "description": "Current price is less than the intrinsic value",
                        "flag": "High",
                        "display": true,
                        "score": null,
                        "source": null
                    }
                ],
                "comment": null
            }
        ]
    }
    ```

    #### 1.6 Response Fields:

    - **success** (boolean): API call status
    - **data** (array): List of scorecard category objects (up to 6 items)
    - **data[].name** (string): Category name (Performance, Valuation, etc.)
    - **data[].tag** (string): Assessment tag (High, Low, Good, Bad, Avg)
    - **data[].type** (string): Category type (score, entryPoint, redFlag)
    - **data[].description** (string): Human-readable assessment explanation
    - **data[].colour** (string): Color indicator (red, green, yellow)
    - **data[].score** (object): Score data for financial categories (null for trading categories)
    - **data[].elements** (array): Detailed factors for entry point and red flags

## Error Handling

**1 HTTP Status Codes:**

| Code | Description | Response |
|------|-------------|----------|
| 200 | Success | Valid JSON response with data |
| 404 | Stock Not Found | Invalid SID or stock not available |
| 4xx | Client Error | Error message in response.text |
| 5xx | Server Error | Error message in response.text |

**2 Python Exception Types:**

```terminal
# SID validation errors
ValueError: SID cannot be empty
ValueError: SID cannot be empty  # for whitespace-only SID

# HTTP request errors  
Exception: HTTP 404, check 'sid' parameter, error: Stock not found
Exception: HTTP 500, check 'sid' parameter, error: Internal Server Error
Exception: Request failed: Connection timeout

# Response validation errors
Exception: Data validation error: Field 'success' missing
Exception: Unexpected error: Invalid JSON response
```

**3 Error Handling Example:**

```python
from tickersnap.stock import StockScorecardAPI

try:
    with StockScorecardAPI() as client:
        response = client.get_data("INVALID_SID")
except ValueError as e:
    print(f"Parameter error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## Client Configuration

=== "Timeout Settings"

    ```python
    # Default timeout: 10 seconds
    client = StockScorecardAPI()

    # Custom timeout: 30 seconds  
    client = StockScorecardAPI(timeout=30)

    # For slower connections
    client = StockScorecardAPI(timeout=60)
    ```

=== "Connection Management"

    ```python
    # Context manager (recommended)
    with StockScorecardAPI() as client:
        response = client.get_data("TCS")
        # Client automatically closed

    # Manual management
    client = StockScorecardAPI()
    try:
        response = client.get_data("TCS")
    finally:
        client.close()  # Important: always close
    ```

## Usage Examples

=== "Single Stock Analysis"

    ```python
    from tickersnap.stock import StockScorecardAPI

    def analyze_stock(sid):
        """Analyze a single stock's scorecard."""
        with StockScorecardAPI() as client:
            response = client.get_data(sid)
            
            if not response.success:
                print(f"No scorecard data available for {sid}")
                return
                
            print(f"📊 {sid} Scorecard Analysis")
            print(f"Categories found: {len(response.data)}")
            
            # Categorize by type
            financial_cats = []
            trading_cats = []
            
            for item in response.data:
                if item.type == "score":
                    financial_cats.append(item)
                else:
                    trading_cats.append(item)
            
            # Financial categories
            print("\n💰 Financial Assessment:")
            for cat in financial_cats:
                color_emoji = "🟢" if cat.colour == "green" else "🔴" if cat.colour == "red" else "🟡"
                print(f"  {cat.name}: {color_emoji} {cat.tag}")
                print(f"    {cat.description}")
            
            # Trading categories
            print("\n📈 Trading Assessment:")
            for cat in trading_cats:
                color_emoji = "🟢" if cat.colour == "green" else "🔴" if cat.colour == "red" else "🟡"
                print(f"  {cat.name}: {color_emoji} {cat.tag}")
                if cat.elements:
                    for element in cat.elements:
                        if element.display:
                            print(f"    • {element.title}: {element.flag}")

    # analyze_stock("TCS")
    ```

=== "Multi-Stock Comparison"

    ```python
    def compare_stocks(stock_list):
        """Compare multiple stocks' scorecards."""
        results = {}
        
        with StockScorecardAPI() as client:
            for sid in stock_list:
                try:
                    response = client.get_data(sid)
                    if response.success and response.data:
                        # Extract key metrics
                        categories = {}
                        for item in response.data:
                            categories[item.name] = {
                                "tag": item.tag,
                                "colour": item.colour
                            }
                        results[sid] = categories
                    else:
                        results[sid] = None
                except Exception as e:
                    print(f"Error fetching {sid}: {e}")
                    results[sid] = None
        
        # Display comparison
        print("📊 Stock Comparison")
        print("-" * 50)
        
        # Get all unique categories
        all_categories = set()
        for stock_data in results.values():
            if stock_data:
                all_categories.update(stock_data.keys())
        
        # Print header
        print(f"{'Category':<15}", end="")
        for sid in stock_list:
            print(f"{sid:<12}", end="")
        print()
        
        # Print data
        for category in sorted(all_categories):
            print(f"{category:<15}", end="")
            for sid in stock_list:
                if results[sid] and category in results[sid]:
                    tag = results[sid][category]["tag"]
                    color = results[sid][category]["colour"]
                    emoji = "🟢" if color == "green" else "🔴" if color == "red" else "🟡"
                    print(f"{emoji}{tag:<11}", end="")
                else:
                    print(f"{'N/A':<12}", end="")
            print()

    # compare_stocks(["TCS", "RELI", "INFY"])
    ```

=== "Portfolio Screening"

    ```python
    def screen_portfolio(portfolio_sids, min_good_categories=2):
        """Screen portfolio stocks based on scorecard criteria."""
        good_stocks = []
        risky_stocks = []
        
        with StockScorecardAPI() as client:
            for sid in portfolio_sids:
                try:
                    response = client.get_data(sid)
                    if not response.success or not response.data:
                        continue
                    
                    # Count good vs bad categories
                    good_count = 0
                    bad_count = 0
                    red_flags = False
                    
                    for item in response.data:
                        if item.colour == "green":
                            good_count += 1
                        elif item.colour == "red":
                            bad_count += 1
                        
                        # Check for red flags
                        if item.name == "Red flags" and item.colour == "red":
                            red_flags = True
                    
                    # Classification
                    if red_flags:
                        risky_stocks.append({
                            "sid": sid,
                            "reason": "Has red flags",
                            "good": good_count,
                            "bad": bad_count
                        })
                    elif good_count >= min_good_categories and bad_count <= good_count:
                        good_stocks.append({
                            "sid": sid,
                            "good": good_count,
                            "bad": bad_count
                        })
                    else:
                        risky_stocks.append({
                            "sid": sid,
                            "reason": f"Only {good_count} good categories",
                            "good": good_count,
                            "bad": bad_count
                        })
                        
                except Exception as e:
                    print(f"Error screening {sid}: {e}")
        
        # Results
        print("🟢 Good Stocks:")
        for stock in good_stocks:
            print(f"  {stock['sid']}: {stock['good']} good, {stock['bad']} bad")
        
        print("\n🔴 Risky Stocks:")
        for stock in risky_stocks:
            print(f"  {stock['sid']}: {stock['reason']} ({stock['good']} good, {stock['bad']} bad)")

    # portfolio = ["TCS", "RELI", "INFY", "HDFC"]
    # screen_portfolio(portfolio)
    ```

=== "Data Export"

    ```python
    import csv
    from datetime import datetime

    def export_scorecard_data(stock_list, filename=None):
        """Export scorecard data to CSV."""
        if not filename:
            filename = f"scorecard_data_{datetime.now().strftime('%Y%m%d')}.csv"
        
        data = []
        
        with StockScorecardAPI() as client:
            for sid in stock_list:
                try:
                    response = client.get_data(sid)
                    if response.success and response.data:
                        for item in response.data:
                            data.append({
                                "SID": sid,
                                "Category": item.name,
                                "Tag": item.tag,
                                "Type": item.type,
                                "Description": item.description,
                                "Colour": item.colour,
                                "Stack": item.stack,
                                "Locked": item.locked
                            })
                except Exception as e:
                    print(f"Error exporting {sid}: {e}")
        
        # Write to CSV
        if data:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["SID", "Category", "Tag", "Type", "Description", "Colour", "Stack", "Locked"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(data)
            
            print(f"Exported {len(data)} scorecard entries to {filename}")
        else:
            print("No data to export")

    # stocks = ["TCS", "RELI", "INFY"]
    # export_scorecard_data(stocks)
    ```

## Rate Limiting & Best Practices

### Recommended Usage

- **Individual analysis**: Real-time calls acceptable for single stocks
- **Bulk screening**: Implement delays between requests (150ms recommended)
- **Portfolio monitoring**: Once per day or as needed

=== "Client Reuse"

    ✅ Good: Reuse client for multiple calls

    ```python
    with StockScorecardAPI() as client:
        for sid in ["TCS", "RELI", "INFY"]:
            response = client.get_data(sid)
            # process response...
    ```

    ❌ Avoid: Creating new client for each call  

    ```python
    for sid in ["TCS", "RELI", "INFY"]:
        with StockScorecardAPI() as client:
            response = client.get_data(sid)
    ```

=== "Error Recovery"

    ```python
    import time
    from tickersnap.stock import StockScorecardAPI

    def robust_scorecard_fetch(sid, retries=3):
        """Fetch scorecard with retry logic."""
        for attempt in range(retries):
            try:
                with StockScorecardAPI(timeout=30) as client:
                    return client.get_data(sid)
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                print(f"Attempt {attempt + 1} failed for {sid}: {e}")
                time.sleep(2 ** attempt)  # exponential backoff
    ```

=== "Bulk Processing"

    ```python
    import time

    def process_stock_list(stock_list, delay=0.15):
        """Process large stock lists with rate limiting."""
        results = {}
        
        with StockScorecardAPI(timeout=30) as client:
            for i, sid in enumerate(stock_list):
                try:
                    response = client.get_data(sid)
                    results[sid] = response
                    
                    # Progress tracking
                    if (i + 1) % 50 == 0:
                        print(f"Processed {i + 1}/{len(stock_list)} stocks")
                    
                    # Rate limiting
                    if i < len(stock_list) - 1:  # Don't delay after last item
                        time.sleep(delay)
                        
                except Exception as e:
                    print(f"Error processing {sid}: {e}")
                    results[sid] = None
        
        return results
    ```

## Edge Cases

### Stocks with Limited Data

Some stocks (particularly smaller companies) may have limited scorecard data or fewer categories:

```python
# Example stocks with limited data
edge_case_stocks = ["INDL", "ELLE", "ATE", "OSWAP"]

with StockScorecardAPI() as client:
    for sid in edge_case_stocks:
        response = client.get_data(sid)
        if response.success:
            categories = [item.name for item in response.data]
            print(f"{sid}: {categories}")
            # May only show: ['Entry point', 'Red flags']
```

### Failed Responses

```python
# Handle stocks that don't exist or have no data
response = client.get_data("INVALID_SID")
if not response.success:
    print("Stock not found or no scorecard data available")
```

---

::: tickersnap.stock.api
