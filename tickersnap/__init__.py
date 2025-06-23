"""
Tickersnap - Stock data snapshots from Tickertape IN

A Python library for accessing Indian stock market data including:

- Market Mood Index (MMI) data
- List of all stocks and ETFs
- Stock scorecard analysis data
"""

__version__ = "0.0.4"

# import submodules for easy access without unpacking classes
from . import lists, mmi, stock

__all__ = [
    "__version__",
    "mmi",
    "lists",
    "stock",
]
