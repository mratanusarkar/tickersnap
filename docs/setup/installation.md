# Installation

!!! note "Note"

    This guide is for end users using `Tickersnap` python package.
    For developers and contributors, see [Development](./development.md).

## Prerequisites

- 🐍 Python ≥ 3.10
- 🖥️ Conda or venv

## Setup

### Install Tickersnap

It is recommended to install `tickersnap` in a virtual environment from PyPI or Conda in a [Python=3.10](https://www.python.org/) (**or above**) environment.

=== "Install using PyPI"

    Activate your virtual environment (recommended):

    ```bash
    source .venv/bin/activate
    ```

    Install `tickersnap` using `pip`:

    ```bash
    pip install tickersnap
    ```

=== "Install using Conda"

    Create a new environment using Conda:

    ```bash
    conda create -n my-project python=3.10
    ```

    Activate your virtual environment:

    ```bash
    conda activate my-project
    ```

    Install `pip` and `tickersnap` using `conda`:

    ```bash
    conda install pip
    pip install tickersnap
    ```

=== "Install from source"

    !!! tip "Note"

        By installing `tickersnap` from source, you can explore the latest features and enhancements that have not yet been officially released.
    
    !!! warning "Note"

        Please note that the latest changes may be still in development and may not be stable and may contain bugs.

    Install from source

    ```bash
    pip install git+https://github.com/mratanusarkar/tickersnap.git
    ```