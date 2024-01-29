#!/bin/bash -e

export PYTHONPATH=`pwd`/src:`pwd`/tests
echo "-- black --"
./.poetry/bin/poetry run black --exclude '.*/\.poetry/.*' .
echo "-- mypy --"
./.poetry/bin/poetry run mypy --show-error-codes . --exclude ./.poetry --exclude src/patch.py
echo "-- flake8 --"
./.poetry/bin/poetry run flake8 .