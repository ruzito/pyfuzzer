#!/bin/bash

export PYTHONPATH=`pwd`/src
# ./.poetry/bin/poetry run python src/pyterm.py $@
./.poetry/bin/poetry run py-spy record -o profile.svg -- python src/main.py $@