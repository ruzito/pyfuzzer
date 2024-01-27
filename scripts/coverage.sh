#!/bin/bash

export PYTHONPATH=`pwd`/src:`pwd`/tests
# pytest --cov=src tests/
./.poetry/bin/poetry run coverage run -m pytest tests/ --hypothesis-profile cover
./.poetry/bin/poetry run coverage html --omit="tests/*" > /dev/null
./.poetry/bin/poetry run coverage xml > /dev/null
./.poetry/bin/poetry run coverage json > /dev/null
./.poetry/bin/poetry run coverage report --omit="tests/*"