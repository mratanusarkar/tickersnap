# Models

## Details and Summary

- Tickertape Models: Pydantic models to hold and map the Tickertape API response for stock scorecard data, acting as a schema for the response.
- Tickersnap Models: Pydantic models to hold `Tickersnap` defined models, to work easily with the library data.

=== "Tickertape Models (API Response)"

    ### Stock Scorecard

    - Main model: `ScorecardResponse`
    - Depends on: `ScorecardItem`, `ScoreData`, `ScorecardElement`
        - `ScorecardItem`: holds individual scorecard category data
        - `ScoreData`: holds score information for financial categories
        - `ScorecardElement`: holds element data for entry point and red flags

=== "Tickersnap Models (Library Datatypes)"

    ### Stock Scores (User-Friendly)

    - Main model: `StockScores`
    - Depends on: `Score`, `ScoreRating`
        - `Score`: simplified scorecard data point with rating
        - `ScoreRating`: unified good/bad/okay/unknown classification

## Usage

| Model | Source API / Used By | Description | Usage | For Public? |
|-------|------------|-------------|-------|------------|
| `ScorecardResponse` | (GET) analyze [/stocks/scorecard/{sid}](https://analyze.api.tickertape.in/stocks/scorecard/{sid}) | Complete stock scorecard data | get 6 scorecard categories for any stock | ✅ |
| `ScorecardItem` | `ScorecardResponse` | holds individual category data | (internal use) | ❌ |
| `ScoreData` | `ScorecardItem` | holds score information | (internal use) | ❌ |
| `ScorecardElement` | `ScorecardItem` | holds element data | (internal use) | ❌ |
| `StockScores` | `StockScorecard` | simplified user-friendly scores | simplified stock analysis | ✅ |
| `Score` | `StockScores` | individual score with rating | (internal use) | ❌ |
| `ScoreRating` | `Score` | good/bad classification | (internal use) | ❌ |

## Scorecard Categories

The stock scorecard contains **6 main categories** that evaluate different aspects of a stock:

### Core Financial Categories (Score-based)

- **Performance**: Stock price performance vs market
- **Valuation**: Stock valuation vs market average  
- **Growth**: Company growth prospects and trends
- **Profitability**: Company profitability and efficiency

### Trading Categories (Element-based)

- **Entry Point**: Current entry timing assessment with detailed factors
- **Red Flags**: Risk assessment with detailed warning indicators

## Score Ratings

| Rating | Description | Color Signal | Investment Implication |
|--------|-------------|--------------|----------------------|
| **GOOD** | Positive indicator | 🟢 Green | Favorable conditions |
| **OKAY** | Neutral indicator | 🟡 Yellow/Orange | Average conditions |
| **BAD** | Negative indicator | 🔴 Red | Unfavorable conditions |
| **UNKNOWN** | Missing/insufficient data | ⚪ Gray | Unable to determine |

## Field Reference

Below is a comprehensive reference for all the fields found in the stock scorecard API models, grouped by logical sections:

??? info "Model Fields Reference"

    ### 1. Response Structure:

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `success` | Success Status | `bool` | true/false | API response success indicator |
    | `data` | Data Payload | `List[ScorecardItem]` | array | List of scorecard category objects (up to 6 items) |

    ### 2. Scorecard Item Fields:

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `name` | Category Name | `str` | text | Scorecard category name (Performance, Valuation, etc.) |
    | `tag` | Category Tag | `str` | High/Low/Good/Bad/Avg | Category assessment tag |
    | `type` | Category Type | `str` | score/entryPoint/redFlag | Type of scorecard category |
    | `description` | Description | `str` | text | Human-readable explanation of the assessment |
    | `colour` | Color Signal | `str` | red/green/yellow | Color indicator for quick visual assessment |
    | `locked` | Locked Status | `bool` | true/false | Whether category data is premium/locked |
    | `stack` | Stack Order | `int` | 1-6 | Display order of categories (1=Performance, 6=Red Flags) |
    | `elements` | Elements List | `List[ScorecardElement]` | array | Detailed factors (for Entry Point and Red Flags only) |

    ### 3. Score Data Fields (Financial Categories):

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `percentage` | Percentage Flag | `bool` | true/false | Whether score value is a percentage |
    | `max` | Maximum Score | `int` | positive | Maximum possible score value |
    | `value` | Score Value | `float` | varies | Actual score value (can be null) |
    | `key` | Score Key | `str` | text | Score identifier matching category name |

    ### 4. Element Fields (Entry Point & Red Flags):

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `title` | Element Title | `str` | text | Name of the specific factor (e.g., "Fundamentals", "ASM") |
    | `type` | Element Type | `str` | flag | Type of element (typically "flag") |
    | `description` | Element Description | `str` | text | Detailed explanation of the factor |
    | `flag` | Flag Value | `str` | High/Low/Medium | Assessment level for this factor |
    | `display` | Display Flag | `bool` | true/false | Whether this element should be shown to users |
    | `score` | Element Score | `Any` | varies | Score value for this element (typically null) |
    | `source` | Data Source | `str` | text | Source of the data (typically null) |

    ### 5. User-Friendly Models (StockScores):

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `performance` | Performance Score | `Score` | object | Overall stock performance assessment |
    | `valuation` | Valuation Score | `Score` | object | Stock valuation assessment |
    | `growth` | Growth Score | `Score` | object | Company growth prospects |
    | `profitability` | Profitability Score | `Score` | object | Company profitability assessment |
    | `entry_point` | Entry Point Score | `Score` | object | Current entry timing assessment |
    | `entry_point_elements` | Entry Point Details | `List[Score]` | array | Detailed entry point factors |
    | `red_flags` | Red Flags Score | `Score` | object | Overall red flags assessment |
    | `red_flags_elements` | Red Flag Details | `List[Score]` | array | Detailed red flag factors |

    ### 6. Individual Score Fields:

    | Field | Full Form | Type | Range/Format | Description |
    |-------|-----------|------|-------------|-------------|
    | `name` | Score Name | `str` | text | Display name of the scorecard item |
    | `description` | Score Description | `str` | text | Human-readable explanation |
    | `value` | Score Value | `str` | text | The actual tag/value from API (e.g., "High", "Low") |
    | `rating` | Score Rating | `ScoreRating` | enum | Simplified good/bad/okay/unknown classification |

## Category Details

### Financial Categories (Score-based)

These categories use quantitative scoring and provide overall assessments:

- **Performance**: Tracks stock price performance relative to market indices
- **Valuation**: Compares stock valuation metrics to market averages
- **Growth**: Evaluates company growth metrics and future prospects  
- **Profitability**: Assesses company profitability ratios and efficiency

**Characteristics:**

- Have `score` data with numerical values
- Empty `elements` array
- Tags: typically "High", "Low", "Good", "Bad"
- Colors: red (bad), green (good), yellow (neutral)

### Trading Categories (Element-based)

These categories provide detailed breakdowns with multiple factors:

- **Entry Point**: Analyzes current entry timing with factors like:

    - Fundamentals (intrinsic value vs current price)
    - Technicals (overbought/oversold conditions)
  
- **Red Flags**: Identifies potential risks with factors like:

    - ASM (Additional Surveillance Measure) status
    - GSM (Graded Surveillance Measure) status  
    - Promoter pledged holdings
    - Unsolicited messages
    - Default probability

**Characteristics:**

- No `score` data (score is null)
- Populated `elements` array with detailed factors
- Tags: "Good", "Bad", "Avg" for overall assessment
- Individual elements have their own flag values

## Edge Cases

### Stocks with Missing Categories

Some stocks (particularly smaller companies) may not have all 6 categories:

- **Common scenario**: Only Entry Point and Red Flags available
- **Missing categories**: Performance, Valuation, Growth, Profitability
- **Reason**: Insufficient financial data for comprehensive analysis
- **Examples**: INDL, ELLE, ATE, OSWAP (as of testing)

### Failed Responses

- **success**: false
- **data**: null
- **Reason**: Invalid SID or stock not found

::: tickersnap.stock.models
