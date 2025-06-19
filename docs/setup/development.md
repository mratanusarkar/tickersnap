# Development

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/mratanusarkar/tickersnap.git
cd tickersnap
```

### 2. Installing `uv`

!!! note "Note"

    If you are using conda base environment as the default base environment for your python projects,
    run the below command to activate the base environment.
    
    If not, skip this step and continue with the next step.

    ```bash
    conda activate base
    ```

If you don't have `uv` installed, you can install it by running:

=== "Linux"

    ```bash
    pip install uv
    ```

=== "Windows"

    ```bash
    pip install uv
    ```

### 3. Setting up the project environment

!!! note "Note"

    Incase you want to do a fresh install, and setup project from scratch using `pyproject.toml`,
    skip this step (3) and continue with the next step (4).

We recommend using `uv` to manage your project environment since `tickersnap` was developed using `uv`,
and you can replicate the same environment from `uv.lock` file by just running:

```bash
uv sync
```

But, feel free to use any python based environment and package manager of your choice.

!!! tip "About uv"

    [uv](https://docs.astral.sh/uv/) is a fast, simple, and secure Python package manager.
    It is recommended to use `uv` to manage your project environment.

### 4. Install dependencies

If you want to do a fresh install with dev and docs dependencies, you can run:

=== "Linux"

    Setup project environment (only if not already done):

    ```bash
    uv venv
    source .venv/bin/activate
    ```

    Install dependencies:

    ```bash
    uv pip install -e ".[dev,docs]"
    ```

=== "Windows"

    Setup project environment:

    ```bash
    uv venv
    .venv\Scripts\activate
    ```

    Install dependencies:

    ```bash
    uv pip install -e ".[dev,docs]"
    ```

## Code Quality

Before committing, please ensure that the code is formatted and styled correctly.
Run the following commands to check and fix code style issues:

```bash
# Check and fix code style issues
black .
ruff check --fix .
```

## Build and serve the documentation

You can build and serve the documentation by running:

```bash
uv pip install -e .[docs]
mkdocs serve
```