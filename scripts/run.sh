#!/bin/bash

export PYTHONPATH=`pwd`/src
# export PYTHONASYNCIODEBUG=1
# ./.poetry/bin/poetry run python src/pyterm.py $@
./.poetry/bin/poetry run python src/main.py "$@"