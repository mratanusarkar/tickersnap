# Stock Scorecard

**Tickersnap** (this python package) provides comprehensive access to stock scorecard data from Tickertape's analysis engine.

## Overview

The Stock Scorecard module evaluates stocks across **6 key categories**:

- Performance
- Valuation
- Growth
- Profitability
- Entry Point
- Red Flags

Get instant insights into any stock's financial health and trading conditions.

!!! note "Note"
    This module sources data from Tickertape's analyze API,
    providing professional-grade stock evaluation metrics and
    from professional analysts for 5000+ Indian stocks.

## Disclaimers

!!! warning "Disclaimer"

    - Scorecard data is for informational and analysis purposes only.
    - None of the data provided via this module is my own, but from Tickertape's analyze API.
    - Some stocks may have limited scorecard categories (especially smaller companies and new listings).
    - The `sid` fields can be used to interact with Tickertape APIs.
    - **Combine with Assets List module for powerful automated stock screening!**

!!! danger "Disclaimer"

    The stock scorecard data provided through this module is for informational purposes only.
    Not financial advice. Always consult qualified financial advisors before making investment decisions.

## Modules

| Module | Description | Target Audience | For Public Use | When to use? |
|--------|-------------|-----------------|----------------|----------------|
| [Scorecard](scorecard.md) | High-level scorecard analysis | General Users | ✅ | When you want simplified stock analysis and screening |
| [API](api.md) | Raw API access | Advanced Users | ✅ | When you need direct access to Tickertape's scorecard API |
| [Models](models.md) | Data models | Internal Use | ❌ | NA |
