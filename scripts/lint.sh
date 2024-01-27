#!/bin/bash

export PYTHONPATH=`pwd`/src:`pwd`/tests
./.poetry/bin/poetry run black --exclude '.*/\.poetry/.*' .
./.poetry/bin/poetry run mypy . --exclude ./.poetry
./.poetry/bin/poetry run flake8 .