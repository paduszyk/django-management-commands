#!/bin/bash

set -e

. ~/.bashrc

npm ci

uv sync --locked

uv run pre-commit install --install-hooks
