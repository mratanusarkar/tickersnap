<div align='center'>

# Tickersnap

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Tests](https://github.com/mratanusarkar/tickersnap/actions/workflows/tests.yml/badge.svg)](https://github.com/mratanusarkar/tickersnap/actions)

**Python Library for Indian Stock Market Analysis** 📈

|
[Documentation](https://mratanusarkar.github.io/tickersnap/) |
[Features](#-key-features) |
[Quick Start](#-quick-start)
|

</div>

Tickersnap provides streamlined access to comprehensive Indian stock market data from [www.tickertape.in](https://www.tickertape.in), enabling powerful financial analysis, automated screening, and market sentiment tracking.

> [!IMPORTANT]
> - This library heavily relies on the (unofficial) public APIs from Tickertape IN.
> - I am not affiliated with Tickertape.in in any way.
> - Tickertape had been my go to for stock analysis tool for like forever!
> - and I am greatful to them for the work they do!

> [!WARNING]
> - All data are for **informational purposes only** and should not be considered as financial advice.
> - Always consult qualified financial advisors before making investment decisions.
> - I am not an expert in finance.
> - I am not responsible for how one uses this library, the consequences, or financial outcomes of using it.

## ✨ Key Features

- **📊 Complete Market Coverage** - Access 5,000+ stocks and 270+ ETFs from Indian exchanges
- **🎯 Stock Scorecard Analysis** - 6-category evaluation (Performance, Valuation, Growth, Profitability, Entry Point, Red Flags)
- **📈 Market Mood Index (MMI)** - Real-time sentiment tracking with Fear/Greed zones
- **⚡ High Performance** - Concurrent processing with progress tracking for large datasets
- **🛡️ Robust & Reliable** - Comprehensive error handling and extensive test coverage
- **🔧 Developer Friendly** - Clean APIs with intuitive method names and comprehensive documentation

## 🛠️ Requirements

- Python 3.10+

## 🚀 Quick Start

### Installation

```bash
pip install tickersnap
```

### Basic Usage

```python
from tickersnap.mmi import MarketMoodIndex
from tickersnap.stock import StockScorecard
from tickersnap.lists import Assets

# Check market sentiment
mmi = MarketMoodIndex()
mood = mmi.get_current_mmi()
print(f"Market Mood: {mood.value:.1f} ({mood.zone.value})")

# Analyze a stock
scorecard = StockScorecard()
analysis = scorecard.get_scorecard("TCS")
if analysis.performance:
    print(f"TCS Performance: {analysis.performance.rating.value}")

# Get all stocks
assets = Assets()
all_stocks = assets.get_all_stocks()
print(f"Total stocks available: {len(all_stocks)}")
```

**👉 [Complete Quick Start Guide](https://mratanusarkar.github.io/tickersnap/quickstart.md)** - Learn with real examples!

## 📦 Core Modules

| Module | Description | Use Case |
|--------|-------------|----------|
| **📋 Assets** | Complete list of stocks & ETFs | Portfolio building, universe selection |
| **📊 Stock Scorecard** | 6-category stock analysis | Investment screening, due diligence |
| **📈 Market Mood Index** | Sentiment tracking (0-100 scale) | Market timing, contrarian investing |

**👉 see documentation for more details!** | [MMI](https://mratanusarkar.github.io/tickersnap/tickersnap/mmi/) | [Assets](https://mratanusarkar.github.io/tickersnap/tickersnap/lists/) | [Stocks](https://mratanusarkar.github.io/tickersnap/tickersnap/stock/) |

## 💡 What You Can Build

- **📊 Stock Screeners** - Find quality stocks automatically
- **📈 Portfolio Trackers** - Monitor your investments daily  
- **🎯 Market Alerts** - Get notified of sentiment extremes
- **🔍 Research Tools** - Comprehensive market analysis
- **🤖 Trading Bots** - Automated analysis and signals
- **🧠 LLM Agents** - Build agents to get live financial data

**👉 see documentation, every module is filled with usage examples!**

## 📄 License

Licensed under the [Apache License 2.0](LICENSE)

## 🤝 Contributing

Contributions are welcome!

(_contribution guidelines are coming soon._)

---

<div align='center'>

**Made with ❤️ for Fin Lovers in India**

</div>
