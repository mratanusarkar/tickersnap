# Tickersnap

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Tests](https://github.com/mratanusarkar/tickersnap/actions/workflows/tests.yml/badge.svg)](https://github.com/mratanusarkar/tickersnap/actions)

**Python Library for Indian Stock Market Analysis** 📈

|
[Documentation](https://mratanusarkar.github.io/tickersnap/) |
[Features](#-key-features)

Tickersnap provides streamlined access to comprehensive Indian stock market data from [www.tickertape.in](https://www.tickertape.in), enabling powerful financial analysis, automated screening, and market sentiment tracking.

> [!IMPORTANT]
> - This library heavily relies on the (unofficial) public APIs from Tickertape IN.
> - I am not affiliated with Tickertape.in in any way.
> - Tickertape had been my go to for stock analysis tool for like forever!
> - and I am greatful to then and a big fan of the work they do!

> [!WARNING]
> - All data are for **informational purposes only** and should not be considered as financial advice.
> - Always consult qualified financial advisors before making investment decisions.
> - I am not an expert in finance.
> - I am not responsible for how one uses this library, or the consequences, or financial outcomes of using it.

## ✨ Key Features

- **📊 Complete Market Coverage** - Access 5,000+ stocks and 270+ ETFs from Indian exchanges
- **🎯 Stock Scorecard Analysis** - 6-category evaluation (Performance, Valuation, Growth, Profitability, Entry Point, Red Flags)
- **📈 Market Mood Index (MMI)** - Real-time sentiment tracking with Fear/Greed zones
- **⚡ High Performance** - Concurrent processing with progress tracking for large datasets
- **🛡️ Robust & Reliable** - Comprehensive error handling and extensive test coverage
- **🔧 Developer Friendly** - Clean APIs with intuitive method names and comprehensive documentation

## 🚀 Quick Start

### Installation

```bash
pip install tickersnap
```

### Basic Usage

```python
from tickersnap.lists import Assets
from tickersnap.stock import StockScorecard
from tickersnap.mmi import MarketMoodIndex

# Get all Indian stocks and ETFs
assets = Assets()
all_stocks = assets.get_all_stocks()
print(f"Total stocks: {len(all_stocks)}")

# Analyze stock scorecards
scorecard = StockScorecard()
tcs_analysis = scorecard.get_scorecard("TCS")
print(f"TCS Performance: {tcs_analysis.performance.rating}")

# Check market sentiment
mmi = MarketMoodIndex()
current_sentiment = mmi.get_current_mmi()
print(f"Market Mood: {current_sentiment.value:.1f} ({current_sentiment.zone})")
```

## 📦 Core Modules

| Module | Description | Use Case |
|--------|-------------|----------|
| **📋 Assets** | Complete list of stocks & ETFs | Portfolio building, universe selection |
| **📊 Stock Scorecard** | 6-category stock analysis | Investment screening, due diligence |
| **📈 Market Mood Index** | Sentiment tracking (0-100 scale) | Market timing, contrarian investing |

## 💡 Powerful Examples

### Stock Screening

```python
from tickersnap.lists import Assets
from tickersnap.stock import StockScorecard

# Screen for quality stocks
assets = Assets()
scorecard = StockScorecard(max_workers=25)

# Get all stocks and their scorecards
all_stocks = assets.get_all_stocks()
results = scorecard.get_stocks_with_scorecards(all_stocks, progress=True)

# Filter for high-quality stocks
quality_stocks = []
for result in results:
    if result.scorecard:
        good_categories = sum(1 for cat in [
            result.scorecard.performance, result.scorecard.valuation,
            result.scorecard.growth, result.scorecard.profitability
        ] if cat and cat.rating.name == "GOOD")
        
        if good_categories >= 3:  # At least 3 good categories
            quality_stocks.append(result.asset.name)

print(f"Found {len(quality_stocks)} high-quality stocks")
```

### Market Sentiment Analysis

```python
from tickersnap.mmi import MarketMoodIndex

mmi = MarketMoodIndex()

# Get current market sentiment
current = mmi.get_current_mmi()
changes = mmi.get_mmi_changes()

print(f"Current MMI: {current.value:.1f} ({current.zone})")
print(f"vs Yesterday: {changes.vs_last_day:+.1f}")
print(f"vs Last Month: {changes.vs_last_month:+.1f}")

# Investment signal
if current.zone == "Extreme Fear":
    print("🟢 Consider buying - Market oversold")
elif current.zone == "Extreme Greed":
    print("🔴 Consider selling - Market overheated")
```

## 📚 Documentation

Comprehensive documentation with examples and API reference:
- **[📖 Full Documentation](https://mratanusarkar.github.io/tickersnap/)**
- **[🚀 Getting Started Guide](https://mratanusarkar.github.io/tickersnap/setup/installation/)**
- **[📋 Assets Module](https://mratanusarkar.github.io/tickersnap/lists/)**
- **[📊 Stock Scorecard](https://mratanusarkar.github.io/tickersnap/stock/)**
- **[📈 Market Mood Index](https://mratanusarkar.github.io/tickersnap/mmi/)**

## 🛠️ Requirements

- Python 3.10+
- Dependencies: `pydantic`, `httpx`, `tqdm`

## 📄 License

Licensed under the [Apache License 2.0](LICENSE)

## 🤝 Contributing

Contributions are welcome!

(_contribution guidelines are coming soon._)

---

**Made with ❤️ for Fin Lovers in India**
