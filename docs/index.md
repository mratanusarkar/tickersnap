<h1 align="center"><strong>Tickersnap</strong></h1>

<p align="center">

<a href="https://mratanusarkar.github.io/tickersnap">
  <img
  src="https://img.shields.io/badge/docs-mkdocs-4baaaa.svg?logo=materialformkdocs&logoColor=white"
  alt="Documentation">
</a>
<a href="https://pypi.org/project/tickersnap/">
  <img
  src="https://img.shields.io/pypi/v/tickersnap.svg?color=blue&logo=pypi&logoColor=white"
  alt="PyPI version">
</a>
<a href="https://pypi.org/project/tickersnap/">
  <img src="https://img.shields.io/pypi/pyversions/tickersnap.svg?color=blue&logo=python&logoColor=white"
  alt="Python versions">
</a>
<a href="https://github.com/mratanusarkar/tickersnap/blob/main/LICENSE">
  <img src="https://img.shields.io/badge/License-Apache%202.0-orange.svg?logo=apache&logoColor=white"
  alt="License: Apache 2.0">
</a>

<br>

<a href="https://github.com/mratanusarkar/tickersnap/actions">
  <img
  src="https://img.shields.io/github/actions/workflow/status/mratanusarkar/tickersnap/docs.yml?logo=githubactions&logoColor=white&label=build"
  alt="GitHub Actions Workflow Status">
</a>
<a href="https://github.com/mratanusarkar/tickersnap/actions">
  <img src="https://img.shields.io/github/actions/workflow/status/mratanusarkar/tickersnap/tests.yml?logo=cachet&logoColor=white&label=tests"
  alt="Tests">
</a>
<a href="https://visitorbadge.io/status?path=https%3A%2F%2Fgithub.com%2Fmratanusarkar%2Ftickersnap">
  <img src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgithub.com%2Fmratanusarkar%2Ftickersnap&label=view&labelColor=%235e5e5e&countColor=%237C8AA0&style=flat&labelStyle=lower"
  alt="Visitors">
</a>

<a href="https://pepy.tech/projects/tickersnap">
  <img src="https://static.pepy.tech/badge/tickersnap"
  alt="PyPI Total Downloads">
</a>

<a href="https://pypistats.org/packages/tickersnap">
  <img src="https://img.shields.io/pypi/dm/tickersnap?style=flat&color=%231F86BF"
  alt="PyPI Monthly Downloads">
</a>

</p>

<p align="center">

<b>Python Library for Indian Stock Market Analysis</b> 📈

<br><br>

<i style="color: #888888">Streamlined access to comprehensive Indian stock market data from <a href="https://www.tickertape.in">Tickertape IN</a>, enabling powerful financial analysis, automated screening, and market sentiment tracking.</i>

</p>

!!! important "Important Notice"
    - This library heavily relies on the (unofficial) public APIs from Tickertape IN.
    - I am not affiliated with Tickertape.in in any way.
    - Tickertape had been my go to for stock analysis tool for like forever!
    - and I am greatful to them for the work they do!

!!! warning "Disclaimer"
    - All data are for **informational purposes only** and should not be considered as financial advice.
    - Always consult qualified financial advisors before making investment decisions.
    - I am not an expert in finance.
    - I am not responsible for how one uses this library, the consequences, or financial outcomes of using it.

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

**👉 [Complete Quick Start Guide](./quickstart.md)** - Learn with real examples!

## 📦 Core Modules

| Module | Description | Use Case |
|--------|-------------|----------|
| **📋 Assets** | Complete list of stocks & ETFs | Portfolio building, universe selection |
| **📊 Stock Scorecard** | 6-category stock analysis | Investment screening, due diligence |
| **📈 Market Mood Index** | Sentiment tracking (0-100 scale) | Market timing, contrarian investing |

**👉 See detailed documentation:** | [MMI](./tickersnap/mmi/index.md) | [Assets](./tickersnap/lists/index.md) | [Stocks](./tickersnap/stock/index.md) |

## 💡 What You Can Build

- **📊 Stock Screeners** - Find quality stocks automatically
- **📈 Portfolio Trackers** - Monitor your investments daily  
- **🎯 Market Alerts** - Get notified of sentiment extremes
- **🔍 Research Tools** - Comprehensive market analysis
- **🤖 Trading Bots** - Automated analysis and signals
- **🧠 LLM Agents** - Build agents to get live financial data

**👉 Every module is filled with usage examples throughout the documentation!**

## 📚 Quick Links

- **[Quick Start Guide](./quickstart.md)** - Get started in minutes
- **[Installation Guide](./setup/installation.md)** - Detailed setup instructions
- **[Development Guide](./setup/development.md)** - Contributing and development setup
- **Module Documentation:**
    - **[Market Mood Index (MMI)](./tickersnap/mmi/index.md)** - Market sentiment tracking
    - **[Assets Lists](./tickersnap/lists/index.md)** - Stock and ETF data access
    - **[Stock Scorecard](./tickersnap/stock/index.md)** - Comprehensive stock analysis

## 📄 License

Licensed under the [Apache License 2.0](https://github.com/mratanusarkar/tickersnap/blob/main/LICENSE)

## 🤝 Contributing

Contributions are welcome!

(_contribution guidelines are coming soon._)

---

**Made with ❤️ for Fin Lovers in India**
