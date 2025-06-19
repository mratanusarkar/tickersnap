# Tickersnap

Tickersnap is a tool for getting snapshots of stock data from www.tickertape.in

## Installation

Clone the repo

```bash
git clone https://github.com/mratanusarkar/tickersnap
cd tickersnap
```

Ensure you have `uv` installed

```bash
pip install -U pip uv
```

Create and activate virtual environment

```bash
uv venv
source .venv/bin/activate
```

Install dependencies

```bash
uv pip install -e .[dev,docs]
```

## Development

For development, you can install the dependencies in `.venv` by running

```bash
uv sync
```

You can build and serve the documentation by running

```bash
uv pip install -e .[docs]
mkdocs serve
```
