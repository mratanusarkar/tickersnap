# API Reference

## Overview

The Assets List API provides programmatic access to Tickertape's complete list of stocks and ETFs through a single endpoint.
This unofficial Python client wraps the Tickertape API with robust error handling, input validation, and response parsing.

**Base URL and Request Type:**

| API | Request Type | Base URL | Response Type |
|-----|--------------|----------|---------------|
| Assets List | GET | `https://api.tickertape.in/stocks/list?filter={filter}` | JSON (application/json) |

**Headers:**

- **Authentication:** None required
- **Rate Limiting:** Not specified by Tickertape
- **Response Format:** JSON (application/json)

## API Details

??? info "Assets List Data"

    ### 1. Assets List

    #### 1.1 API Details:

    Retrieve complete list of all available assets (stocks and ETFs) with optional filtering.

    **Endpoint:** `GET /stocks/list`  
    **Base URL:** `https://api.tickertape.in`  
    **Full URL:** `https://api.tickertape.in/stocks/list?filter={filter}`

    #### 1.2 Parameters:

    | Parameter | Type | Required | Options | Default | Description |
    |-----------|------|----------|---------|---------|-------------|
    | `filter` | string | No | 'a'-'z', 'others' | None | Filter assets by starting letter or 'others' |

    **Filter Options:**
    - **Letters**: 'a' to 'z' (case insensitive) - assets starting with that letter
    - **Others**: 'others' (case sensitive) - assets not starting with letters
    - **None**: No filter - returns all available assets (~5312 total)

    #### 1.3 Request Example:

    ```bash
    # Get all assets
    curl -X GET "https://api.tickertape.in/stocks/list"

    # Get assets starting with 'a'
    curl -X GET "https://api.tickertape.in/stocks/list?filter=a"

    # Get assets not starting with letters
    curl -X GET "https://api.tickertape.in/stocks/list?filter=others"
    ```

    #### 1.4 Python Usage:

    === "AssetsList"

        ```python
        from tickersnap.lists import AssetsList

        # Basic usage - get all assets
        with AssetsList() as client:
            response = client.get_data()
            print(f"Total assets: {len(response.data)}")
            
            # Print first few assets
            for asset in response.data[:3]:
                print(f"{asset.name} ({asset.ticker}) - {asset.type}")

        # Filter by starting letter
        with AssetsList() as client:
            response = client.get_data(filter='a')
            print(f"Assets starting with 'a': {len(response.data)}")

        # Get assets not starting with letters
        with AssetsList() as client:
            response = client.get_data(filter='others')
            print(f"Other assets: {len(response.data)}")

        # With custom timeout
        with AssetsList(timeout=30) as client:
            response = client.get_data(filter='t')
        ```

    #### 1.5 Response Schema:

    ```json
    {
        "success": true,
        "data": [
            {
                "sid": "1234",
                "name": "Reliance Industries Limited",
                "ticker": "RELIANCE",
                "type": "stock",
                "slug": "reliance-industries-ltd",
                "isin": "INE002A01018"
            },
            {
                "sid": "5678",
                "name": "Nippon India ETF Nifty 50",
                "ticker": "NIFTYBEES",
                "type": "etf",
                "slug": "nippon-india-etf-nifty-50",
                "isin": "INF204KB17I5"
            }
        ]
    }
    ```

    #### 1.6 Response Fields:

    - **success** (boolean): API call status
    - **data** (array): List of asset objects
    - **data[].sid** (string): Tickertape's security identifier
    - **data[].name** (string): Full company or fund name
    - **data[].ticker** (string): Exchange trading symbol
    - **data[].type** (string): Asset type ('stock' or 'etf')
    - **data[].slug** (string): URL path for Tickertape
    - **data[].isin** (string): International Securities Identification Number

## Error Handling

**1 HTTP Status Codes:**

| Code | Description | Response |
|------|-------------|----------|
| 200 | Success | Valid JSON response with data |
| 4xx | Client Error | Error message in response.text |
| 5xx | Server Error | Error message in response.text |

**2 Python Exception Types:**

```terminal
# Filter validation errors
ValueError: Invalid filter 'xyz'. Valid options are: a, b, c, ..., z, others. Only the letters are case insensitive.
ValueError: Empty filter '' not allowed. Use filter=None or omit the parameter to get all assets.
ValueError: Filter ' a ' contains leading or trailing whitespaces. Please remove the whitespaces and try again.

# HTTP request errors  
Exception: HTTP 404 error: Not Found
Exception: Request failed: Connection timeout

# Response validation errors
Exception: Data validation error: Field 'success' missing
```

**3 Error Handling Example:**

```python
from tickersnap.lists import AssetsList

try:
    with AssetsList() as client:
        response = client.get_data(filter='invalid')
except ValueError as e:
    print(f"Parameter error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## Client Configuration

=== "Timeout Settings"

    ```python
    # Default timeout: 10 seconds
    client = AssetsList()

    # Custom timeout: 30 seconds  
    client = AssetsList(timeout=30)

    # For slower connections
    client = AssetsList(timeout=60)
    ```

=== "Connection Management"

    ```python
    # Context manager (recommended)
    with AssetsList() as client:
        response = client.get_data()
        # Client automatically closed

    # Manual management
    client = AssetsList()
    try:
        response = client.get_data()
    finally:
        client.close()  # Important: always close
    ```

## Usage Examples

=== "Fetch all Assets"

    ```python
    from tickersnap.lists import AssetsList

    with AssetsList() as client:
        all_assets = client.get_data()
        
        # Categorize by type
        stocks = [asset for asset in all_assets.data if asset.type == "stock"]
        etfs = [asset for asset in all_assets.data if asset.type == "etf"]
        
        print(f"Total assets: {len(all_assets.data)}")
        print(f"Stocks: {len(stocks)}")
        print(f"ETFs: {len(etfs)}")
    ```

=== "Filtered Search"

    ```python
    from tickersnap.lists import AssetsList
    
    search = 'A'
    
    with AssetsList() as client:
        response = client.get_data(filter=search.lower())
        
        print(f"Assets starting with '{search}':")
        
        # show first 10 assets
        for asset in response.data[:10]:
            print(f"  {asset.ticker}: {asset.name}")
        
        print(f"Total found: {len(response.data)}")
    ```

=== "Data Export"

    ```python
    import csv
    from tickersnap.lists import AssetsList

    def export_to_csv(filename="assets.csv"):
        """Export all assets to CSV file."""
        with AssetsList() as client:
            response = client.get_data()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['sid', 'name', 'ticker', 'type', 'slug', 'isin']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for asset in response.data:
                    writer.writerow({
                        'sid': asset.sid,
                        'name': asset.name,
                        'ticker': asset.ticker,
                        'type': asset.type,
                        'slug': asset.slug,
                        'isin': asset.isin
                    })
            
            print(f"Exported {len(response.data)} assets to {filename}")

    # export_to_csv()  # uncomment to run
    ```

=== "Asset Statistics"

    ```python
    def analyze_assets():
        """Analyze asset distribution and statistics."""
        with AssetsList() as client:
            all_assets = client.get_data()
            
            # Count by type
            type_counts = {}
            for asset in all_assets.data:
                type_counts[asset.type] = type_counts.get(asset.type, 0) + 1
            
            # Count by starting letter
            letter_counts = {}
            for asset in all_assets.data:
                first_char = asset.name[0].upper() if asset.name else 'Unknown'
                if first_char.isalpha():
                    letter_counts[first_char] = letter_counts.get(first_char, 0) + 1
                else:
                    letter_counts['Others'] = letter_counts.get('Others', 0) + 1
            
            print("📊 Asset Statistics")
            print(f"Total Assets: {len(all_assets.data)}")
            print("\nBy Type:")
            for asset_type, count in sorted(type_counts.items()):
                print(f"  {asset_type.upper()}: {count}")
            
            print("\nTop 5 Starting Letters:")
            sorted_letters = sorted(letter_counts.items(), key=lambda x: x[1], reverse=True)
            for letter, count in sorted_letters[:5]:
                print(f"  {letter}: {count}")

    analyze_assets()
    ```

## Rate Limiting & Best Practices

### Recommended Usage

- **Asset discovery**: Once per day or as needed
- **Filtered searches**: Multiple calls acceptable for different filters
- **Bulk operations**: Implement delays between requests

=== "Client Reuse"

    ✅ Good: Reuse client for multiple calls

    ```python
    with AssetsList() as client:
        all_assets = client.get_data()
        a_assets = client.get_data(filter='a')
        others = client.get_data(filter='others')
        # process responses...
    ```

    ❌ Avoid: Creating new client for each call  

    ```python
    for filter_char in ['a', 'b', 'c']:
        with AssetsList() as client:
            response = client.get_data(filter=filter_char)
    ```

=== "Error Recovery"

    ```python
    import time
    from tickersnap.lists import AssetsList

    def robust_fetch(filter_value=None, retries=3):
        """Fetch assets with retry logic."""
        for attempt in range(retries):
            try:
                with AssetsList(timeout=30) as client:
                    return client.get_data(filter=filter_value)
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)  # exponential backoff
    ```

---

::: tickersnap.lists.api
