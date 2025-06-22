# Quick Start Guide

Welcome to **Tickersnap** - your gateway to Indian stock market analysis! 🚀

This guide will get you up and running in minutes... whether you're an experienced trader, developer, investor, enthusiast, or just a beginner getting started with market analysis!

## 🚀 Getting Started

Don't let complex financial jargon intimidate you! Tickersnap makes Indian stock market analysis accessible to everyone!

It's simple... just understand the basic concepts, pick sample code and run them to see things in action!

📦 **Install the package**

To get started, just [install the package](https://mratanusarkar.github.io/tickersnap/setup/installation/),
run usage example codes (_available throughout the docs_), and see the results for yourself.

Experiment and add your modifications... and when you understand the library, build cool and more complex stuff for market analysis!

🧠 **Basic Concepts**

Tickersnap has **3 core modules** that work together:

| Module | What it does | Example | Learn More |
|--------|--------------|---------|------------|
| **📈 MMI** | Tracks market sentiment | Market fear or greed today? | [MMI](./tickersnap/mmi/index.md) |
| **📋 Assets** | Lists all stocks & ETFs | Get all 5,000+ Indian stocks | [Assets](./tickersnap/lists/index.md) |
| **📊 Scorecard** | Analyzes individual stocks | TCS performance: Good/Bad? | [Stocks](./tickersnap/stock/index.md) |

💡 **The Power of Combination**

Use **Assets** to find stocks → **Scorecard** to analyze them → **MMI** for market timing

## ⚡️ Quick Start Examples

=== "Market Mood Index (MMI)"

    !!! example "Example"

        ```python
        from tickersnap.mmi import MarketMoodIndex

        # Get market sentiment
        mmi = MarketMoodIndex()
        current = mmi.get_current_mmi()
        changes = mmi.get_mmi_changes()

        print(f"📊 Market Mood: {current.value:.1f} ({current.zone.value})")
        print(f"📈 vs Yesterday: {changes.vs_last_day:+.1f}")
        print(f"📅 vs Last Week: {changes.vs_last_week:+.1f}")

        # Investment signal
        if current.zone.value in ["Extreme Fear", "Fear"]:
            print("🟢 Consider buying opportunities")
        elif current.zone.value in ["Extreme Greed", "Greed"]:
            print("🔴 Be cautious, market may be overheated")
        ```

=== "Stock Scorecard Analysis"

    ```python
    from tickersnap.stock import StockScorecard

    # Analyze a stock
    scorecard = StockScorecard()
    analysis = scorecard.get_scorecard("TCS")

    print(f"📈 TCS Stock Analysis:")
    if analysis.performance:
        print(f"Performance: {analysis.performance.value} ({analysis.performance.rating.value})")
    if analysis.valuation:
        print(f"Valuation: {analysis.valuation.value} ({analysis.valuation.rating.value})")
    if analysis.growth:
        print(f"Growth: {analysis.growth.value} ({analysis.growth.rating.value})")
    if analysis.entry_point:
        print(f"Entry Point: {analysis.entry_point.value} ({analysis.entry_point.rating.value})")

    # Quick quality check
    good_categories = sum(1 for cat in [
        analysis.performance, analysis.valuation, 
        analysis.growth, analysis.profitability
    ] if cat and cat.rating.value == "good")

    print(f"Quality Score: {good_categories}/4 categories are good")
    ```

## 🎯 Understanding Output

=== "Market Mood Index (MMI)"

    | MMI Zones | Meaning | Implications |
    |-----------|-------------|--------------|
    | **0-30** | Extreme Fear 🟢 | Good buying opportunity |
    | **30-50** | Fear ⚪ | Monitor trends |
    | **50-70** | Greed 🟡 | Be selective |
    | **70-100** | Extreme Greed 🔴 | Avoid new positions |

=== "Stock Scorecard Analysis"

    | Stock Ratings | Meaning | Implications |
    |-----------|-------------|--------------|
    | **good** 🟢 | Positive signal | must consider analysing the stock further! |
    | **okay** 🟡 | Neutral/Average | most common case scenario for most stocks! |
    | **bad** 🔴 | Negative signal | something is wrong with the stock! |
    | **unknown** ⚪ | Insufficient data | probably new or banned, data missing! |

## 🎓 Next Steps

- 📋 [Assets Lists](./tickersnap/lists/index.md) - Get all stocks and ETFs
- 📊 [Stock Scorecard](./tickersnap/stock/index.md) - Advanced stock analysis
- 📈 [Market Mood Index](./tickersnap/mmi/index.md) - Market sentiment tracking
- 📖 [Full Documentation](./index.md) - Complete guides and examples

**Happy Coding & Happy Analyzing!** ✨
