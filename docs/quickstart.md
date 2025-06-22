# Quick Start Guide

Welcome to **Tickersnap** - your gateway to Indian stock market analysis! 🚀

This guide will get you up and running in minutes, whether you're a complete beginner or an experienced developer.

## 📋 What You'll Learn

- [Installation](#installation) - Get tickersnap running on your system
- [Basic Concepts](#basic-concepts) - Understand the three core modules
- [Your First Script](#your-first-script) - Write your first market analysis
- [Common Use Cases](#common-use-cases) - Real-world examples
- [Next Steps](#next-steps) - Where to go from here

---

## 🔧 Installation

### Prerequisites

- **Python 3.10+** (check with `python --version`)
- **Internet connection** (for fetching live market data)

### Install Tickersnap

```bash
pip install tickersnap
```

That's it! No API keys, no registration, no complex setup. 

### Verify Installation

```python
import tickersnap
print("✅ Tickersnap installed successfully!")
```

---

## 🧠 Basic Concepts

Tickersnap has **3 core modules** that work together:

| Module | What it does | Example |
|--------|--------------|---------|
| **📋 Assets** | Lists all stocks & ETFs | Get all 5,000+ Indian stocks |
| **📊 Scorecard** | Analyzes individual stocks | TCS performance: Good/Bad? |
| **📈 MMI** | Tracks market sentiment | Market fear or greed today? |

### The Power of Combination

- Use **Assets** to find stocks → **Scorecard** to analyze them → **MMI** for market timing
- Perfect for screening, research, and automated analysis

---

## 🚀 Your First Script

Let's write a simple script that checks market sentiment and analyzes a popular stock:

```python
from tickersnap.mmi import MarketMoodIndex
from tickersnap.stock import StockScorecard

# 1. Check market sentiment
print("📈 Checking market mood...")
mmi = MarketMoodIndex()
current_mood = mmi.get_current_mmi()

print(f"Market Mood Index: {current_mood.value:.1f}")
print(f"Zone: {current_mood.zone}")

if current_mood.zone == "Extreme Fear":
    print("💡 Market is fearful - might be a good buying opportunity!")
elif current_mood.zone == "Extreme Greed":
    print("⚠️ Market is greedy - be cautious with new positions!")

# 2. Analyze a popular stock
print("\n📊 Analyzing TCS stock...")
scorecard = StockScorecard()
tcs_analysis = scorecard.get_scorecard("TCS")

print(f"Performance: {tcs_analysis.performance.value} ({tcs_analysis.performance.rating})")
print(f"Valuation: {tcs_analysis.valuation.value} ({tcs_analysis.valuation.rating})")
print(f"Entry Point: {tcs_analysis.entry_point.value} ({tcs_analysis.entry_point.rating})")

print("\n✅ Analysis complete!")
```

**Run this script** and you'll see live market data and stock analysis!

---

## 💡 Common Use Cases

### 1. **Daily Market Check** (2 minutes)

Perfect for your morning routine:

```python
from tickersnap.mmi import MarketMoodIndex

# Quick market pulse
mmi = MarketMoodIndex()
current = mmi.get_current_mmi()
changes = mmi.get_mmi_changes()

print(f"📊 Today's Market Mood: {current.value:.1f} ({current.zone})")
print(f"📈 vs Yesterday: {changes.vs_last_day:+.1f}")
print(f"📅 vs Last Week: {changes.vs_last_week:+.1f}")

# Investment signal
if current.zone in ["Extreme Fear", "Fear"]:
    print("🟢 Consider buying opportunities")
elif current.zone in ["Extreme Greed", "Greed"]:
    print("🔴 Be cautious, market may be overheated")
```

### 2. **Stock Screening** (5 minutes)

Find quality stocks automatically:

```python
from tickersnap.lists import Assets
from tickersnap.stock import StockScorecard

# Get popular stocks
assets = Assets()
scorecard = StockScorecard()

# Analyze top stocks
popular_stocks = ["TCS", "RELI", "INFY", "HDFC", "ICICIBANK"]
results = scorecard.get_scorecards(popular_stocks)

print("🔍 Quality Stock Analysis:")
for i, result in enumerate(results):
    if result:
        stock = popular_stocks[i]
        
        # Count good categories
        good_count = sum(1 for cat in [
            result.performance, result.valuation, 
            result.growth, result.profitability
        ] if cat and cat.rating.name == "GOOD")
        
        print(f"{stock}: {good_count}/4 good categories")
        
        if good_count >= 3:
            print(f"  ⭐ High quality stock!")
```

### 3. **Portfolio Health Check** (10 minutes)

Monitor your existing holdings:

```python
from tickersnap.stock import StockScorecard

# Your portfolio (replace with your actual holdings)
my_portfolio = ["TCS", "RELI", "INFY", "HDFC"]

scorecard = StockScorecard()
results = scorecard.get_scorecards(my_portfolio, progress=True)

print("📊 Portfolio Health Report:")
for i, result in enumerate(results):
    if result:
        stock = my_portfolio[i]
        print(f"\n📈 {stock}:")
        
        # Key metrics
        if result.performance:
            print(f"  Performance: {result.performance.rating}")
        if result.entry_point:
            print(f"  Entry Point: {result.entry_point.rating}")
        if result.red_flags:
            print(f"  Red Flags: {result.red_flags.rating}")
            
        # Alert for red flags
        if result.red_flags and result.red_flags.rating.name == "BAD":
            print(f"  ⚠️ WARNING: {stock} has red flags!")
```

### 4. **Market Opportunity Finder** (15 minutes)

Find stocks with good entry points:

```python
from tickersnap.lists import Assets
from tickersnap.stock import StockScorecard

# Get all stocks and find opportunities
assets = Assets()
scorecard = StockScorecard(max_workers=20)

# Sample analysis (use all_stocks for complete analysis)
all_stocks = assets.get_all_stocks()
sample_stocks = all_stocks[:50]  # First 50 for demo

print(f"🔍 Analyzing {len(sample_stocks)} stocks for opportunities...")
results = scorecard.get_stocks_with_scorecards(sample_stocks, progress=True)

# Find good entry points
opportunities = []
for result in results:
    if (result.scorecard and 
        result.scorecard.entry_point and 
        result.scorecard.entry_point.rating.name == "GOOD"):
        
        opportunities.append({
            "name": result.asset.name,
            "ticker": result.asset.ticker
        })

print(f"\n🎯 Found {len(opportunities)} stocks with good entry points:")
for stock in opportunities[:10]:  # Show top 10
    print(f"  • {stock['ticker']}: {stock['name']}")
```

---

## 🎯 Understanding the Output

### Market Mood Index (MMI)
- **0-30**: Extreme Fear (🟢 Good buying opportunity)
- **30-50**: Fear (⚪ Monitor trends)
- **50-70**: Greed (🟡 Be selective)
- **70-100**: Extreme Greed (🔴 Avoid new positions)

### Stock Ratings
- **GOOD**: 🟢 Positive signal
- **OKAY**: 🟡 Neutral/Average
- **BAD**: 🔴 Negative signal
- **UNKNOWN**: ⚪ Insufficient data

### Stock Categories
- **Performance**: Recent price performance
- **Valuation**: How expensive/cheap the stock is
- **Growth**: Company's growth prospects
- **Profitability**: Company's profit efficiency
- **Entry Point**: Current timing for buying
- **Red Flags**: Risk warnings

---

## 🚨 Common Gotchas

### 1. **Internet Connection Required**
```python
# This will fail without internet
mmi = MarketMoodIndex()
# ❌ Exception: Request failed: Connection timeout
```

### 2. **Invalid Stock Codes**
```python
# Use correct SIDs (not NSE symbols)
scorecard.get_scorecard("TCS")     # ✅ Correct
scorecard.get_scorecard("TCS.NS")  # ❌ Wrong format
```

### 3. **Rate Limiting for Large Batches**
```python
# For 100+ stocks, use reasonable workers
scorecard = StockScorecard(max_workers=10)  # ✅ Good
scorecard = StockScorecard(max_workers=50)  # ❌ Too aggressive
```

---

## 🎓 Next Steps

### Learn More
- **📖 [Full Documentation](https://mratanusarkar.github.io/tickersnap/)** - Complete guides and API reference
- **📋 [Assets Module](https://mratanusarkar.github.io/tickersnap/lists/)** - Working with stock lists
- **📊 [Stock Scorecard](https://mratanusarkar.github.io/tickersnap/stock/)** - Advanced stock analysis
- **📈 [Market Mood Index](https://mratanusarkar.github.io/tickersnap/mmi/)** - Market sentiment tracking

### Build Something Cool
- **Portfolio Tracker**: Monitor your investments daily
- **Stock Screener**: Find stocks matching your criteria
- **Market Alert System**: Get notified of market extremes
- **Research Dashboard**: Combine all modules for comprehensive analysis

### Get Help
- **📖 Documentation**: Most questions answered in the docs
- **🐛 Issues**: Report bugs on GitHub
- **💡 Ideas**: Suggest features or improvements

---

## 🎉 You're Ready!

You now have everything you need to start analyzing the Indian stock market with Tickersnap!

**Remember:**
- Start simple with the examples above
- Experiment with different stocks and criteria
- Use the detailed documentation when you need more advanced features
- This is for educational/informational purposes - not financial advice

**Happy analyzing!** 📈✨
