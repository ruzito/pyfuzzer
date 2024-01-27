#!/bin/bash

export PYTHONPATH=`pwd`/src:`pwd`/tests
./.poetry/bin/poetry run pytest -v tests/ --hypothesis-profile explain