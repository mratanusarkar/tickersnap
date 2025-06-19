# Market Mood Index (MMI)

!!! quote "Quote"
    "_Be fearful when others are greedy and greedy when others are fearful_"
    
    — Warren Buffett

## What is MMI?

The **Market Mood Index (MMI)** is Tickertape's proprietary sentiment indicator that measures investor emotions in the Indian stock market.
It tracks market sentiment on a **scale of 0-100**, categorizing market mood into four distinct zones based on fear and greed psychology.

## Understanding the Four Zones

| Zone | Range | Description | Investment Signal |
|------|-------|-------------|-------------------|
| **Extreme Fear** | < 30 | Market oversold, widespread selling | **Good time to buy** |
| **Fear** | 30-50 | Cautious sentiment, trajectory dependent | Monitor trend direction |
| **Greed** | 50-70 | Optimistic market, overbought territory | **Consider selling** |
| **Extreme Greed** | > 70 | Market euphoria, avoid fresh positions | Wait for correction |

## Bull vs Bear: The Sentiment Connection

MMI's Fear/Greed zones directly correspond to traditional **Bull and Bear market sentiment**.
When MMI shows Fear zones, it reflects bearish sentiment (investors expecting market decline),
while Greed zones indicate bullish sentiment (optimism about market rises).

Like other sentiment indicators, MMI serves as a contrarian indicator - extreme readings often signal potential market reversals.

!!! quote "Quote"
    "_high greed may indicate that markets are overbought, and prices may correct soon_"

    — [Kotak Securities](https://www.kotaksecurities.com/investing-guide/articles/market-mood-index-guide/)

## How MMI Works

MMI is built using **6 fundamental factors**, each providing unique insights into market psychology:

- **FII Activity** - Foreign institutional investor sentiment
- **Volatility & Skew** - Market risk and direction expectations  
- **Momentum** - Price trend strength using moving averages
- **Market Breadth** - Stocks advancing vs declining ratio
- **Price Strength** - 52-week highs vs lows comparison
- **Gold Demand** - Safe haven vs equity preference

## Key Features

All thanks to [www.tickertape.in](https://www.tickertape.in) for this amazing tool/indicator MMI. From what I could gather, here are it's core features:

✅ **91.28% Accuracy** - Proven track record in predicting market tops and bottoms  
✅ **Real-time Updates** - Live sentiment tracking  
✅ **Contrarian Indicator** - Based on Warren Buffett's principle

!!! warning "Disclaimer"
    MMI is a sentiment tool for informational purposes only. Not financial advice.
    Always consult qualified financial advisors before making investment decisions.

### References

If you are curious and wish to explore more, here are some interesting references and articles:

- [Market Sentiment - Wikipedia](https://en.wikipedia.org/wiki/Market_sentiment)
- [Tickertape MMI](https://www.tickertape.in/market-mood-index)
- [How MMI Helps Time Investments](https://www.tickertape.in/blog/how-mmi-can-help-in-timing-your-investments-better/)
- [Market Trend - Wikipedia](https://en.wikipedia.org/wiki/Market_trend)
- [Bull Market](https://www.tickertape.in/blog/bull-market/)
- [Bear Market](https://www.tickertape.in/blog/don-fear-a-bear-market/)

---

## About Tickersnap

**Tickersnap** (this python package) provides unofficial Python API access to Tickertape's Market Mood Index and other financial data.
Since Tickertape doesn't offer official APIs, Tickersnap bridges this gap for developers and analysts.

Along with the official API, this python package also provides a streamlined way to fetch, process, and work with MMI data,
as well as providing a utility-focused classes and functions to work with MMI data.

Here are the offerings of this python package:

| Module | Description | Target Audience | For Public Use |
|--------|-------------|-----------------|----------------|
| [MMI](mmi.md) | Market Mood Index | General Users, Common Users | ✅ |
| [API](api.md) | Raw API access | Advanced Users, Want to use Tickertape API | 🟡 |
| [Models](models.md) | Data models | NA | ❌ |
