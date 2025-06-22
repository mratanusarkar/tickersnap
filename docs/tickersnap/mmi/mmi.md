# Market Mood Index

A high-level Python interface for accessing Tickertape's **Market Mood Index (MMI)** data with simplified, user-friendly methods.

It provides simple functions to automate or programatically get the current MMI value, trends, and changes for daily market analysis,
with no headache of complex API handling, and distraction free excessive data fields knowledge!

!!! warning "Disclaimer"
    MMI is a sentiment tool for informational purposes only. Not financial advice.
    Always consult qualified financial advisors before making investment decisions.

## Overview

The `MarketMoodIndex` class provides a clean, intuitive API for accessing MMI data without dealing with complex API responses or field mappings. Perfect for automation, programmatic daily market analysis, trading strategies, and financial applications.

**Key Features:**

- ✅ **Simple MMI data access** - No complex API handling required
- ✅ **Zone classification** - Automatic Fear/Greed zone calculation  
- ✅ **Trend analysis** - Historical data for charting and analysis
- ✅ **Comparison data** - Easy period-over-period comparisons
- ✅ **Error handling** - Robust timeout and retry capabilities
- ✅ **Extensive Test Coverage** - A robust CI/CD pipeline to identify changes in Tickertape API.

## Quick Start

!!! example "See MMI Data"

    ```python
    from tickersnap.mmi import MarketMoodIndex

    # Initialize MMI client
    mmi = MarketMoodIndex()

    # Get current MMI with zone
    current = mmi.get_current_mmi()
    print(f"MMI: {current.value:.1f} ({current.zone})")

    # Get trends for analysis  
    trends = mmi.get_mmi_trends()
    print(f"Current: {trends.current.value:.1f}")
    print(f"10-day trend: {', '.join(f'{day.value:.1f}' for day in trends.last_10_days)}")

    # Get comparison data
    changes = mmi.get_mmi_changes()
    print(f"vs Yesterday: {changes.vs_last_day:+.1f}")
    print(f"vs Last Month: {changes.vs_last_month:+.1f}")
    ```

## Core Methods

=== "Current MMI Value"

    Get the current Market Mood Index with automatic zone classification.

    !!! info "Function Signature"

        ```python
        def get_current_mmi() -> MMICurrent
        ```

    !!! success "Returns"

        - Current MMI value (0-100)
        - Zone classification
        - Timestamp

    !!! example "Example"

        ```python
        mmi = MarketMoodIndex()
        current = mmi.get_current_mmi()

        print(f"Date: {current.date}")
        print(f"MMI: {current.value:.1f}")
        print(f"Zone: {current.zone}")  # EXTREME_FEAR, FEAR, GREED, EXTREME_GREED

        # Zone-based trading logic
        if current.zone == "Extreme Fear":
            print("🟢 Good time to buy!")
        elif current.zone == "Extreme Greed":  
            print("🔴 Avoid fresh positions!")
        else:
            print("⚪ Monitor trend")
        ```

=== "Historical Trends"

    Get MMI trend data for charting and analysis (10 days + 10 months).

    !!! info "Function Signature"

        ```python
        def get_mmi_trends() -> MMITrends
        ```

    !!! success "Returns"

        - Current MMI value
        - Historical data series for trend analysis

    !!! example "Example"

        ```python
        mmi = MarketMoodIndex()
        trends = mmi.get_mmi_trends()

        # Current vs historical analysis
        current = trends.current.value
        daily_avg = sum(day.value for day in trends.last_10_days) / len(trends.last_10_days)

        print(f"Current MMI: {current:.1f}")
        print(f"10-day average: {daily_avg:.1f}")
        print(f"Trend: {'📈 Rising' if current > daily_avg else '📉 Falling'}")

        # Chart data preparation (last 10 days)
        dates = [day.date for day in trends.last_10_days]
        values = [day.value for day in trends.last_10_days]

        # Chart data preparation (last 10 months)
        dates = [month.date for month in trends.last_10_months]
        values = [month.value for month in trends.last_10_months]
        ```

=== "Period Comparisons"

    Get MMI changes vs previous periods (day, week, month, year).

    !!! info "Function Signature"

        ```python
        def get_mmi_changes() -> MMIChanges
        ```

    !!! success "Returns"

        - Current MMI value
        - Historical MMI values with built-in comparison properties

    !!! example "Example"

        ```python
        mmi = MarketMoodIndex()
        changes = mmi.get_mmi_changes()

        # Quick comparisons
        print(f"Current MMI: {changes.current.value:.1f}")
        print(f"vs Yesterday: {changes.vs_last_day:+.1f}")
        print(f"vs Last Week: {changes.vs_last_week:+.1f}")
        print(f"vs Last Month: {changes.vs_last_month:+.1f}")
        print(f"vs Last Year: {changes.vs_last_year:+.1f}")

        # Programmatic comparison
        for period in ["day", "week", "month", "year"]:
            change = changes.vs_last(period)
            direction = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            print(f"vs {period.title()}: {direction} {change:+.1f}")
        ```

## Configuration

=== "Timeout Settings"

    Set the HTTP request timeout for the underlying API.

    !!! example "Example"

        ```python
        # Default timeout (10 seconds)
        mmi = MarketMoodIndex()

        # Custom timeout for slower connections
        mmi = MarketMoodIndex(timeout=30)
        ```

=== "Error Handling"

    Handle errors gracefully.

    !!! example "Example"

        ```python
        from tickersnap.mmi import MarketMoodIndex

        try:
            mmi = MarketMoodIndex(timeout=30)
            current = mmi.get_current_mmi()
            print(f"MMI: {current.value:.1f} ({current.zone})")
        except Exception as e:
            print(f"Failed to fetch MMI data: {e}")
        ```

## Usage Examples

=== "Daily Trading Strategy"

    Generate daily buy/sell signals based on MMI.

    !!! example "Example"

        ```python
        from tickersnap.mmi import MarketMoodIndex

        def daily_market_signal():
            """Generate daily buy/sell signals based on MMI."""

            mmi = MarketMoodIndex()
            
            try:
                current = mmi.get_current_mmi()
                changes = mmi.get_mmi_changes()
                
                # Signal logic
                if current.zone == "Extreme Fear":
                    signal = "🟢 BUY SIGNAL"
                elif current.zone == "Extreme Greed":
                    signal = "🔴 SELL SIGNAL"
                else:
                    signal = "⚪ HOLD/MONITOR"
                    
                # Trend confirmation
                trend = "Rising" if changes.vs_last_week > 0 else "Falling"
                
                print(f"MMI: {current.value:.1f} ({current.zone})")
                print(f"Signal: {signal}")
                print(f"Weekly Trend: {trend} ({changes.vs_last_week:+.1f})")
                
            except Exception as e:
                print(f"Error: {e}")

        # Run daily at market open or use a cron job
        daily_market_signal()
        ```

=== "Historical Analysis"

    Analyze MMI patterns for research.

    !!! example "Example"

        ```python
        def analyze_mmi_patterns():
            """Analyze MMI patterns for research."""
            mmi = MarketMoodIndex()
    
            # Get comprehensive data
            trends = mmi.get_mmi_trends()
            changes = mmi.get_mmi_changes()
            
            # Calculate statistics
            daily_values = [day.value for day in trends.last_10_days]
            monthly_values = [month.value for month in trends.last_10_months]
            
            daily_avg = sum(daily_values) / len(daily_values)
            monthly_avg = sum(monthly_values) / len(monthly_values)
            
            # Volatility analysis
            daily_range = max(daily_values) - min(daily_values)
            
            print(f"📊 MMI Analysis Report")
            print(f"Current: {trends.current.value:.1f}")
            print(f"10-day avg: {daily_avg:.1f}")
            print(f"10-month avg: {monthly_avg:.1f}")
            print(f"Daily volatility: {daily_range:.1f}")
            print(f"YoY change: {changes.vs_last_year:+.1f}")

        analyze_mmi_patterns()
        ```

=== "Real-time Monitoring"

    Monitor MMI for extreme readings.

    !!! example "Example"

        ```python
        import time
        from datetime import datetime

        def monitor_mmi_alerts():
            """Monitor MMI for extreme readings."""
            mmi = MarketMoodIndex()
            
            while True:
                try:
                    current = mmi.get_current_mmi()
                    changes = mmi.get_mmi_changes()
                    
                    # Extreme zone alerts
                    if current.value <= 25:
                        print(f"🚨 EXTREME FEAR ALERT: MMI {current.value:.1f}")
                        print(f"   Last seen this low: Check historical data")
                        
                    elif current.value >= 75:
                        print(f"🚨 EXTREME GREED ALERT: MMI {current.value:.1f}")
                        print(f"   Market may be overheated")
                        
                    # Large change alerts  
                    if abs(changes.vs_last_day) > 10:
                        direction = "jumped" if changes.vs_last_day > 0 else "dropped"
                        print(f"📈 LARGE MOVE: MMI {direction} {abs(changes.vs_last_day):.1f} points")
                        
                    print(f"[{datetime.now().strftime('%H:%M')}] MMI: {current.value:.1f}")
                    
                except Exception as e:
                    print(f"Error: {e}")
                    
                # Check every 15 minutes during market hours
                time.sleep(15 * 60)

        # monitor_mmi_alerts()  # uncomment to run
        ```

=== "Advanced Usage"

    For advanced users who need access to all API fields (from tickertape API).
    See [API](api.md) for more details and [Models](models.md) for data field details.

    !!! example "Example"

        ```python
        # Raw API data (all fields)
        raw_current = mmi.get_raw_current_data()
        raw_period = mmi.get_raw_period_data(period=5)

        print(f"FII flows: ₹{raw_current.fii} crores")
        print(f"Nifty: {raw_current.nifty:.1f}")
        print(f"VIX: {raw_current.vix:.1f}")
        ```

    !!! note "Note"

        For daily usage, prefer the simplified methods (`get_current_mmi`, `get_mmi_trends`, `get_mmi_changes`).

## Data Models

| Model | Description | Key Fields |
|-------|-------------|------------|
| `MMICurrent` | Current MMI with zone | `value`, `zone`, `date` |
| `MMITrends` | Historical trend data | `current`, `last_10_days`, `last_10_months` |
| `MMIChanges` | Period comparisons | `current`, `vs_last_day`, `vs_last_week`, etc. |
| `MMIDataPoint` | Individual data point | `date`, `value` |

## MMI Zones

| Zone | Range | Description | Investment Signal |
|------|-------|-------------|-------------------|
| **Extreme Fear** | 0-30 | Market oversold | 🟢 Good time to buy |
| **Fear** | 30-50 | Cautious sentiment | ⚪ Monitor trend |
| **Greed** | 50-70 | Optimistic market | 🟡 Consider selling |
| **Extreme Greed** | 70-100 | Market euphoria | 🔴 Avoid fresh positions |

---

::: tickersnap.mmi.mmi