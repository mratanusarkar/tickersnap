# Stock Scorecard

A high-level Python interface for accessing Tickertape's **Stock Scorecard data** with simplified, user-friendly methods.

It provides simple functions to get comprehensive stock analysis including 6 key categories for daily market analysis (as listed below), with no headache of complex API handling, and distraction free excessive data fields knowledge!

Key Categories from Tickertape Scorecard:

- Performance
- Valuation
- Growth
- Profitability
- Entry Point
- Red Flags

!!! warning "Disclaimer"

    Stock scorecard data is for informational purposes only. Not financial advice.
    Always consult qualified financial advisors before making investment decisions.

## Overview

The `StockScorecard` class provides a clean, intuitive API for accessing comprehensive stock analysis without dealing with complex API responses or field mappings. Perfect for stock screening, portfolio analysis, investment research, and automated trading strategies.

**Key Features:**

- ✅ **Comprehensive Analysis** - 6 key categories covering all aspects of stock evaluation
- ✅ **Batch Processing** - Analyze multiple stocks concurrently with progress tracking
- ✅ **Combined Data** - Asset + Scorecard data in unified format
- ✅ **Smart Ratings** - No confusion with good/bad/okay classifications
- ✅ **Error Resilience** - Partial failures don't stop the entire process
- ✅ **Performance Optimized** - Concurrent processing for 5k+ stocks
- ✅ **Extensive Test Coverage** - A robust CI/CD pipeline to identify changes in Tickertape API.

!!! note "Note"

    - I personally find the tickertape scorecard to be a bit confusing!
    - It uses a mix of scores, flags, values, and numbers to indicate the rating.
    - Instead of mental headache to see which "high" means good or bad, we have simplified it to a single rating.
    - Simply look for good, bad, okay, and unknown (for missing data) ratings.

!!! tip "Tip"

    - Logically speaking, only "Valuation" and "Red Flags" are cases where `low` means good and `high` means bad.
    - For all other scores and elements in categories, `high` means good and `low` means bad.

## Quick Start

!!! example "Analyze Stock Scorecards"

    ```python
    from tickersnap.stock import StockScorecard

    # Initialize scorecard client
    scorecard = StockScorecard()

    # Get single stock scorecard
    tcs_scores = scorecard.get_scorecard("TCS")
    print(f"Performance: {tcs_scores.performance.value} ({tcs_scores.performance.rating})")
    print(f"Valuation: {tcs_scores.valuation.value} ({tcs_scores.valuation.rating})")

    # Get multiple stocks with progress
    stocks = ["TCS", "RELI", "INFY", "HDFC"]
    results = scorecard.get_scorecards(stocks, progress=True)
    
    # Count good vs bad stocks
    good_stocks = [r for r in results if r and r.performance and r.performance.rating.name == "GOOD"]
    print(f"Good performers: {len(good_stocks)}/{len(stocks)}")

    # Combined asset + scorecard data
    from tickersnap.lists import Assets
    assets = Assets()
    tcs_asset = next(s for s in assets.get_all_stocks() if s.sid == "TCS")
    
    combined = scorecard.get_stock_with_scorecard(tcs_asset)
    print(f"Stock: {combined.asset.name} ({combined.asset.ticker})")
    if combined.scorecard:
        print(f"Entry Point: {combined.scorecard.entry_point.rating}")
    ```

## Core Methods

=== "Single Stock Analysis"

    Get comprehensive scorecard for a single stock by SID.

    !!! info "Function Signature"

        ```python
        def get_scorecard(sid: str) -> StockScores
        ```

    !!! success "Returns"

        - Complete stock scorecard with 6 categories
        - User-friendly ratings (GOOD/BAD/OKAY/UNKNOWN)
        - Detailed elements for Entry Point and Red Flags

    !!! example "Example"

        ```python
        scorecard = StockScorecard()
        scores = scorecard.get_scorecard("TCS")

        # Financial categories
        print(f"Performance: {scores.performance.value} - {scores.performance.description}")
        print(f"Valuation: {scores.valuation.value} - {scores.valuation.rating}")
        print(f"Growth: {scores.growth.value}")
        print(f"Profitability: {scores.profitability.value}")

        # Trading categories with elements
        if scores.entry_point:
            print(f"Entry Point: {scores.entry_point.value} ({scores.entry_point.rating})")
            if scores.entry_point_elements:
                for element in scores.entry_point_elements:
                    print(f"  • {element.name}: {element.value} ({element.rating})")

        if scores.red_flags:
            print(f"Red Flags: {scores.red_flags.value} ({scores.red_flags.rating})")
            if scores.red_flags_elements:
                for flag in scores.red_flags_elements:
                    print(f"  ⚠️ {flag.name}: {flag.value}")

        # Quick investment signal
        good_categories = sum(1 for cat in [scores.performance, scores.valuation, 
                                          scores.growth, scores.profitability] 
                             if cat and cat.rating.name == "GOOD")
        print(f"Investment signal: {good_categories}/4 categories are good")
        ```

=== "Batch Processing"

    Get scorecards for multiple stocks with concurrent processing and progress tracking.

    !!! info "Function Signature"

        ```python
        def get_scorecards(
            sids: List[str], 
            progress: Optional[ProgressType] = None
        ) -> List[Optional[StockScores]]
        ```

    !!! success "Returns"

        - List of scorecard data (None for failed requests)
        - Order matches input SID order
        - Concurrent processing for performance

    !!! example "Example"

        ```python
        scorecard = StockScorecard(max_workers=20)
        
        # Large batch with progress bar
        large_cap_stocks = ["TCS", "RELI", "INFY", "HDFC", "ICICIBANK", "KOTAKBANK"]
        results = scorecard.get_scorecards(large_cap_stocks, progress=True)

        # Analyze results
        successful = [r for r in results if r is not None]
        print(f"Success rate: {len(successful)}/{len(large_cap_stocks)}")

        # Custom progress callback
        def progress_callback(completed, total, current_sid):
            percentage = (completed / total) * 100
            print(f"Progress: {percentage:.1f}% - Processing {current_sid}")

        results = scorecard.get_scorecards(
            large_cap_stocks, 
            progress=progress_callback
        )

        # Screen for good stocks
        good_stocks = []
        for i, result in enumerate(results):
            if result:
                good_count = sum(1 for cat in [result.performance, result.valuation,
                                             result.growth, result.profitability]
                               if cat and cat.rating.name == "GOOD")
                if good_count >= 2:  # At least 2 good categories
                    good_stocks.append(large_cap_stocks[i])
        
        print(f"Stocks with 2+ good categories: {good_stocks}")
        ```

=== "Single Asset + Scorecard"

    Get combined asset information + scorecard data for a single stock.

    !!! info "Function Signature"

        ```python
        def get_stock_with_scorecard(asset: AssetData) -> StockWithScorecard
        ```

    !!! success "Returns"

        - Asset metadata (name, ticker, ISIN, etc.)
        - Scorecard data (or None if API fails)
        - Unified format for easy processing

    !!! example "Example"

        ```python
        from tickersnap.lists import Assets
        from tickersnap.stock import StockScorecard

        # Get asset data
        assets_client = Assets()
        scorecard_client = StockScorecard()

        # Single stock with complete data
        all_stocks = assets_client.get_all_stocks()
        tcs_asset = next(s for s in all_stocks if s.sid == "TCS")
        
        combined = scorecard_client.get_stock_with_scorecard(tcs_asset)
        print(f"Company: {combined.asset.name}")
        print(f"Ticker: {combined.asset.ticker}")
        print(f"ISIN: {combined.asset.isin}")
        
        if combined.scorecard:
            print(f"Overall assessment available with {sum(1 for cat in [
                combined.scorecard.performance, combined.scorecard.valuation,
                combined.scorecard.growth, combined.scorecard.profitability,
                combined.scorecard.entry_point, combined.scorecard.red_flags
            ] if cat)} categories")
        else:
            print("❌ Scorecard data unavailable")
        ```

=== "Batch Asset + Scorecard"

    Get combined asset information + scorecard data for multiple stocks with concurrent processing.

    !!! info "Function Signature"

        ```python
        def get_stocks_with_scorecards(
            assets: List[AssetData], 
            progress: Optional[ProgressType] = None
        ) -> List[StockWithScorecard]
        ```

    !!! success "Returns"

        - List of combined asset + scorecard data
        - Asset metadata always present
        - Scorecard data (or None if API fails)
        - Order matches input assets order

    !!! example "Example"

        ```python
        from tickersnap.lists import Assets
        from tickersnap.stock import StockScorecard

        # Get asset data
        assets_client = Assets()
        scorecard_client = StockScorecard()

        # Batch processing with complete data
        all_stocks = assets_client.get_all_stocks()
        nifty50_assets = [s for s in all_stocks if any(name in s.name for name in [
            "Tata Consultancy",
            "Reliance Industries", 
            "HDFC Bank", "Infosys"
        ])][:4]  # Sample 4 stocks
        
        combined_results = scorecard_client.get_stocks_with_scorecards(
            nifty50_assets, progress=True
        )
        
        # Comprehensive analysis
        for result in combined_results:
            print(f"\n📊 {result.asset.name} ({result.asset.ticker})")
            if result.scorecard:
                # Count good categories
                categories = [
                    result.scorecard.performance,
                    result.scorecard.valuation,
                    result.scorecard.growth,
                    result.scorecard.profitability
                ]
                good_count = sum(1 for cat in categories if cat and cat.rating.name == "GOOD")
                print(f"  Financial strength: {good_count}/4 categories are good")
                
                # Entry point analysis
                if result.scorecard.entry_point:
                    print(f"  Entry timing: {result.scorecard.entry_point.rating}")
                
                # Risk assessment
                if result.scorecard.red_flags:
                    risk_level = result.scorecard.red_flags.rating
                    print(f"  Risk level: {risk_level}")
            else:
                print("  ❌ Scorecard data unavailable")

        # Performance analysis from test_end_user_usage.py
        successful = sum(1 for r in combined_results if r.scorecard is not None)
        if len(combined_results) > 0:
            success_rate = successful / len(combined_results) * 100
            print(f"\nSuccess rate: {success_rate:.1f}%")
            
            # Category analysis
            good_performance = sum(1 for r in combined_results 
                if r.scorecard and r.scorecard.performance 
                and r.scorecard.performance.rating.name == "GOOD"
            )
            print(f"Good performance stocks: {good_performance}/{successful}")
        ```

## Configuration

=== "Performance Settings"

    Configure timeout and concurrency for optimal performance.

    !!! example "Example"

        ```python
        # Default settings (good for most use cases)
        scorecard = StockScorecard()

        # High-performance settings for large batches
        scorecard = StockScorecard(
            timeout=30,      # Longer timeout for slow connections
            max_workers=20   # More concurrent requests
        )

        # Conservative settings for rate limiting
        scorecard = StockScorecard(
            timeout=60,      # Very patient timeout
            max_workers=5    # Fewer concurrent requests
        )
        ```

=== "Error Handling"

    Handle errors gracefully with robust error handling.

    !!! example "Example"

        ```python
        from tickersnap.stock import StockScorecard

        try:
            scorecard = StockScorecard(timeout=30)
            
            # Single stock - will raise exception on failure
            result = scorecard.get_scorecard("TCS")
            print(f"TCS scorecard: {result.performance.rating}")
            
        except Exception as e:
            print(f"Failed to fetch scorecard: {e}")

        # Batch processing - individual failures don't stop the process
        stocks = ["TCS", "INVALID_SID", "RELI"]
        results = scorecard.get_scorecards(stocks)
        
        for i, result in enumerate(results):
            if result:
                print(f"{stocks[i]}: Success")
            else:
                print(f"{stocks[i]}: Failed (but others continued)")
        ```

## Usage Examples

=== "Portfolio Screening"

    Screen large portfolios for investment opportunities.

    !!! example "Example"

        ```python
        from tickersnap.lists import Assets
        from tickersnap.stock import StockScorecard

        def screen_portfolio(min_good_categories=2, max_red_flags=True):
            """Screen all stocks for investment opportunities."""
            
            # Get all stocks
            assets = Assets()
            scorecard = StockScorecard(max_workers=25)
            
            print("📊 Fetching all stocks...")
            all_stocks = assets.get_all_stocks()
            print(f"Total stocks: {len(all_stocks)}")
            
            # Get scorecards for sample stocks (for demo purposes)
            print("🔍 Analyzing scorecards...")
            results = scorecard.get_stocks_with_scorecards(
                all_stocks[:50],  # Sample first 50 for demo
                progress=True
            )
            
            # Screen for good stocks
            good_stocks = []
            risky_stocks = []
            
            for result in results:
                if not result.scorecard:
                    continue
                    
                # Count good financial categories
                financial_cats = [
                    result.scorecard.performance,
                    result.scorecard.valuation, 
                    result.scorecard.growth,
                    result.scorecard.profitability
                ]
                good_count = sum(1 for cat in financial_cats 
                               if cat and cat.rating.name == "GOOD")
                
                # Check red flags
                has_red_flags = (result.scorecard.red_flags and 
                               result.scorecard.red_flags.rating.name == "BAD")
                
                # Classification
                if good_count >= min_good_categories and (not max_red_flags or not has_red_flags):
                    good_stocks.append({
                        "name": result.asset.name,
                        "ticker": result.asset.ticker,
                        "good_categories": good_count,
                        "entry_point": result.scorecard.entry_point.rating.name if result.scorecard.entry_point else "UNKNOWN"
                    })
                elif has_red_flags:
                    risky_stocks.append({
                        "name": result.asset.name,
                        "ticker": result.asset.ticker,
                        "reason": "Has red flags"
                    })
            
            # Results
            print(f"\n🟢 Investment Opportunities ({len(good_stocks)} stocks):")
            for stock in sorted(good_stocks, key=lambda x: x["good_categories"], reverse=True)[:10]:
                print(f"  {stock['ticker']}: {stock['name']}")
                print(f"    Good categories: {stock['good_categories']}/4")
                print(f"    Entry point: {stock['entry_point']}")
            
            print(f"\n🔴 Risky Stocks ({len(risky_stocks)} stocks):")
            for stock in risky_stocks[:5]:
                print(f"  {stock['ticker']}: {stock['reason']}")

        # screen_portfolio()  # Uncomment to run
        ```

=== "Sector Analysis"

    Analyze stocks by sector or theme.

    !!! example "Example"

        ```python
        def analyze_sector(sector_keywords, sample_size=20):
            """Analyze stocks in a specific sector."""
            from tickersnap.lists import Assets
            from tickersnap.stock import StockScorecard
            
            # Get sector stocks
            assets = Assets()
            scorecard = StockScorecard()
            
            all_stocks = assets.get_all_stocks()
            sector_stocks = []
            
            for stock in all_stocks:
                for keyword in sector_keywords:
                    if keyword.lower() in stock.name.lower():
                        sector_stocks.append(stock)
                        break
            
            # Sample for analysis
            sample_stocks = sector_stocks[:sample_size]
            print(f"📊 Analyzing {len(sample_stocks)} {'/'.join(sector_keywords)} stocks...")
            
            # Get scorecards
            results = scorecard.get_stocks_with_scorecards(sample_stocks, progress=True)
            
            # Sector statistics
            total_analyzed = 0
            category_stats = {
                "performance": {"good": 0, "bad": 0, "okay": 0},
                "valuation": {"good": 0, "bad": 0, "okay": 0},
                "growth": {"good": 0, "bad": 0, "okay": 0},
                "profitability": {"good": 0, "bad": 0, "okay": 0}
            }
            
            top_stocks = []
            
            for result in results:
                if not result.scorecard:
                    continue
                    
                total_analyzed += 1
                
                # Track category statistics
                categories = {
                    "performance": result.scorecard.performance,
                    "valuation": result.scorecard.valuation,
                    "growth": result.scorecard.growth,
                    "profitability": result.scorecard.profitability
                }
                
                good_count = 0
                for cat_name, cat_data in categories.items():
                    if cat_data:
                        rating = cat_data.rating.name.lower()
                        if rating in category_stats[cat_name]:
                            category_stats[cat_name][rating] += 1
                        if rating == "good":
                            good_count += 1
                
                # Track top performers
                if good_count >= 2:
                    top_stocks.append({
                        "name": result.asset.name,
                        "ticker": result.asset.ticker,
                        "good_count": good_count,
                        "entry_point": result.scorecard.entry_point.rating.name if result.scorecard.entry_point else "UNKNOWN"
                    })
            
            # Sector report
            print(f"\n📈 {'/'.join(sector_keywords).title()} Sector Analysis")
            print(f"Stocks analyzed: {total_analyzed}")
            
            print("\n📊 Category Performance:")
            for category, stats in category_stats.items():
                total = sum(stats.values())
                if total > 0:
                    good_pct = (stats["good"] / total) * 100
                    print(f"  {category.title()}: {good_pct:.1f}% good ({stats['good']}/{total})")
            
            print(f"\n🏆 Top Performers ({len(top_stocks)} stocks):")
            for stock in sorted(top_stocks, key=lambda x: x["good_count"], reverse=True)[:5]:
                print(f"  {stock['ticker']}: {stock['good_count']}/4 good categories")

        # analyze_sector(["bank", "financial"], sample_size=15)
        # analyze_sector(["pharma", "drug"], sample_size=10)
        # analyze_sector(["tech", "software", "IT"], sample_size=20)
        ```

=== "Market Monitoring"

    Monitor market conditions and stock performance.

    !!! example "Example"

        ```python
        import time
        from datetime import datetime

        def market_pulse_check(watchlist):
            """Check market pulse using scorecard data."""
            from tickersnap.stock import StockScorecard
            
            scorecard = StockScorecard()
            
            while True:
                print(f"\n🕐 Market Pulse Check - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                
                try:
                    results = scorecard.get_scorecards(watchlist)
                    
                    # Market sentiment analysis
                    total_stocks = len([r for r in results if r])
                    if total_stocks == 0:
                        print("❌ No data available")
                        continue
                    
                    # Count performance ratings
                    performance_sentiment = {"good": 0, "bad": 0, "okay": 0}
                    entry_point_sentiment = {"good": 0, "bad": 0, "okay": 0}
                    
                    for result in results:
                        if result:
                            # Performance sentiment
                            if result.performance:
                                rating = result.performance.rating.name.lower()
                                if rating in performance_sentiment:
                                    performance_sentiment[rating] += 1
                            
                            # Entry point sentiment
                            if result.entry_point:
                                rating = result.entry_point.rating.name.lower()
                                if rating in entry_point_sentiment:
                                    entry_point_sentiment[rating] += 1
                    
                    # Market signals
                    perf_good_pct = (performance_sentiment["good"] / total_stocks) * 100
                    entry_good_pct = (entry_point_sentiment["good"] / total_stocks) * 100
                    
                    print(f"📊 Market Sentiment ({total_stocks} stocks):")
                    print(f"  Performance: {perf_good_pct:.1f}% positive")
                    print(f"  Entry Points: {entry_good_pct:.1f}% favorable")
                    
                    # Overall signal
                    if perf_good_pct >= 60 and entry_good_pct >= 60:
                        print("🟢 BULLISH: Strong market conditions")
                    elif perf_good_pct <= 40 or entry_good_pct <= 40:
                        print("🔴 BEARISH: Weak market conditions")
                    else:
                        print("🟡 NEUTRAL: Mixed market conditions")
                    
                    # Individual alerts
                    print("\n🚨 Stock Alerts:")
                    for i, result in enumerate(results):
                        if result:
                            sid = watchlist[i]
                            
                            # Red flag alerts
                            if (result.red_flags and 
                                result.red_flags.rating.name == "BAD"):
                                print(f"  ⚠️ {sid}: New red flags detected")
                            
                            # Good entry point alerts
                            if (result.entry_point and 
                                result.entry_point.rating.name == "GOOD"):
                                print(f"  🟢 {sid}: Good entry point")
                
                except Exception as e:
                    print(f"❌ Error: {e}")
                
                # Check every 4 hours during market time
                time.sleep(4 * 60 * 60)

        # watchlist = ["TCS", "RELI", "INFY", "HDFC", "ICICIBANK"]
        # market_pulse_check(watchlist)  # Uncomment to run
        ```

=== "Advanced Screening"

    Advanced stock screening with custom criteria.

    !!! example "Example"

        ```python
        def advanced_stock_screener():
            """Advanced stock screening with multiple criteria."""
            from tickersnap.lists import Assets
            from tickersnap.stock import StockScorecard
            
            assets = Assets()
            scorecard = StockScorecard(max_workers=30)
            
            # Get sample of stocks for demo (use all_stocks for full screening)
            all_stocks = assets.get_all_stocks()
            sample_stocks = all_stocks[:100]  # Sample for demo
            
            print(f"🔍 Advanced screening of {len(sample_stocks)} stocks...")
            
            # Get all scorecard data
            results = scorecard.get_stocks_with_scorecards(sample_stocks, progress=True)
            
            # Define screening criteria
            screens = {
                "value_picks": {
                    "name": "Value Picks",
                    "criteria": lambda r: (
                        r.scorecard and
                        r.scorecard.valuation and r.scorecard.valuation.rating.name == "GOOD" and
                        r.scorecard.performance and r.scorecard.performance.rating.name != "BAD" and
                        r.scorecard.entry_point and r.scorecard.entry_point.rating.name == "GOOD"
                    )
                },
                "growth_stocks": {
                    "name": "Growth Stocks", 
                    "criteria": lambda r: (
                        r.scorecard and
                        r.scorecard.growth and r.scorecard.growth.rating.name == "GOOD" and
                        r.scorecard.profitability and r.scorecard.profitability.rating.name == "GOOD" and
                        (not r.scorecard.red_flags or r.scorecard.red_flags.rating.name != "BAD")
                    )
                },
                "quality_stocks": {
                    "name": "Quality Stocks",
                    "criteria": lambda r: (
                        r.scorecard and
                        sum(1 for cat in [r.scorecard.performance, r.scorecard.valuation,
                                        r.scorecard.growth, r.scorecard.profitability]
                           if cat and cat.rating.name == "GOOD") >= 3
                    )
                },
                "turnaround_plays": {
                    "name": "Turnaround Plays",
                    "criteria": lambda r: (
                        r.scorecard and
                        r.scorecard.performance and r.scorecard.performance.rating.name == "BAD" and
                        r.scorecard.valuation and r.scorecard.valuation.rating.name == "GOOD" and
                        r.scorecard.entry_point and r.scorecard.entry_point.rating.name == "GOOD"
                    )
                }
            }
            
            # Apply screens
            screen_results = {}
            for screen_id, screen_config in screens.items():
                matches = []
                for result in results:
                    if screen_config["criteria"](result):
                        matches.append({
                            "name": result.asset.name,
                            "ticker": result.asset.ticker,
                            "isin": result.asset.isin
                        })
                screen_results[screen_id] = matches
            
            # Display results
            print("\n🎯 Screening Results:")
            for screen_id, matches in screen_results.items():
                screen_name = screens[screen_id]["name"]
                print(f"\n📊 {screen_name} ({len(matches)} stocks):")
                
                for stock in matches[:10]:  # Show top 10
                    print(f"  • {stock['ticker']}: {stock['name']}")
                
                if len(matches) > 10:
                    print(f"  ... and {len(matches) - 10} more stocks")

        # advanced_stock_screener()  # Uncomment to run
        ```

## Data Models

| Model | Description | Key Fields |
|-------|-------------|------------|
| `StockScores` | Complete stock scorecard | `performance`, `valuation`, `growth`, `profitability`, `entry_point`, `red_flags` |
| `StockWithScorecard` | Combined asset + scorecard | `asset`, `scorecard` |
| `Score` | Individual category score | `name`, `description`, `value`, `rating` |
| `ScoreRating` | Rating classification | `GOOD`, `BAD`, `OKAY`, `UNKNOWN` |

## Scorecard Categories

| Category | Type | Description | Key Insights |
|----------|------|-------------|--------------|
| **Performance** | Financial | Stock price performance vs market | Recent returns and momentum |
| **Valuation** | Financial | Stock valuation vs market average | Price attractiveness and value |
| **Growth** | Financial | Company growth prospects | Revenue/earnings growth potential |
| **Profitability** | Financial | Company profitability metrics | Operational efficiency and margins |
| **Entry Point** | Trading | Current entry timing assessment | Technical and fundamental entry signals |
| **Red Flags** | Trading | Risk assessment and warnings | Regulatory issues, debt concerns, etc. |

## Score Ratings

| Rating | Description | Investment Signal | Color Code |
|--------|-------------|-------------------|------------|
| **GOOD** | Positive indicator | 🟢 Favorable conditions | Green |
| **OKAY** | Neutral indicator | 🟡 Average conditions | Yellow/Orange |
| **BAD** | Negative indicator | 🔴 Unfavorable conditions | Red |
| **UNKNOWN** | Insufficient data | ⚪ Unable to determine | Gray |

---

::: tickersnap.stock.scorecard
