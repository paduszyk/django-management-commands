#!/bin/bash

set -e

. ~/.bashrc

npm ci

pyenv virtualenv venv && pyenv activate venv

pip install -e ".[dev]"

pre-commit install --install-hooks
