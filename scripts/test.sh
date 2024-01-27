#!/bin/bash

export PYTHONPATH=`pwd`/src:`pwd`/tests
./.poetry/bin/poetry run pytest -v tests/ -m 'not hypothesis' "$@"