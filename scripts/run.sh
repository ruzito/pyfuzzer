#!/bin/bash

export PYTHONPATH=`pwd`/src
# ./.poetry/bin/poetry run python src/pyterm.py $@
./.poetry/bin/poetry run python src/main.py $@