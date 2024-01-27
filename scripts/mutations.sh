#!/bin/bash

export PYTHONPATH=`pwd`/src:`pwd`/tests
./.poetry/bin/poetry run mutmut run --runner="scripts/lint.sh && pytest tests/ --hypothesis-profile cover" --paths-to-mutate=./src